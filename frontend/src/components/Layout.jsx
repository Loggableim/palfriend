import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  Tabs,
  Tab,
  Container,
  Menu,
  MenuItem,
  Switch,
  FormControlLabel,
  Tooltip
} from '@mui/material';
import {
  Brightness4 as DarkModeIcon,
  Brightness7 as LightModeIcon,
  Language as LanguageIcon,
  Dashboard as DashboardIcon,
  Settings as SettingsIcon,
  Description as LogsIcon,
  Event as EventsIcon
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';

import Dashboard from './Dashboard';
import Settings from './Settings';
import Logs from './Logs';
import Events from './Events';

function TabPanel({ children, value, index }) {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && (
        <AnimatePresence mode="wait">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <Box sx={{ py: 3 }}>{children}</Box>
          </motion.div>
        </AnimatePresence>
      )}
    </div>
  );
}

function Layout({ darkMode, setDarkMode }) {
  const { t, i18n } = useTranslation();
  const [tabValue, setTabValue] = useState(0);
  const [langAnchor, setLangAnchor] = useState(null);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleLanguageClick = (event) => {
    setLangAnchor(event.currentTarget);
  };

  const handleLanguageClose = () => {
    setLangAnchor(null);
  };

  const handleLanguageChange = (lang) => {
    i18n.changeLanguage(lang);
    localStorage.setItem('language', lang);
    handleLanguageClose();
  };

  const tabs = [
    { label: t('dashboard'), icon: <DashboardIcon />, component: Dashboard },
    { label: t('settings'), icon: <SettingsIcon />, component: Settings },
    { label: t('logs'), icon: <LogsIcon />, component: Logs },
    { label: t('events'), icon: <EventsIcon />, component: Events }
  ];

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static" elevation={0}>
        <Toolbar>
          <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
            <Typography variant="h6" component="div" sx={{ fontWeight: 600 }}>
              {t('app_title')}
            </Typography>
          </Box>

          <Tooltip title={t('language')}>
            <IconButton color="inherit" onClick={handleLanguageClick}>
              <LanguageIcon />
            </IconButton>
          </Tooltip>
          
          <Tooltip title={darkMode ? t('light_mode') : t('dark_mode')}>
            <IconButton color="inherit" onClick={() => setDarkMode(!darkMode)}>
              {darkMode ? <LightModeIcon /> : <DarkModeIcon />}
            </IconButton>
          </Tooltip>

          <Menu
            anchorEl={langAnchor}
            open={Boolean(langAnchor)}
            onClose={handleLanguageClose}
          >
            <MenuItem 
              onClick={() => handleLanguageChange('en')}
              selected={i18n.language === 'en'}
            >
              English
            </MenuItem>
            <MenuItem 
              onClick={() => handleLanguageChange('de')}
              selected={i18n.language === 'de'}
            >
              Deutsch
            </MenuItem>
          </Menu>
        </Toolbar>

        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          variant="fullWidth"
          textColor="inherit"
          indicatorColor="secondary"
          sx={{ 
            borderTop: 1, 
            borderColor: 'divider',
            backgroundColor: 'rgba(0, 0, 0, 0.1)'
          }}
        >
          {tabs.map((tab, index) => (
            <Tab
              key={index}
              label={tab.label}
              icon={tab.icon}
              iconPosition="start"
              sx={{ minHeight: 64 }}
            />
          ))}
        </Tabs>
      </AppBar>

      <Container maxWidth="xl" sx={{ flexGrow: 1 }}>
        {tabs.map((tab, index) => (
          <TabPanel key={index} value={tabValue} index={index}>
            <tab.component />
          </TabPanel>
        ))}
      </Container>

      <Box
        component="footer"
        sx={{
          py: 2,
          px: 3,
          mt: 'auto',
          backgroundColor: (theme) =>
            theme.palette.mode === 'light'
              ? theme.palette.grey[200]
              : theme.palette.grey[900],
          textAlign: 'center'
        }}
      >
        <Typography variant="body2" color="text.secondary">
          © 2024 PalFriend - TikTok ChatPal Brain
        </Typography>
      </Box>
    </Box>
  );
}

export default Layout;
