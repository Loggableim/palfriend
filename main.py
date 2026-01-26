"""
Main application entry point for TikTok ChatPal Brain.
"""

import asyncio
import gc
import json
import logging
import os
import time
from typing import Dict, Any, Set, Optional

import websockets
from TikTokLive import TikTokLiveClient
from TikTokLive.events import (
    ConnectEvent,
    CommentEvent,
    GiftEvent,
    DisconnectEvent,
    FollowEvent,
    LikeEvent,
    SubscribeEvent,
    ShareEvent,
    JoinEvent,
)

from settings import load_settings, save_settings
from memory import MemoryDB
from speech import SpeechState, MicState, MicrophoneMonitor
from utils import trim_text, TokenBucket
from response import Relevance, ResponseEngine
from outbox import OutboxBatcher
from events import EventDeduper, make_signature, touch_viewer, schedule_greeting
from gui import ConfigGUI
from modules.audio import AudioManager
from modules.tts import TTSManager

# Constants
MAX_REPLY_THRESHOLD = 0.8
DEFAULT_REPLY_THRESHOLD = 0.4
ANIMAZE_RECONNECT_DELAY = 0.8

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("ChatPalBrain")

# Global state
animaze_ws = None
message_queue: Optional[asyncio.Queue[str]] = None
comment_queue: Optional[asyncio.Queue[dict]] = None
gift_queue: Optional[asyncio.Queue] = None
like_queue: Optional[asyncio.Queue] = None
join_queue: Optional[asyncio.Queue] = None
follow_queue: Optional[asyncio.Queue] = None
share_queue: Optional[asyncio.Queue] = None
subscribe_queue: Optional[asyncio.Queue] = None

LAST_OUTPUT_TS = 0.0
LAST_JOIN_ANNOUNCE_TS = 0.0
PENDING_JOINS: Set[str] = set()
viewers: Dict[str, Dict] = {}
greet_tasks: Dict[str, asyncio.Task] = {}


async def connect_animaze(cfg: Dict[str, Any], speech: SpeechState) -> None:
    """
    Connect to Animaze WebSocket server.
    
    Args:
        cfg: Configuration dictionary
        speech: SpeechState instance
    """
    global animaze_ws
    
    if animaze_ws is not None:
        return
    
    animaze_uri = f"ws://{cfg['animaze']['host']}:{cfg['animaze']['port']}"
    max_attempts = int(cfg.get("animaze", {}).get("retry_max_attempts", 5))
    base_delay = float(cfg.get("animaze", {}).get("retry_base_delay", 1.0))
    
    for attempt in range(max_attempts):
        try:
            animaze_ws = await websockets.connect(animaze_uri, ping_interval=20, ping_timeout=20)
            log.info("Verbunden mit ChatPal WebSocket")
            asyncio.create_task(handle_animaze_messages(cfg, speech))
            return
        except (websockets.exceptions.WebSocketException, OSError, ConnectionError) as e:
            log.error(f"ChatPal Verbindung fehlgeschlagen (Versuch {attempt + 1}/{max_attempts}): {e}")
            animaze_ws = None
            if attempt < max_attempts - 1:
                delay = base_delay * (2 ** attempt)
                await asyncio.sleep(delay)
        except Exception as e:
            log.error(f"ChatPal Verbindung unerwarteter Fehler: {e}")
            animaze_ws = None
            break


async def handle_animaze_messages(cfg: Dict[str, Any], speech: SpeechState) -> None:
    """
    Handle incoming messages from Animaze WebSocket.
    
    Args:
        cfg: Configuration dictionary
        speech: SpeechState instance
    """
    global animaze_ws
    
    try:
        async for raw in animaze_ws:
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue
            
            act = msg.get("action") or msg.get("event") or ""
            if act == "ChatbotSpeechStarted":
                speech.mark_started()
            elif act == "ChatbotSpeechEnded":
                speech.mark_ended()
            else:
                log.info(f"ChatPal ← {msg}")
    except Exception as e:
        log.warning(f"ChatPal Verbindung beendet: {e}")
    finally:
        animaze_ws = None
        speech.mark_ended()
        await asyncio.sleep(1.5)
        asyncio.create_task(connect_animaze(cfg, speech))


