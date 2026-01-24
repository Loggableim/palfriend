"""
Flask backend API server for the PalFriend web interface.
Provides REST API and WebSocket support for real-time updates.
"""

import asyncio
import json
import logging
import os
import threading
import time
from typing import Any, Dict

import yaml
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from settings import load_settings, save_settings, DEFAULT_SETTINGS
from memory import load_memory

log = logging.getLogger("ChatPalBrain")

# Flask app setup
app = Flask(__name__, static_folder='frontend/build', static_url_path=None)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global state
app_state = {
    'running': False,
    'connected': {
        'tiktok': False,
        'animaze': False,
        'microphone': False
    },
    'stats': {
        'viewers': 0,
        'comments': 0,
        'gifts': 0,
        'followers': 0
    },
    'mic_level': 0.0,
    'logs': []
}

main_thread = None
micmon_ref = None


class WebSocketHandler(logging.Handler):
    """Custom logging handler that broadcasts to WebSocket clients."""
    
    def emit(self, record):
        try:
            msg = self.format(record)
            log_entry = {
                'timestamp': time.time(),
                'level': record.levelname,
                'message': msg
            }
            app_state['logs'].append(log_entry)
            # Keep only last 1000 logs
            if len(app_state['logs']) > 1000:
                app_state['logs'] = app_state['logs'][-1000:]
            
            socketio.emit('log', log_entry)
        except Exception:
            pass


# Setup WebSocket logging
ws_handler = WebSocketHandler()
ws_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
logging.getLogger().addHandler(ws_handler)


# API Routes

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve React frontend for all non-API routes (SPA support)."""
    # Security note: We check if path STARTS with 'api/' or 'socket.io/'
    # This is intentional - paths like '/user/api/data' are valid SPA routes.
    # Actual API routes (e.g., /api/settings) have explicit Flask route handlers
    # that take precedence over this catch-all route.
    if path.startswith('api/') or path.startswith('socket.io/'):
        return jsonify({'error': 'Not found'}), 404
    
    # Serve static files directly if they exist
    if path and app.static_folder:
        file_path = os.path.join(app.static_folder, path)
        if os.path.isfile(file_path):
            return send_from_directory(app.static_folder, path)
    
    # Everything else -> index.html (React Router handles it)
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get current settings."""
    try:
        cfg = load_settings()
        return jsonify({'success': True, 'data': cfg})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/settings', methods=['PUT'])
