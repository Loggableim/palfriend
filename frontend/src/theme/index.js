/**
 * Main theme configuration for the PalFriend UI
 * Integrates colors, typography, and spacing into MUI theme
 * 
 * Usage: import { createPalFriendTheme } from '../theme'
 */

import { createTheme } from '@mui/material/styles';
import { colors } from './colors';
import { typography } from './typography';
import { borderRadius, shadowsLight, shadowsDark } from './spacing';

/**
 * Creates a MUI theme configured for PalFriend
 * 
 * @param {boolean} darkMode - Whether to use dark mode
 * @returns {Theme} Configured MUI theme
 */
export const createPalFriendTheme = (darkMode = true) => {
  const mode = darkMode ? 'dark' : 'light';
  const shadows = darkMode ? shadowsDark : shadowsLight;
  
  return createTheme({
    palette: {
      mode,
      primary: colors.primary,
      secondary: colors.secondary,
      success: colors.success,
      error: colors.error,
      warning: colors.warning,
      info: colors.info,
      grey: colors.grey,
      background: {
        default: darkMode ? colors.background.dark.default : colors.background.light.default,
        paper: darkMode ? colors.background.dark.paper : colors.background.light.paper,
      },
      text: {
        primary: darkMode ? colors.text.dark.primary : colors.text.light.primary,
        secondary: darkMode ? colors.text.dark.secondary : colors.text.light.secondary,
        disabled: darkMode ? colors.text.dark.disabled : colors.text.light.disabled,
      },
      divider: darkMode ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.12)',
    },
    
    typography,
    
    shape: {
      borderRadius: borderRadius.md,
    },
    
    components: {
      // Button overrides
      MuiButton: {
        styleOverrides: {
          root: {
            textTransform: 'none',
            fontWeight: 500,
            borderRadius: borderRadius.md,
            padding: '8px 16px',
          },
          containedPrimary: {
            '&:hover': {
              backgroundColor: colors.primary.dark,
            },
          },
          containedSecondary: {
            '&:hover': {
              backgroundColor: colors.secondary.dark,
            },
          },
        },
      },
      
      // Card overrides
      MuiCard: {
        styleOverrides: {
          root: {
            boxShadow: darkMode ? shadows.lg : shadows.md,
            borderRadius: borderRadius.lg,
            transition: 'box-shadow 0.2s ease-in-out, transform 0.2s ease-in-out',
            '&:hover': {
              boxShadow: darkMode ? shadows.xl : shadows.lg,
            },
          },
        },
      },
      
      // CardContent overrides
      MuiCardContent: {
        styleOverrides: {
          root: {
            padding: '24px',
            '&:last-child': {
              paddingBottom: '24px',
            },
          },
        },
      },
      
      // Paper overrides
      MuiPaper: {
        styleOverrides: {
          root: {
            backgroundImage: 'none', // Remove default gradient
          },
          elevation1: {
            boxShadow: shadows.sm,
          },
          elevation2: {
            boxShadow: shadows.md,
          },
          elevation3: {
            boxShadow: shadows.lg,
          },
        },
      },
      
      // Chip overrides
      MuiChip: {
        styleOverrides: {
          root: {
            borderRadius: borderRadius.sm,
            fontWeight: 500,
          },
        },
      },
      
      // TextField overrides
      MuiTextField: {
        defaultProps: {
          variant: 'outlined',
          size: 'medium',
        },
      },
      
      // Slider overrides
      MuiSlider: {
        styleOverrides: {
          root: {
            height: 8,
          },
          thumb: {
            width: 20,
            height: 20,
          },
          track: {
            borderRadius: borderRadius.sm,
          },
          rail: {
            borderRadius: borderRadius.sm,
            opacity: 0.3,
          },
        },
      },
      
      // LinearProgress overrides
      MuiLinearProgress: {
        styleOverrides: {
          root: {
            borderRadius: borderRadius.full,
            height: 8,
          },
          bar: {
            borderRadius: borderRadius.full,
          },
        },
      },
      
      // Tab overrides
      MuiTab: {
        styleOverrides: {
          root: {
            textTransform: 'none',
            fontWeight: 500,
            minHeight: 56,
          },
        },
      },
      
      // Accordion overrides
      MuiAccordion: {
        styleOverrides: {
          root: {
            borderRadius: `${borderRadius.md}px !important`,
            '&:before': {
              display: 'none',
            },
            '&.Mui-expanded': {
              margin: '8px 0',
            },
          },
        },
      },
      
      // Switch overrides
      MuiSwitch: {
        styleOverrides: {
          root: {
            width: 52,
            height: 30,
            padding: 0,
          },
          switchBase: {
            padding: 3,
            '&.Mui-checked': {
              transform: 'translateX(22px)',
            },
          },
          thumb: {
            width: 24,
            height: 24,
          },
          track: {
            borderRadius: borderRadius.full,
          },
        },
      },
      
      // Tooltip overrides
      MuiTooltip: {
        styleOverrides: {
          tooltip: {
            borderRadius: borderRadius.sm,
            fontSize: '0.75rem',
            padding: '8px 12px',
          },
        },
      },
      
      // AppBar overrides
      MuiAppBar: {
        styleOverrides: {
          root: {
            boxShadow: shadows.md,
          },
        },
      },
    },
  });
};

// Export theme tokens for direct usage
export { colors } from './colors';
export { typography } from './typography';
export { spacing, borderRadius, shadowsLight, shadowsDark } from './spacing';

export default createPalFriendTheme;