async def send_to_animaze(text: str, cfg: Dict[str, Any]) -> None:
    """
    Queue a message to send to Animaze.
    
    Args:
        text: Message text to send
        cfg: Configuration dictionary
    """
    if not text:
        return
    
    maxlen = int(cfg.get("style", {}).get("max_line_length", 140))
    t = trim_text(text, maxlen)
    log.info(f"→ ChatPal enqueue: {t}")
    await message_queue.put(t)


async def sender_worker(
    cfg: Dict[str, Any], 
    speech: SpeechState,
    tts_manager: Optional[TTSManager] = None,
    audio_manager: Optional[AudioManager] = None
) -> None:
    """
    Worker that sends messages to Animaze or uses local TTS.
    
    Args:
        cfg: Configuration dictionary
        speech: SpeechState instance
        tts_manager: Optional TTSManager for local TTS
        audio_manager: Optional AudioManager for audio playback
    """
    global LAST_OUTPUT_TS, animaze_ws
    
    # Check if TTS is enabled
    tts_enabled = bool(int(cfg.get("tts", {}).get("enabled", 0)))
    use_local_tts = tts_enabled and tts_manager and audio_manager
    
    if use_local_tts:
        log.info("Using local TTS with Fish Audio")
    else:
        log.info("Using Animaze WebSocket for TTS")
    
    while True:
        text = await message_queue.get()
        
        if use_local_tts:
            # Use local TTS and audio playback
            await speech.wait_idle()
            
            try:
                log.info(f"→ TTS Synthesizing: {text}")
                
                # Synthesize audio
                audio_file = await tts_manager.synthesize_to_file(text)
                
                if audio_file:
                    # Mark speech started
                    speech.mark_started()
                    
                    # Play audio
                    await audio_manager.play_file(audio_file)
                    
                    # Mark speech ended
                    speech.mark_ended()
                    
                    # Post-speech gap
                    pg = int(cfg.get("speech", {}).get("post_gap_ms", 250)) / 1000.0
                    await asyncio.sleep(pg)
                    
                    LAST_OUTPUT_TS = time.time()
                    log.info(f"✓ TTS playback completed")
                else:
                    log.error("TTS synthesis failed, skipping message")
            except Exception as e:
                log.error(f"TTS/Audio error: {e}")
                speech.mark_ended()
        else:
            # Original Animaze WebSocket behavior
            # Retry connection
            for _ in range(6):
                await connect_animaze(cfg, speech)
                if animaze_ws is not None:
                    break
                await asyncio.sleep(0.5)
            
            if animaze_ws is None:
                log.warning("ChatPal nicht erreichbar, retry wird eingeplant")
                await asyncio.sleep(0.8)
                await message_queue.put(text)
                continue
            
            await speech.wait_idle()
            
            try:
                payload = {
                    "action": "ChatbotSendMessage",
                    "id": str(time.time_ns()),
                    "message": text,
                    "priority": 1
                }
                log.info(f"→ ChatPal SEND: {payload['message']}")
                await animaze_ws.send(json.dumps(payload))
                
                st = int(cfg.get("speech", {}).get("wait_start_timeout_ms", 1200)) / 1000.0
                mt = int(cfg.get("speech", {}).get("max_speech_ms", 15000)) / 1000.0
                pg = int(cfg.get("speech", {}).get("post_gap_ms", 250)) / 1000.0
                
                started = await speech.wait_started(timeout=st)
                if started:
                    await speech.wait_ended(timeout=mt)
                await asyncio.sleep(pg)
                
                LAST_OUTPUT_TS = time.time()
            except Exception as e:
                log.error(f"ChatPal SEND Fehler: {e}")
                await asyncio.sleep(0.5)
                await message_queue.put(text)
        
        await asyncio.sleep(0.02)


