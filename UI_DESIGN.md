# UI Design Overview

## Modern Web Interface Features

The new PalFriend web interface features a complete redesign with modern UX principles:

### 🎨 Visual Design

#### Color Scheme
- **Dark Mode (Default)**
  - Background: Deep black (#0a0a0a)
  - Paper: Dark grey (#1e1e1e)
  - Primary: Blue (#1976d2)
  - Secondary: Pink (#dc004e)
  
- **Light Mode**
  - Background: Light grey (#f5f5f5)
  - Paper: White (#ffffff)
  - Primary: Blue (#1976d2)
  - Secondary: Pink (#dc004e)

#### Typography
- Font Family: Roboto, Helvetica, Arial, sans-serif
- Headings: 500 weight, proportional sizing
- Body: 400 weight, optimized line-height
- Code/Logs: Monospace font

#### Spacing
- Consistent 8px grid system
- Card padding: 24px
- Section spacing: 24px
- Component spacing: 16px
- Form field spacing: 16px

### 📱 Layout Structure

```
┌─────────────────────────────────────────────────────┐
│  App Bar                                  🌍 🌓     │
│  PalFriend - TikTok ChatPal Brain                   │
├─────────────────────────────────────────────────────┤
│  [Dashboard] [Settings] [Logs] [Events]            │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Tab Content Area                                   │
│  (Responsive Grid Layout)                           │
│                                                     │
│                                                     │
│                                                     │
├─────────────────────────────────────────────────────┤
│  Footer - © 2024 PalFriend                          │
└─────────────────────────────────────────────────────┘
```

### 🖥️ Dashboard Tab

```
┌─────────────────────────────────────────────────────┐
│  Status: ⚫ Running              [START] [STOP]     │
└─────────────────────────────────────────────────────┘

┌──────────────────────┐  ┌──────────────────────────┐
│ Connection Status    │  │ Microphone Level 🎤      │
│                      │  │ ████████░░░░ 67%         │
│ ✅ TikTok           │  │                          │
│ ✅ Animaze          │  │ [Live VU Chart]          │
│ ✅ Microphone       │  │                          │
└──────────────────────┘  └──────────────────────────┘

┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ 👥 142   │ │ 💬 1.2K  │ │ 🎁 89    │ │ ➕ 45    │
│ Viewers  │ │ Comments │ │ Gifts    │ │ Followers│
└──────────┘ └──────────┘ └──────────┘ └──────────┘

┌─────────────────────────────────────────────────────┐
│ Memory Statistics                                   │
│ Total Users: 1,234    Recent Activity: 89           │
└─────────────────────────────────────────────────────┘
```

### ⚙️ Settings Tab

```
[SAVE] [Export JSON] [Export YAML] [Reload]

┌─────────────────────────────────────────────────────┐
│ 📂 Import Configuration                             │
│ Drag and drop your file here or click to select    │
└─────────────────────────────────────────────────────┘

▼ TikTok Settings ───────────────────────────────────
  TikTok Handle: [@PupCid...................]
  Session ID:    [••••••••••••••••••••••••] 👁️

▶ Animaze Settings ──────────────────────────────────

▼ Comment Settings ──────────────────────────────────
  ☑️ Comment Processing Enabled
  
  Global Cooldown: ●───────────────── 15s
  Per-User Cooldown: ●───────────────── 30s
  Max Replies/Min: [20................]
  Reply Threshold: ●───────────────── 0.6
  
  ☑️ Respond to Greetings
  ☑️ Respond to Thanks

▶ Microphone Settings ───────────────────────────────
  ☑️ Microphone Enabled
  Device: [Logitech USB Mic ▼]
  Silence Threshold: ●───────────────── 0.02

▶ Join Settings ─────────────────────────────────────
```

### 📋 Logs Tab

```
[Search logs...] [🗑️] [⬇️] [Auto-scroll: ON]

Showing 127 of 1000 logs

┌─────────────────────────────────────────────────────┐
│ 14:23:45  [INFO]    TikTok connected (Room 123)    │
│ 14:23:46  [INFO]    Animaze WebSocket connected    │
│ 14:23:48  [WARNING] Rate limit approaching         │
│ 14:23:50  [ERROR]   Failed to process comment      │
│ 14:23:52  [INFO]    New viewer joined: John        │
└─────────────────────────────────────────────────────┘
```

### 📊 Events Tab

```
┌──────────┐ ┌──────────┐ ┌──────────┐
│ 💬 1,234 │ │ 🎁 89    │ │ ➕ 45    │
│ Comments │ │ Gifts    │ │ Followers│
└──────────┘ └──────────┘ └──────────┘

Real-time Updates
┌─────────────────────────────────────────────────────┐
│ 🎁 [gift]      14:30:12                             │
│ User123 sent Rose x5                                │
├─────────────────────────────────────────────────────┤
│ 💬 [comment]   14:30:10                             │
│ TikTok comment from Alice: Hello!                   │
├─────────────────────────────────────────────────────┤
│ ➕ [follow]    14:30:05                             │
│ Bob followed                                        │
└─────────────────────────────────────────────────────┘
```

### 🎭 Animations

1. **Page Transitions**
   - Fade in/out with slide animation
   - Duration: 300ms
   - Easing: ease-in-out

2. **Connection Status**
   - Pulsing animation when connected
   - Scale: 1 → 1.2 → 1
   - Duration: 2s, infinite

3. **Card Hover**
   - Scale up slightly (1.05x)
   - Box shadow increases
   - Duration: 200ms

4. **Button Click**
   - Scale down (0.95x)
   - Ripple effect from Material UI
   - Duration: 100ms

5. **Log/Event Entry**
   - Slide in from left
   - Fade in opacity
   - Duration: 200ms

6. **VU Meter**
   - Smooth bar animation
   - 60fps update rate
   - Color changes based on level
   - Chart updates in real-time

### 📐 Responsive Breakpoints

1. **Desktop (1200px+)**
   - Full 4-column grid for stats
   - Side-by-side layout for settings
   - Maximum width: 1400px

2. **Tablet (768px-1199px)**
   - 2-column grid for stats
   - Stacked settings sections
   - Optimized spacing

3. **Mobile (<768px)**
   - Single column layout
   - Stack all cards
   - Larger touch targets
   - Collapsible sections

### 🎯 Interactive Elements

1. **Sliders**
   - Visual value display
   - Marks at key positions
   - Smooth dragging
   - Immediate feedback

2. **Toggles**
   - Material UI Switch
   - Labeled clearly
   - Instant state change
   - Accessible

3. **Dropdowns**
   - Material UI Select
   - Search/filter support
   - Keyboard navigation
   - Custom styling

4. **Drag-and-Drop**
   - Visual feedback on hover
   - Border color change
   - Upload icon animation
   - File type validation

### 🌍 Localization

All UI text is translated through i18next:
- English (en) - Default
- German (de) - Vollständig übersetzt

Add new languages by:
1. Create new locale file in `src/i18n/locales/`
2. Translate all keys
3. Register in `src/i18n/config.js`
4. Add to language menu in `Layout.jsx`

### ♿ Accessibility

- Semantic HTML structure
- ARIA labels on interactive elements
- Keyboard navigation (Tab, Enter, Esc)
- Focus indicators visible
- Color contrast meets WCAG AA
- Screen reader compatible
- Alt text on icons

### 🔒 Security Features

- Password fields with toggle visibility
- No sensitive data in localStorage
- API key masking in UI
- CSRF protection via Flask
- CORS properly configured
- Input validation on all fields

### 📦 Component Architecture

```
App (Theme Provider)
└── Layout (Navigation)
    ├── Dashboard
    │   ├── StatusCard
    │   ├── ConnectionStatus
    │   ├── VUMeter
    │   ├── StatCards (x4)
    │   └── MemoryStats
    ├── Settings
    │   ├── ActionButtons
    │   ├── DragDropImport
    │   └── SettingsAccordions (x6)
    ├── Logs
    │   ├── FilterBar
    │   └── LogList
    └── Events
        ├── EventStats
        └── EventStream
```

### 🎨 Icon Usage

All icons from Material UI Icons:
- Dashboard: DashboardIcon
- Settings: SettingsIcon
- Logs: DescriptionIcon
- Events: EventIcon
- Start: PlayArrowIcon
- Stop: StopIcon
- Connected: CheckCircleIcon
- Disconnected: CancelIcon
- Theme: Brightness4/7Icon
- Language: LanguageIcon
- Microphone: MicIcon
- And many more...

All SVG-based for crisp rendering at any resolution.
