/**
 * Typography configuration for the PalFriend UI
 * Defines all typography tokens and scales
 * 
 * Usage: import { typography } from '../theme/typography'
 */

// Font families
export const fontFamilies = {
  // Primary font for UI text
  primary: '"Roboto", "Helvetica", "Arial", sans-serif',
  
  // Monospace font for code, logs, and technical data
  mono: '"Roboto Mono", "Courier New", Consolas, monospace',
};

// Font weights
export const fontWeights = {
  light: 300,
  regular: 400,
  medium: 500,
  semibold: 600,
  bold: 700,
};

// Font sizes (in rem for accessibility)
export const fontSizes = {
  xs: '0.75rem',     // 12px
  sm: '0.875rem',    // 14px
  base: '1rem',      // 16px
  lg: '1.125rem',    // 18px
  xl: '1.25rem',     // 20px
  '2xl': '1.5rem',   // 24px
  '3xl': '1.875rem', // 30px
  '4xl': '2.25rem',  // 36px
  '5xl': '3rem',     // 48px
};

// Line heights
export const lineHeights = {
  tight: 1.25,
  normal: 1.5,
  relaxed: 1.75,
};

// Letter spacing
export const letterSpacing = {
  tight: '-0.025em',
  normal: '0',
  wide: '0.025em',
};

/**
 * Typography scale for MUI theme
 */
export const typography = {
  fontFamily: fontFamilies.primary,
  
  h1: {
    fontSize: fontSizes['4xl'],
    fontWeight: fontWeights.medium,
    lineHeight: lineHeights.tight,
    letterSpacing: letterSpacing.tight,
  },
  
  h2: {
    fontSize: fontSizes['3xl'],
    fontWeight: fontWeights.medium,
    lineHeight: lineHeights.tight,
    letterSpacing: letterSpacing.tight,
  },
  
  h3: {
    fontSize: fontSizes['2xl'],
    fontWeight: fontWeights.medium,
    lineHeight: lineHeights.normal,
    letterSpacing: letterSpacing.normal,
  },
  
  h4: {
    fontSize: fontSizes.xl,
    fontWeight: fontWeights.medium,
    lineHeight: lineHeights.normal,
    letterSpacing: letterSpacing.normal,
  },
  
  h5: {
    fontSize: fontSizes.lg,
    fontWeight: fontWeights.medium,
    lineHeight: lineHeights.normal,
    letterSpacing: letterSpacing.normal,
  },
  
  h6: {
    fontSize: fontSizes.base,
    fontWeight: fontWeights.semibold,
    lineHeight: lineHeights.normal,
    letterSpacing: letterSpacing.normal,
  },
  
  subtitle1: {
    fontSize: fontSizes.base,
    fontWeight: fontWeights.medium,
    lineHeight: lineHeights.normal,
    letterSpacing: letterSpacing.normal,
  },
  
  subtitle2: {
    fontSize: fontSizes.sm,
    fontWeight: fontWeights.medium,
    lineHeight: lineHeights.normal,
    letterSpacing: letterSpacing.normal,
  },
  
  body1: {
    fontSize: fontSizes.base,
    fontWeight: fontWeights.regular,
    lineHeight: lineHeights.relaxed,
    letterSpacing: letterSpacing.normal,
  },
  
  body2: {
    fontSize: fontSizes.sm,
    fontWeight: fontWeights.regular,
    lineHeight: lineHeights.relaxed,
    letterSpacing: letterSpacing.normal,
  },
  
  button: {
    fontSize: fontSizes.sm,
    fontWeight: fontWeights.medium,
    lineHeight: lineHeights.normal,
    letterSpacing: letterSpacing.wide,
    textTransform: 'none', // Override MUI default uppercase
  },
  
  caption: {
    fontSize: fontSizes.xs,
    fontWeight: fontWeights.regular,
    lineHeight: lineHeights.normal,
    letterSpacing: letterSpacing.normal,
  },
  
  overline: {
    fontSize: fontSizes.xs,
    fontWeight: fontWeights.medium,
    lineHeight: lineHeights.normal,
    letterSpacing: letterSpacing.wide,
    textTransform: 'uppercase',
  },
};

export default typography;