async def process_comments(
    cfg: Dict[str, Any],
    memory_db: MemoryDB,
    batcher: OutboxBatcher,
    viewers: Dict[str, Dict]
) -> None:
    """
    Process incoming comments and generate responses.
    
    Args:
        cfg: Configuration dictionary
        memory_db: MemoryDB instance
        batcher: OutboxBatcher instance
        viewers: Active viewers dictionary
    """
    comment_cfg = cfg.get("comment", {})
    
    if not bool(int(comment_cfg.get("enabled", 1))):
        while True:
            _ = await comment_queue.get()
        return
    
    global_cd = int(comment_cfg.get("global_cooldown", 6))
    per_user_cd = int(comment_cfg.get("per_user_cooldown", 15))
    max_per_min = int(comment_cfg.get("max_replies_per_min", 20))
    reply_threshold = float(comment_cfg.get("reply_threshold", 0.6))
    
    # Guard against excessively high thresholds
    if reply_threshold > MAX_REPLY_THRESHOLD:
        log.info(f"reply_threshold {reply_threshold} zu hoch, setze auf {DEFAULT_REPLY_THRESHOLD}")
        reply_threshold = DEFAULT_REPLY_THRESHOLD
    
    resp_greet = bool(int(comment_cfg.get("respond_to_greetings", 1)))
    greet_cd = int(comment_cfg.get("greeting_cooldown", 360))
    resp_thanks = bool(int(comment_cfg.get("respond_to_thanks", 1)))
    
    scorer = Relevance(comment_cfg)
    resp = ResponseEngine(cfg, memory_db)
    bucket = TokenBucket(capacity=max_per_min, rate_per_sec=max(1, max_per_min) / 60.0)
    
    next_allowed_global = 0.0
    per_user_until_local: Dict[str, float] = {}
    
    while True:
        item = await comment_queue.get()
        try:
            txt = item["text"]
            uid = item["uid"]
            nick = item["nick"]
            
            touch_viewer(viewers, uid, nick)
            now = time.time()
            
            if len(txt) < int(comment_cfg.get("min_length", 3)) or scorer.is_ignored(txt):
                continue
            
            if now < per_user_until_local.get(uid, 0):
                await asyncio.sleep(0.05)
                await comment_queue.put(item)
                continue
            
            score = scorer.score(txt)
            quick = False
            
            # Handle greetings
            if resp_greet and scorer.is_greeting(txt) and ("?" not in txt) and (len(txt.split()) <= 4):
                user = await memory_db.get_user(uid)
                if now - user.last_greet >= greet_cd:
                    # Update last_greet
                    user.last_greet = now
                    await memory_db.save_user(user)
                    
                    await bucket.take()
                    if time.time() < next_allowed_global:
                        await asyncio.sleep(max(0.01, next_allowed_global - time.time()))
                    if batcher:
                        await batcher.add(f"{nick} sagt hallo", uid=uid)
                    next_allowed_global = time.time() + global_cd
                    per_user_until_local[uid] = time.time() + per_user_cd
                    quick = True
            
            if quick:
                continue
            
            # Handle thanks
            if resp_thanks and scorer.is_thanks(txt):
                await bucket.take()
                if time.time() < next_allowed_global:
                    await asyncio.sleep(max(0.01, next_allowed_global - time.time()))
                if batcher:
                    await batcher.add(f"{nick} bedankt sich", uid=uid)
                next_allowed_global = time.time() + global_cd
                per_user_until_local[uid] = time.time() + per_user_cd
                continue
            
            # Handle high-relevance comments
            if score >= reply_threshold:
                await bucket.take()
                if time.time() < next_allowed_global:
                    await asyncio.sleep(max(0.01, next_allowed_global - time.time()))
                reply = await resp.reply_to_comment(nick, txt, uid)
                if reply and batcher:
                    await batcher.add(f"@{nick}: {txt} → {reply}", uid=uid)
                    next_allowed_global = time.time() + global_cd
                    per_user_until_local[uid] = time.time() + per_user_cd
        except Exception as e:
            log.error(f"process_comments Fehler: {e}")