def update_settings():
    """Update settings."""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        save_settings(data)
        return jsonify({'success': True, 'message': 'Settings saved successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/settings/export', methods=['GET'])
def export_settings():
    """Export settings as JSON or YAML."""
    try:
        cfg = load_settings()
        format_type = request.args.get('format', 'json').lower()
        
        if format_type == 'yaml':
            content = yaml.dump(cfg, default_flow_style=False, allow_unicode=True)
            return content, 200, {'Content-Type': 'application/x-yaml', 
                                 'Content-Disposition': 'attachment; filename=settings.yaml'}
        else:
            return jsonify(cfg), 200, {'Content-Disposition': 'attachment; filename=settings.json'}
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/settings/import', methods=['POST'])
def import_settings():
    """Import settings from JSON or YAML."""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        content = file.read().decode('utf-8')
        
        # Try to parse as YAML first, then JSON
        try:
            cfg = yaml.safe_load(content)
        except yaml.YAMLError:
            try:
                cfg = json.loads(content)
            except json.JSONDecodeError:
                return jsonify({'success': False, 'error': 'Invalid file format'}), 400
        
        save_settings(cfg)
        return jsonify({'success': True, 'message': 'Settings imported successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current application status."""
    return jsonify({'success': True, 'data': app_state})


@app.route('/api/start', methods=['POST'])
def start_app():
    """Start the TikTok bot."""
    global main_thread
    
    try:
        if app_state['running']:
            return jsonify({'success': False, 'error': 'Application already running'})
        
        cfg = load_settings()
        
        # Start main application in background thread
        def run_main():
            from main import start_all
            asyncio.run(start_all(cfg, None))
        
        main_thread = threading.Thread(target=run_main, daemon=True)
        main_thread.start()
        
        app_state['running'] = True
        socketio.emit('status_change', {'running': True})
        
        return jsonify({'success': True, 'message': 'Application started'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stop', methods=['POST'])
def stop_app():
    """Stop the TikTok bot."""
    try:
        app_state['running'] = False
        socketio.emit('status_change', {'running': False})
        return jsonify({'success': True, 'message': 'Application stopped'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/memory', methods=['GET'])
def get_memory():
    """Get memory statistics."""
    try:
        cfg = load_settings()
        mem_cfg = cfg.get('memory', {})
        memory = load_memory(mem_cfg.get('file', 'memory.json'), mem_cfg.get('decay_days', 90))
        
        stats = {
            'total_users': len(memory.get('users', {})),
            'recent_activity': sum(1 for u in memory.get('users', {}).values() 
                                  if time.time() - u.get('last_seen', 0) < 3600)
        }
        
        return jsonify({'success': True, 'data': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/devices', methods=['GET'])
def get_audio_devices():
    """Get available audio input devices."""
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        input_devs = [
            {'id': i, 'name': d['name'], 'channels': int(d.get('max_input_channels', 0))}
            for i, d in enumerate(devices)
            if int(d.get('max_input_channels', 0)) > 0
        ]
        return jsonify({'success': True, 'data': input_devs})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/defaults', methods=['GET'])
def get_defaults():
    """Get default settings."""
    return jsonify({'success': True, 'data': DEFAULT_SETTINGS})


@app.route('/api/persona/state', methods=['GET'])
def get_persona_state():
    """Get current persona state."""
    try:
        from response import ResponseEngine
        cfg = load_settings()
        memory = load_memory(cfg.get("memory", {}).get("file", "memory.json"))
        engine = ResponseEngine(cfg, memory)
        
        scope_id = request.args.get('scope_id', 'session')
        state = engine.get_persona_state(scope_id)
        
        if state is None:
            return jsonify({
                'success': False, 
                'error': 'Personality system not enabled or not available'
            }), 400
        
        return jsonify({'success': True, 'data': state})
    except Exception as e:
        log.error(f"Failed to get persona state: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/persona/reset', methods=['POST'])
def reset_persona():
    """Reset persona state to defaults."""
    try:
        from response import ResponseEngine
        cfg = load_settings()
        memory = load_memory(cfg.get("memory", {}).get("file", "memory.json"))
        engine = ResponseEngine(cfg, memory)
        
        data = request.get_json() or {}
        scope_id = data.get('scope_id', 'session')
        
        success = engine.reset_persona(scope_id)
        
        if not success:
            return jsonify({
                'success': False, 
                'error': 'Personality system not enabled or reset failed'
            }), 400
        
        return jsonify({'success': True, 'message': f'Persona reset for {scope_id}'})
    except Exception as e:
        log.error(f"Failed to reset persona: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/persona/update', methods=['PATCH'])
def update_persona():
    """Update persona tone weights or stance overrides."""
    try:
        from modules.persona_state import PersonaStateStore
        cfg = load_settings()
        personality_config = cfg.get("personality_bias", {})
        
        if not personality_config.get("enabled", 0):
            return jsonify({
                'success': False, 
                'error': 'Personality system not enabled'
            }), 400
        
        db_path = personality_config.get("persistence", {}).get("db_path", "./persona_state.db")
        store = PersonaStateStore(personality_config, db_path)
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        scope_id = data.get('scope_id', 'session')
        tone_weights = data.get('tone_weights')
        stance_overrides = data.get('stance_overrides')
        
        # Get current state
        current_state = store.get_state(scope_id)
        
        # Update with new values
        if tone_weights is not None:
            current_state['tone_weights'] = tone_weights
        if stance_overrides is not None:
            current_state['stance_overrides'] = stance_overrides
        
        # Save updated state
        store.save_state(scope_id, current_state['tone_weights'], current_state['stance_overrides'])
        
        return jsonify({'success': True, 'message': 'Persona updated', 'data': current_state})
    except Exception as e:
        log.error(f"Failed to update persona: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# WebSocket events

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection."""
    log.info('Client connected')
    emit('status', app_state)


@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection."""
    log.info('Client disconnected')


@socketio.on('request_status')
def handle_status_request():
    """Handle status request."""
    emit('status', app_state)


def broadcast_mic_level(level):
    """Broadcast microphone level to all clients."""
    app_state['mic_level'] = level
    socketio.emit('mic_level', {'level': level})


def broadcast_connection_status(service, connected):
    """Broadcast connection status change."""
    app_state['connected'][service] = connected
    socketio.emit('connection_status', {'service': service, 'connected': connected})


def broadcast_stats_update(stats):
    """Broadcast statistics update."""
    app_state['stats'].update(stats)
    socketio.emit('stats', app_state['stats'])


def main():
    """
    Main entry point for the web interface.
    
    Security Note:
        The application binds to 0.0.0.0 (all interfaces) to allow access from:
        - Docker containers
        - Cloud deployments
        - Network-accessible development environments
        
        For production deployments:
        - Use a reverse proxy (nginx, Apache) with SSL/TLS
        - Configure firewall rules to restrict access
        - Set PORT environment variable to use a different port
        - Consider using authentication middleware if exposing publicly
    """
    # Run Flask-SocketIO server
    port = int(os.environ.get('PORT', 5008))
    log.info(f'Starting web interface on http://localhost:{port}')
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)  # nosec B104


if __name__ == '__main__':
    main()
