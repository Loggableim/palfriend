/**
 * Color palette for the PalFriend UI
 * Defines all color tokens used across the application
 * 
 * Usage: import { colors } from '../theme/colors'
 */

export const colors = {
  // Primary brand colors
  primary: {
    main: '#1976d2',
    light: '#42a5f5',
    dark: '#1565c0',
    contrastText: '#ffffff',
  },

  // Secondary brand colors
  secondary: {
    main: '#dc004e',
    light: '#ff4081',
    dark: '#c51162',
    contrastText: '#ffffff',
  },

  // Success colors
  success: {
    main: '#2e7d32',
    light: '#4caf50',
    dark: '#1b5e20',
    contrastText: '#ffffff',
  },

  // Error colors
  error: {
    main: '#d32f2f',
    light: '#ef5350',
    dark: '#c62828',
    contrastText: '#ffffff',
  },

  // Warning colors
  warning: {
    main: '#ed6c02',
    light: '#ff9800',
    dark: '#e65100',
    contrastText: '#ffffff',
  },

  // Info colors
  info: {
    main: '#0288d1',
    light: '#03a9f4',
    dark: '#01579b',
    contrastText: '#ffffff',
  },

  // Grey scale
  grey: {
    50: '#fafafa',
    100: '#f5f5f5',
    200: '#eeeeee',
    300: '#e0e0e0',
    400: '#bdbdbd',
    500: '#9e9e9e',
    600: '#757575',
    700: '#616161',
    800: '#424242',
    900: '#212121',
  },

  // Background colors
  background: {
    light: {
      default: '#f5f5f5',
      paper: '#ffffff',
      elevated: '#ffffff',
    },
    dark: {
      default: '#0a0a0a',
      paper: '#1e1e1e',
      elevated: '#2d2d2d',
    },
  },

  // Text colors
  text: {
    light: {
      primary: 'rgba(0, 0, 0, 0.87)',
      secondary: 'rgba(0, 0, 0, 0.6)',
      disabled: 'rgba(0, 0, 0, 0.38)',
    },
    dark: {
      primary: '#ffffff',
      secondary: 'rgba(255, 255, 255, 0.7)',
      disabled: 'rgba(255, 255, 255, 0.5)',
    },
  },

  // Connection status colors
  status: {
    online: '#4caf50',
    offline: '#f44336',
    connecting: '#ff9800',
    idle: '#9e9e9e',
  },

  // VU meter colors
  vuMeter: {
    low: '#4caf50',      // Green - safe level
    medium: '#ff9800',   // Orange - moderate level
    high: '#f44336',     // Red - high/clipping level
    background: '#e0e0e0',
  },
};

/**
 * CSS variable names for dynamic theming
 */
export const cssVars = {
  // Primary
  '--color-primary': colors.primary.main,
  '--color-primary-light': colors.primary.light,
  '--color-primary-dark': colors.primary.dark,
  
  // Secondary
  '--color-secondary': colors.secondary.main,
  '--color-secondary-light': colors.secondary.light,
  '--color-secondary-dark': colors.secondary.dark,
  
  // Status
  '--color-success': colors.success.main,
  '--color-error': colors.error.main,
  '--color-warning': colors.warning.main,
  '--color-info': colors.info.main,
  
  // Connection status
  '--color-status-online': colors.status.online,
  '--color-status-offline': colors.status.offline,
  '--color-status-connecting': colors.status.connecting,
  
  // VU meter
  '--color-vu-low': colors.vuMeter.low,
  '--color-vu-medium': colors.vuMeter.medium,
  '--color-vu-high': colors.vuMeter.high,
};

export default colors;