async def process_event_batch(
    cfg: Dict[str, Any],
    memory_db: MemoryDB,
    batcher: OutboxBatcher,
    viewers: Dict[str, Dict],
    greet_tasks: Dict[str, asyncio.Task],
    pending_joins: Set[str]
) -> None:
    """
    Process batched events from TikTok.
    
    Args:
        cfg: Configuration dictionary
        memory_db: MemoryDB instance
        batcher: OutboxBatcher instance
        viewers: Active viewers dictionary
        greet_tasks: Active greeting tasks
        pending_joins: Pending join announcements
    """
    event_priority = cfg.get("event_priority", {
        "gift": 3, "follow": 2, "subscribe": 3, "share": 2, "like": 1, "join": 1
    })
    
    while True:
        try:
            tasks = [
                asyncio.create_task(gift_queue.get()),
                asyncio.create_task(join_queue.get()),
                asyncio.create_task(follow_queue.get()),
                asyncio.create_task(share_queue.get()),
                asyncio.create_task(subscribe_queue.get()),
                asyncio.create_task(like_queue.get())
            ]
            
            done, pending = await asyncio.wait(tasks, timeout=0.2, return_when=asyncio.FIRST_COMPLETED)
            
            for t in pending:
                t.cancel()
            
            for t in done:
                try:
                    evt = t.result()
                    uid = getattr(evt.user, "uniqueId", "") or getattr(evt.user, "id", "")
                    if not uid:
                        continue
                    
                    nick = getattr(evt.user, "nickname", "") or uid
                    touch_viewer(viewers, uid, nick)
                    
                    # Determine event type and priority
                    evt_type = type(evt).__name__.replace("Event", "").lower()
                    priority = event_priority.get(evt_type, 1)
                    
                    if isinstance(evt, GiftEvent):
                        gname = getattr(evt.gift, "name", "Gift")
                        count = int(getattr(evt, "repeat_count", getattr(evt.gift, "repeat_count", 1)) or 1)
                        await memory_db.remember_event(uid, nickname=nick, gift_inc=count)
                        if batcher:
                            await batcher.add(f"{nick} sent {gname} x{count}", priority=priority, uid=uid)
                    elif isinstance(evt, JoinEvent):
                        await memory_db.remember_event(uid, nickname=nick, join=True)
                        if int(cfg.get("join_rules", {}).get("enabled", 1)):
                            if uid not in greet_tasks:
                                greet_tasks[uid] = asyncio.create_task(
                                    schedule_greeting(uid, viewers, greet_tasks, pending_joins, memory_db, cfg)
                                )
                            pending_joins.add(nick)
                    elif isinstance(evt, FollowEvent):
                        await memory_db.remember_event(uid, nickname=nick, follow=True)
                        if batcher:
                            await batcher.add(f"{nick} followed", priority=priority, uid=uid)
                    elif isinstance(evt, ShareEvent):
                        await memory_db.remember_event(uid, nickname=nick, share=True)
                        if batcher:
                            await batcher.add(f"{nick} shared", priority=priority, uid=uid)
                    elif isinstance(evt, SubscribeEvent):
                        await memory_db.remember_event(uid, nickname=nick, sub=True)
                        if batcher:
                            await batcher.add(f"{nick} subscribed", priority=priority, uid=uid)
                    elif isinstance(evt, LikeEvent):
                        count = int(getattr(evt, "count", 1))
                        if count >= int(cfg.get("like_threshold", 20)):
                            await memory_db.remember_event(uid, nickname=nick, like_inc=count)
                            if batcher:
                                await batcher.add(f"{nick} liked x{count}", priority=priority, uid=uid)
                except Exception as e:
                    log.error(f"Error processing event: {e}")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            log.error(f"process_event_batch Fehler: {e}")


