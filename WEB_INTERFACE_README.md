# PalFriend Web Interface - Modern GUI Redesign

This document describes the new modern web-based interface for PalFriend TikTok ChatPal Brain.

## Overview

The GUI has been completely redesigned with a modern React frontend and Flask backend, replacing the legacy Tkinter interface.

## Features

✅ **Modern Web-Based UI** - React frontend served by Flask backend
✅ **Dark/Light Mode** - User-selectable themes with persistent preference
✅ **Tab-Based Navigation** - Dashboard, Settings, Logs, and Events sections
✅ **Fully Responsive** - Works seamlessly on desktop, tablet, and mobile
✅ **Drag-and-Drop Config** - Easy configuration file upload
✅ **Real-Time Updates** - WebSocket connection for live status
✅ **Visual Indicators** - Connection status for TikTok, Animaze, Microphone
✅ **Modern Input Controls** - Sliders, toggles, dropdowns instead of text fields
✅ **Live VU Meter** - Animated microphone level visualization
✅ **Interactive Dashboard** - Real-time KPI display with animations
✅ **Optimized Typography** - Clean, readable fonts and spacing
✅ **SVG Icons** - Material UI icons for crisp visuals
✅ **Smooth Animations** - Framer Motion for polished interactions
✅ **Localization Support** - English and German languages included
✅ **Config Export/Import** - JSON and YAML format support

## Architecture

### Backend (Flask)
- **app.py** - Main Flask application with REST API and WebSocket support
- REST endpoints for settings, status, device management
- WebSocket events for real-time updates (logs, stats, mic level)
- Integrates with existing main.py application logic

### Frontend (React + Vite)
- **Material UI** - Modern component library with theming
- **React Router** - Client-side routing
- **Socket.io Client** - Real-time WebSocket communication
- **i18next** - Internationalization framework
- **Framer Motion** - Animation library
- **Recharts** - Chart visualization for VU meter history
- **React Dropzone** - Drag-and-drop file upload

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Node.js Dependencies

```bash
cd frontend
npm install
```

## Running the Application

### Development Mode

Run the Flask backend and React frontend separately:

```bash
# Terminal 1: Start Flask backend
python app.py

# Terminal 2: Start React dev server
cd frontend
npm run dev
```

The frontend will be available at http://localhost:3000 (proxied to Flask at port 5000).

### Production Mode

Build the React frontend and serve it from Flask:

```bash
# Build React frontend
cd frontend
npm run build

# Start Flask (serves the built React app)
cd ..
python app.py
```

The application will be available at http://localhost:5000

## Legacy GUI (Tkinter)

The original Tkinter GUI is still available and can be launched with:

```bash
python main.py
```

This will start the legacy interface. To use the new web interface, use `app.py` instead.

## Usage

### Dashboard Tab
- View connection status (TikTok, Animaze, Microphone)
- Start/Stop the application
- Monitor real-time statistics (viewers, comments, gifts, followers)
- Watch live microphone level with VU meter
- View memory statistics

### Settings Tab
- Configure all application settings with modern controls
- Use sliders for numeric values (cooldowns, thresholds)
- Use toggles for boolean options
- Use dropdowns for selections (model, device)
- Drag-and-drop configuration files to import
- Export settings as JSON or YAML

### Logs Tab
- View real-time application logs
- Search/filter logs
- Download logs for debugging
- Auto-scroll to latest entries

### Events Tab
- Monitor live TikTok events
- View event statistics
- Track comments, gifts, follows, likes, joins, shares

## Theme Support

The interface supports both dark and light themes:
- Click the theme toggle button in the app bar
- Your preference is saved to localStorage
- Theme persists across sessions

## Localization

The interface is available in multiple languages:
- English (default)
- German (Deutsch)

To switch languages:
- Click the language icon in the app bar
- Select your preferred language
- Your selection is saved to localStorage

## Configuration Import/Export

### Export Settings
1. Go to Settings tab
2. Click "Export JSON" or "Export YAML"
3. File is downloaded to your browser

### Import Settings
1. Go to Settings tab
2. Drag configuration file to the upload area, or click to select
3. Settings are automatically loaded

Supported formats: `.json`, `.yaml`, `.yml`

## API Endpoints

The Flask backend provides these REST API endpoints:

- `GET /api/settings` - Get current settings
- `PUT /api/settings` - Update settings
- `GET /api/settings/export?format={json|yaml}` - Export settings
- `POST /api/settings/import` - Import settings
- `GET /api/status` - Get application status
- `POST /api/start` - Start the application
- `POST /api/stop` - Stop the application
- `GET /api/memory` - Get memory statistics
- `GET /api/devices` - Get available audio devices
- `GET /api/defaults` - Get default settings

