/**
 * Spacing and layout tokens for the PalFriend UI
 * Based on an 8px grid system for consistent spacing
 * 
 * Usage: import { spacing, shadows, borderRadius } from '../theme/spacing'
 */

// Base spacing unit (8px)
const BASE_UNIT = 8;

/**
 * Spacing scale (multipliers of 8px)
 */
export const spacing = {
  0: 0,
  0.5: BASE_UNIT * 0.5,  // 4px
  1: BASE_UNIT * 1,      // 8px
  1.5: BASE_UNIT * 1.5,  // 12px
  2: BASE_UNIT * 2,      // 16px
  2.5: BASE_UNIT * 2.5,  // 20px
  3: BASE_UNIT * 3,      // 24px
  4: BASE_UNIT * 4,      // 32px
  5: BASE_UNIT * 5,      // 40px
  6: BASE_UNIT * 6,      // 48px
  8: BASE_UNIT * 8,      // 64px
  10: BASE_UNIT * 10,    // 80px
  12: BASE_UNIT * 12,    // 96px
  16: BASE_UNIT * 16,    // 128px
};

/**
 * Border radius scale
 */
export const borderRadius = {
  none: 0,
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  '2xl': 24,
  full: 9999,
};

/**
 * Box shadow elevation scale for light mode
 */
export const shadowsLight = {
  none: 'none',
  sm: '0 1px 2px rgba(0, 0, 0, 0.05)',
  md: '0 2px 4px rgba(0, 0, 0, 0.1)',
  lg: '0 4px 6px rgba(0, 0, 0, 0.1)',
  xl: '0 8px 12px rgba(0, 0, 0, 0.1)',
  '2xl': '0 12px 24px rgba(0, 0, 0, 0.12)',
  inner: 'inset 0 2px 4px rgba(0, 0, 0, 0.06)',
};

/**
 * Box shadow elevation scale for dark mode
 */
export const shadowsDark = {
  none: 'none',
  sm: '0 1px 2px rgba(0, 0, 0, 0.3)',
  md: '0 2px 4px rgba(0, 0, 0, 0.4)',
  lg: '0 4px 6px rgba(0, 0, 0, 0.5)',
  xl: '0 8px 12px rgba(0, 0, 0, 0.5)',
  '2xl': '0 12px 24px rgba(0, 0, 0, 0.6)',
  inner: 'inset 0 2px 4px rgba(0, 0, 0, 0.3)',
};

/**
 * Breakpoints for responsive design
 * Matches MUI default breakpoints
 */
export const breakpoints = {
  xs: 0,
  sm: 600,
  md: 900,
  lg: 1200,
  xl: 1536,
};

/**
 * Z-index scale for layering
 */
export const zIndex = {
  base: 0,
  dropdown: 1000,
  sticky: 1100,
  modal: 1300,
  popover: 1400,
  tooltip: 1500,
};

/**
 * Animation durations
 */
export const transitions = {
  fast: '150ms',
  normal: '200ms',
  slow: '300ms',
  verySlow: '500ms',
};

/**
 * Animation easing functions
 */
export const easing = {
  easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
  easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
  easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
  sharp: 'cubic-bezier(0.4, 0, 0.6, 1)',
};

export default {
  spacing,
  borderRadius,
  shadowsLight,
  shadowsDark,
  breakpoints,
  zIndex,
  transitions,
  easing,
};