async def join_announcer_worker(cfg: Dict[str, Any], batcher: OutboxBatcher, speech: SpeechState, mic: MicState) -> None:
    """
    Worker that announces pending joins.
    
    Args:
        cfg: Configuration dictionary
        batcher: OutboxBatcher instance
        speech: SpeechState instance
        mic: MicState instance
    """
    global LAST_JOIN_ANNOUNCE_TS, PENDING_JOINS, LAST_OUTPUT_TS
    
    while True:
        await asyncio.sleep(1.0)
        
        if not batcher:
            continue
        if speech.is_speaking() or mic.is_active():
            continue
        if not PENDING_JOINS:
            continue
        
        idle_need = int(cfg.get("join_rules", {}).get("min_idle_since_last_output_sec", 25))
        gcd = int(cfg.get("join_rules", {}).get("greet_global_cooldown_sec", 180))
        
        if (time.time() - LAST_OUTPUT_TS) < idle_need:
            continue
        if (time.time() - LAST_JOIN_ANNOUNCE_TS) < gcd:
            continue
        
        names = list(PENDING_JOINS)[:20]
        for n in names:
            PENDING_JOINS.discard(n)
        
        if names:
            joined_chunk = ", ".join(names)
            await batcher.add(f"Neu dabei: {joined_chunk}")
            LAST_JOIN_ANNOUNCE_TS = time.time()


