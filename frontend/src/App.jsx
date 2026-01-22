import React, { useState, useEffect, useMemo } from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';

import Layout from './components/Layout';
import socketService from './utils/socket';
import { createPalFriendTheme } from './theme';

function App() {
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : true;
  });

  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
  }, [darkMode]);

  useEffect(() => {
    // Connect to WebSocket on mount
    socketService.connect();

    return () => {
      socketService.disconnect();
    };
  }, []);

  // Use centralized theme configuration
  const theme = useMemo(() => createPalFriendTheme(darkMode), [darkMode]);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box className={darkMode ? 'dark-mode' : 'light-mode'}>
          <Layout darkMode={darkMode} setDarkMode={setDarkMode} />
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
