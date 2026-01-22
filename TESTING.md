# Testing the New Web Interface

## Quick Start Testing

### 1. Backend Testing

Test that the Flask backend starts correctly:

```bash
python3 app.py
```

Expected output:
- Flask app starts on port 5000
- No errors about missing modules
- WebSocket server initialized
- API endpoints registered

Test API endpoints with curl:

```bash
# Get settings
curl http://localhost:5000/api/settings

# Get status
curl http://localhost:5000/api/status

# Get devices
curl http://localhost:5000/api/devices

# Get defaults
curl http://localhost:5000/api/defaults
```

### 2. Frontend Development Testing

```bash
cd frontend
npm install
npm run dev
```

Expected output:
- Vite dev server starts on port 3000
- Opens browser automatically
- No compilation errors
- Hot reload works

### 3. Frontend Production Build Testing

```bash
cd frontend
npm run build
```

Expected output:
- Build completes without errors
- Creates `build/` directory
- Minified and optimized assets

### 4. Full Stack Testing

```bash
# Build frontend first
cd frontend
npm run build
cd ..

# Start Flask (serves built frontend)
python3 app.py
```

Then open http://localhost:5000 in browser.

## Feature Testing Checklist

### Dashboard Tab
- [ ] Connection status indicators show for TikTok, Animaze, Microphone
- [ ] Start button starts the application
- [ ] Stop button stops the application
- [ ] Statistics cards show correct numbers
- [ ] VU meter animates when microphone is active
- [ ] VU meter chart displays history
- [ ] Memory statistics display correctly

### Settings Tab
- [ ] All settings load from backend
- [ ] Text fields update correctly
- [ ] Sliders work and show current values
- [ ] Toggles switch on/off
- [ ] Dropdowns show options
- [ ] Save button saves settings
- [ ] Export JSON downloads configuration
- [ ] Export YAML downloads configuration
- [ ] Drag-and-drop area accepts files
- [ ] Importing JSON updates settings
- [ ] Importing YAML updates settings
- [ ] Password fields can be shown/hidden
- [ ] Device selector shows available devices

### Logs Tab
- [ ] Logs appear in real-time
- [ ] Search/filter works
- [ ] Clear button empties logs
- [ ] Download button saves logs to file
- [ ] Auto-scroll toggle works
- [ ] Log level colors are correct
- [ ] Timestamps are formatted

### Events Tab
- [ ] Event statistics update in real-time
- [ ] Event stream shows new events
- [ ] Event icons are correct
- [ ] Event colors match types
- [ ] Timestamps are formatted

### Theme & Localization
- [ ] Dark mode toggle switches theme
- [ ] Theme persists on page reload
- [ ] Language selector shows options
- [ ] Switching to German translates UI
- [ ] Switching to English translates UI
- [ ] Language persists on page reload

### Responsive Design
- [ ] Desktop view (1200px+) looks good
- [ ] Tablet view (768px-1199px) adapts layout
- [ ] Mobile view (<768px) shows mobile-friendly layout
- [ ] Navigation works on all screen sizes
- [ ] Touch interactions work on mobile

### Real-Time Updates
- [ ] WebSocket connects on page load
- [ ] Logs appear without refresh
- [ ] Statistics update without refresh
- [ ] Microphone level updates smoothly
- [ ] Connection status changes reflect immediately
- [ ] Reconnects automatically if connection drops

### Animations
- [ ] Page transitions are smooth
- [ ] Button hover effects work
- [ ] Card hover effects work
- [ ] Modal animations are smooth
- [ ] List items animate when added
- [ ] Connection status pulses when connected

## Common Issues

### Frontend won't build
- Check Node.js version (must be 16+)
- Delete `node_modules` and run `npm install` again
- Check for syntax errors in JSX files

### Backend won't start
- Check Python version (must be 3.8+)
- Install missing dependencies: `pip install -r requirements.txt`
- Check for port conflicts (5000)

### WebSocket won't connect
- Ensure Flask backend is running
- Check browser console for errors
- Verify CORS settings
- Try disabling browser extensions

### Settings won't save
- Check Flask logs for errors
- Verify file permissions for settings.yaml
- Check API endpoint responses in browser DevTools

### Real-time updates not working
- Check WebSocket connection in browser console
- Verify Flask-SocketIO is installed
- Check for firewall blocking WebSocket

## Browser DevTools Testing

Open browser DevTools (F12) and check:

1. **Console Tab**
   - No JavaScript errors
   - WebSocket connection established
   - API calls succeed

2. **Network Tab**
   - API requests return 200 OK
   - WebSocket upgrade succeeds
   - Static assets load correctly

3. **Application Tab**
   - localStorage has 'darkMode' and 'language'
   - Values persist across reloads

## Performance Testing

- [ ] Initial page load < 3 seconds
- [ ] Navigation between tabs < 100ms
- [ ] Settings save < 500ms
- [ ] Log updates < 50ms latency
- [ ] VU meter updates 60fps
- [ ] No memory leaks after 1 hour

## Accessibility Testing

- [ ] Tab navigation works through all controls
- [ ] Screen reader can read all content
- [ ] Keyboard shortcuts work
- [ ] Contrast ratios meet WCAG standards
- [ ] Focus indicators are visible

## Cross-Browser Testing

Test in:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

## Security Testing

- [ ] API key fields are password type
- [ ] No sensitive data in browser console
- [ ] No sensitive data in localStorage
- [ ] CORS is properly configured
- [ ] Input validation works

## Automated Testing (Future)

For future improvements, consider adding:
- Unit tests with Jest
- Component tests with React Testing Library
- E2E tests with Playwright
- API tests with pytest
- Performance tests with Lighthouse

## Reporting Issues

When reporting issues, include:
1. Steps to reproduce
2. Expected behavior
3. Actual behavior
4. Browser and version
5. Operating system
6. Console errors (if any)
7. Network errors (if any)