async def tiktok_listener(
    cfg: Dict[str, Any],
    memory_db: MemoryDB,
    deduper: EventDeduper,
    viewers: Dict[str, Dict]
) -> None:
    """
    Listen to TikTok live events.
    
    Args:
        cfg: Configuration dictionary
        memory_db: MemoryDB instance
        deduper: EventDeduper instance
        viewers: Active viewers dictionary
    """
    sess = cfg["tiktok"].get("session_id") or ""
    client = TikTokLiveClient(unique_id=cfg["tiktok"]["unique_id"])
    
    # Apply session if provided
    if sess:
        try:
            if hasattr(client.web, "set_session_id"):
                client.web.set_session_id(sess)
            elif hasattr(client.web, "set_session"):
                client.web.set_session(sess)
            else:
                log.warning("TikTok Session ID konnte nicht gesetzt werden: keine passende Methode")
        except Exception as e:
            log.warning(f"TikTok Session ID konnte nicht gesetzt werden: {e}")
    
    comment_cfg = cfg.get("comment", {})
    min_len = int(comment_cfg.get("min_length", 3))
    scorer = Relevance(comment_cfg)
    
    @client.on(ConnectEvent)
    async def on_connect(evt: ConnectEvent):
        log.info(f"TikTok connected (Room {client.room_id})")
    
    @client.on(CommentEvent)
    async def on_comment(evt: CommentEvent):
        try:
            txt = (evt.comment or "").strip()
            low = txt.lower()
            if len(low) < min_len or scorer.is_ignored(low):
                return
            
            uid = getattr(evt.user, "uniqueId", "") or getattr(evt.user, "id", "")
            if not uid:
                return
            
            nick = getattr(evt.user, "nickname", "") or uid
            sig = make_signature("comment", uid, low)
            if await deduper.seen(sig):
                return
            
            touch_viewer(viewers, uid, nick)
            await memory_db.remember_event(uid, nickname=nick, message=txt)
            await comment_queue.put({"uid": uid, "nick": nick, "text": low})
            log.info(f"TikTok Kommentar von {nick}: {txt}")
        except Exception as e:
            log.error(f"Error processing comment: {e}")
    
    @client.on(GiftEvent)
    async def on_gift(evt: GiftEvent):
        try:
            uid = getattr(evt.user, "uniqueId", "") or getattr(evt.user, "id", "")
            sig = make_signature("gift", uid, getattr(evt.gift, "name", "Gift"), getattr(evt, "repeat_count", 1))
            if await deduper.seen(sig):
                return
            await gift_queue.put(evt)
        except Exception as e:
            log.error(f"Error processing gift: {e}")
    
    @client.on(FollowEvent)
    async def on_follow(evt: FollowEvent):
        try:
            now = time.time()
            if now - getattr(on_follow, "_last", 0) < int(cfg.get("comment", {}).get("global_cooldown", 6)):
                return
            setattr(on_follow, "_last", now)
            
            uid = getattr(evt.user, "uniqueId", "") or getattr(evt.user, "id", "")
            sig = make_signature("follow", uid)
            if await deduper.seen(sig):
                return
            await follow_queue.put(evt)
        except Exception as e:
            log.error(f"Error processing follow: {e}")
    
    @client.on(SubscribeEvent)
    async def on_subscribe(evt: SubscribeEvent):
        try:
            uid = getattr(evt.user, "uniqueId", "") or getattr(evt.user, "id", "")
            sig = make_signature("subscribe", uid)
            if await deduper.seen(sig):
                return
            await subscribe_queue.put(evt)
        except Exception as e:
            log.error(f"Error processing subscribe: {e}")
    
    @client.on(LikeEvent)
    async def on_like(evt: LikeEvent):
        try:
            await like_queue.put(evt)
        except Exception as e:
            log.error(f"Error processing like: {e}")
    
    @client.on(ShareEvent)
    async def on_share(evt: ShareEvent):
        try:
            uid = getattr(evt.user, "uniqueId", "") or getattr(evt.user, "id", "")
            sig = make_signature("share", uid)
            if await deduper.seen(sig):
                return
            await share_queue.put(evt)
        except Exception as e:
            log.error(f"Error processing share: {e}")
    
    @client.on(JoinEvent)
    async def on_join(evt: JoinEvent):
        try:
            uid = getattr(evt.user, "uniqueId", "") or getattr(evt.user, "id", "")
            if not uid:
                return
            
            nick = getattr(evt.user, "nickname", "") or uid
            sig = make_signature("join", uid)
            if await deduper.seen(sig):
                return
            
            touch_viewer(viewers, uid, nick)
            await join_queue.put(evt)
        except Exception as e:
            log.error(f"Error processing join: {e}")
    
    @client.on(DisconnectEvent)
    async def on_disconnect(evt: DisconnectEvent):
        log.warning("TikTok disconnected; reconnecting…")
        await asyncio.sleep(5)
        try:
            await client.connect()
        except Exception as e:
            log.error(f"TikTok reconnect failed: {e}")
    
    # Retry connection with exponential backoff
    max_retries = 5
    for attempt in range(max_retries):
        try:
            await client.connect(fetch_gift_info=True)
            break
        except Exception as e:
            log.error(f"TikTok connection failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                delay = 2 ** attempt
                await asyncio.sleep(delay)
            else:
                log.error("TikTok connection failed after all retries")
                raise


async def clean_memory_periodic(memory_db: MemoryDB, decay_days: int) -> None:
    """
    Periodically clean old memory entries.
    
    Args:
        memory_db: MemoryDB instance
        decay_days: Number of days after which user data is considered stale
    """
    while True:
        await asyncio.sleep(3600)
        try:
            old_count = await memory_db.get_user_count()
            removed = await memory_db.clean_old_users(decay_days)
            new_count = await memory_db.get_user_count()
            
            # Trigger garbage collection
            gc.collect()
            
            log.info(f"Memory gecleant: {removed} Benutzer entfernt, {new_count} verbleibend")
        except Exception as e:
            log.error(f"Memory cleanup Fehler: {e}")


async def start_all(cfg: Dict[str, Any], gui=None) -> None:
    """
    Start all application components.
    
    Args:
        cfg: Configuration dictionary
        gui: Optional GUI instance for callbacks
    """
    global viewers, greet_tasks, PENDING_JOINS
    global message_queue, comment_queue, gift_queue, like_queue
    global join_queue, follow_queue, share_queue, subscribe_queue
    
    # Initialize asyncio queues in the current event loop
    message_queue = asyncio.Queue()
    comment_queue = asyncio.Queue()
    gift_queue = asyncio.Queue()
    like_queue = asyncio.Queue()
    join_queue = asyncio.Queue()
    follow_queue = asyncio.Queue()
    share_queue = asyncio.Queue()
    subscribe_queue = asyncio.Queue()
    
    # Initialize state
    speech = SpeechState()
    mic = MicState()
    
    mem_cfg = cfg.get("memory", {})
    
    # Initialize MemoryDB
    json_path = mem_cfg.get("file", "memory.json")
    # Convert memory.json to memory.db safely
    base_path = os.path.splitext(json_path)[0]
    db_path = f"{base_path}.db"
    per_user_history = mem_cfg.get("per_user_history", 10)
    memory_db = MemoryDB(db_path=db_path, per_user_history=per_user_history)
    await memory_db.initialize()
    log.info(f"MemoryDB initialized with {await memory_db.get_user_count()} users")
    
    deduper = EventDeduper(int(cfg.get("dedupe_ttl", 600)))
    
    viewers = {}
    greet_tasks = {}
    PENDING_JOINS = set()
    
    # Initialize TTS and Audio managers if enabled
    tts_manager = None
    audio_manager = None
    tts_enabled = bool(int(cfg.get("tts", {}).get("enabled", 0)))
    
    if tts_enabled:
        try:
            log.info("Initializing TTS and Audio systems...")
            
            # Initialize AudioManager
            audio_manager = AudioManager(cfg)
            
            # Initialize TTSManager
            tts_manager = TTSManager(cfg)
            await tts_manager.initialize()
            
            log.info("TTS and Audio systems initialized successfully")
            
            # Schedule periodic cache cleanup
            async def cleanup_tts_cache():
                while True:
                    await asyncio.sleep(86400)  # Once per day
                    try:
                        await tts_manager.clean_old_cache()
                        await tts_manager.clean_temp_files()
                    except Exception as e:
                        log.error(f"TTS cache cleanup error: {e}")
            
            asyncio.create_task(cleanup_tts_cache())
        except Exception as e:
            log.error(f"Failed to initialize TTS/Audio: {e}")
            log.warning("Falling back to Animaze WebSocket mode")
            tts_manager = None
            audio_manager = None
    
    # Start microphone monitor if enabled
    micmon = None
    mic_enabled = int(cfg.get("microphone", {}).get("enabled", 1))
    if mic_enabled:
        def vu_cb(level):
            pass
        
        micmon = MicrophoneMonitor(cfg, mic, level_cb=vu_cb)
        mic_device = str(cfg.get("microphone", {}).get("device", "")).strip()
        if mic_device:
            micmon.set_device(mic_device)
        else:
            micmon.start()
        
        if gui:
            gui.micmon_ref = micmon
    
    # Create batcher with proper callback
    async def send_callback(text):
        await send_to_animaze(text, cfg)
    
    ob = cfg.get("outbox", {})
    batcher = OutboxBatcher(
        window_s=int(ob.get("window_seconds", 8)),
        max_items=int(ob.get("max_items", 8)),
        max_chars=int(ob.get("max_chars", 320)),
        sep=str(ob.get("separator", " • ")),
        send_callback=send_callback,
        speech_state=speech,
        mic_state=mic
    )
    
    # Start background tasks
    asyncio.create_task(sender_worker(cfg, speech, tts_manager, audio_manager))
    asyncio.create_task(clean_memory_periodic(memory_db, mem_cfg.get("decay_days", 90)))
    asyncio.create_task(batcher.worker())
    asyncio.create_task(join_announcer_worker(cfg, batcher, speech, mic))
    asyncio.create_task(process_comments(cfg, memory_db, batcher, viewers))
    asyncio.create_task(process_event_batch(cfg, memory_db, batcher, viewers, greet_tasks, PENDING_JOINS))
    
    # Start TikTok listener
    await tiktok_listener(cfg, memory_db, deduper, viewers)


def main():
    """Main entry point for the legacy Tkinter GUI."""
    cfg = load_settings()
    app = ConfigGUI(cfg, start_all)
    app.mainloop()


if __name__ == "__main__":
    main()