## WebSocket Events

Real-time events pushed to clients:

- `status` - Full status update
- `status_change` - Application running state change
- `connection_status` - Service connection change
- `stats` - Statistics update
- `mic_level` - Microphone level update
- `log` - New log entry

## Technology Stack

### Backend
- Flask 3.0+ - Web framework
- Flask-CORS - Cross-origin resource sharing
- Flask-SocketIO - WebSocket support
- Python-SocketIO - SocketIO implementation

### Frontend
- React 18.2+ - UI framework
- Material UI 5.14+ - Component library
- **Tailwind CSS 4.x** - Utility-first CSS framework
- **DaisyUI 5.x** - Tailwind CSS component library with theming
- Vite 5.0+ - Build tool and dev server
- React Router 6.20+ - Routing
- Socket.io Client 4.5+ - WebSocket client
- i18next 23.7+ - Internationalization
- Framer Motion 10.16+ - Animations
- Recharts 2.10+ - Charts
- React Dropzone 14.2+ - File upload
- Axios 1.6+ - HTTP client

## DaisyUI Integration

The frontend includes [DaisyUI](https://daisyui.com/), a Tailwind CSS component library that provides:

- Pre-built component classes (buttons, cards, modals, etc.)
- Theme system with multiple built-in themes
- Custom theme support
- Responsive design utilities

### Available Themes

The following themes are configured:
- **light** (default)
- **dark** (activated automatically based on system preference)
- **cupcake** (light pastel theme)
- **palfriend** (custom brand theme)

### Using DaisyUI Components

DaisyUI components can be used alongside Material UI. Example:

```jsx
// DaisyUI button
<button className="btn btn-primary">Click Me</button>

// DaisyUI card
<div className="card bg-base-100 shadow-xl">
  <div className="card-body">
    <h2 className="card-title">Card Title</h2>
    <p>Card content here</p>
  </div>
</div>
```

### Theme Switching

To switch themes, add the `data-theme` attribute to the `html` element:

```javascript
// Switch to dark theme
document.documentElement.setAttribute('data-theme', 'dark');

// Switch to custom palfriend theme
document.documentElement.setAttribute('data-theme', 'palfriend');
```

### Custom Theme Configuration

The custom `palfriend` theme is defined in `frontend/src/styles/index.css` using the DaisyUI v5 plugin syntax:

```css
@plugin "daisyui/theme" {
  name: "palfriend";
  --color-primary: #1976d2;
  --color-secondary: #dc004e;
  /* ... more color tokens */
}
```

### DaisyUI Component Reference

For a full list of available components and their classes, see:
- [DaisyUI Components](https://daisyui.com/components/)
- [DaisyUI Themes](https://daisyui.com/docs/themes/)
- [DaisyUI Customization](https://daisyui.com/docs/config/)

## Browser Support

The interface supports all modern browsers:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Responsive Design

The interface is fully responsive with breakpoints for:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobile (< 768px)

## Performance

- Real-time updates via WebSocket (low latency)
- React component optimization with memoization
- Material UI theme caching
- Efficient log buffering (max 1000 entries)
- Optimized bundle size with Vite

## Accessibility

- Semantic HTML structure
- ARIA labels on interactive elements
- Keyboard navigation support
- High contrast mode support
- Screen reader compatible

## Customization

### Adding New Languages

1. Create a new locale file in `frontend/src/i18n/locales/`
2. Copy the structure from `en.json`
3. Translate all strings
4. Import and register in `frontend/src/i18n/config.js`
5. Add menu item in `Layout.jsx`

### Custom Themes

Modify the theme in `frontend/src/App.jsx`:

```javascript
const theme = createTheme({
  palette: {
    primary: { main: '#your-color' },
    secondary: { main: '#your-color' }
  }
});
```

## Troubleshooting

### Frontend won't start
- Ensure Node.js 16+ is installed
- Delete `node_modules` and run `npm install`
- Check for port conflicts (default: 3000)

### Backend won't start
- Ensure all Python dependencies are installed
- Check for port conflicts (default: 5000)
- Review Flask error logs

### WebSocket connection fails
- Ensure Flask backend is running
- Check firewall settings
- Verify CORS configuration

### Real-time updates not working
- Check WebSocket connection in browser console
- Verify Flask-SocketIO is installed correctly
- Check for network proxy issues

## Contributing

When adding new features:
1. Add backend API endpoints in `app.py`
2. Add frontend API calls in `frontend/src/utils/api.js`
3. Create/update React components
4. Add translations to all locale files
5. Update this documentation

## License

Same as main PalFriend project.
