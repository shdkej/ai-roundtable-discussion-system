// Apple-inspired Design System
export const theme = {
  // Color Palette - Apple-inspired
  colors: {
    // Primary Apple Colors
    primary: {
      50: '#f0f9ff',
      100: '#e0f2fe', 
      200: '#bae6fd',
      300: '#7dd3fc',
      400: '#38bdf8',
      500: '#0ea5e9',  // Primary Blue
      600: '#0284c7',
      700: '#0369a1',
      800: '#075985',
      900: '#0c4a6e',
    },
    
    // Neutral Grays - Apple's sophisticated grays
    gray: {
      50: '#fafafa',
      100: '#f5f5f5',
      200: '#e5e5e5',
      300: '#d4d4d4',
      400: '#a3a3a3',
      500: '#737373',
      600: '#525252',
      700: '#404040',
      800: '#262626',
      900: '#171717',
    },
    
    // System Colors
    system: {
      red: '#ff3b30',
      orange: '#ff9500',
      yellow: '#ffcc00',
      green: '#34c759',
      mint: '#00c7be',
      teal: '#30b0c7',
      cyan: '#32ade6',
      blue: '#007aff',
      indigo: '#5856d6',
      purple: '#af52de',
      pink: '#ff2d92',
    },
    
    // Surfaces
    surface: {
      primary: '#ffffff',
      secondary: '#f8f9fa',
      tertiary: '#f1f3f4',
      elevated: '#ffffff',
      overlay: 'rgba(0, 0, 0, 0.4)',
    },
    
    // Text
    text: {
      primary: '#1d1d1f',
      secondary: '#86868b',
      tertiary: '#a1a1a6',
      inverse: '#ffffff',
      accent: '#007aff',
    },
    
    // Borders
    border: {
      light: '#e5e5e7',
      medium: '#d2d2d7',
      heavy: '#a1a1a6',
    }
  },
  
  // Typography - San Francisco inspired
  typography: {
    fontFamily: {
      primary: '-apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", Arial, sans-serif',
      mono: 'SF Mono, Monaco, "Cascadia Code", "Roboto Mono", Consolas, "Courier New", monospace',
    },
    
    fontSize: {
      xs: '0.75rem',      // 12px
      sm: '0.875rem',     // 14px  
      base: '1rem',       // 16px
      lg: '1.125rem',     // 18px
      xl: '1.25rem',      // 20px
      '2xl': '1.5rem',    // 24px
      '3xl': '1.875rem',  // 30px
      '4xl': '2.25rem',   // 36px
      '5xl': '3rem',      // 48px
    },
    
    fontWeight: {
      light: 300,
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
      heavy: 800,
    },
    
    lineHeight: {
      tight: 1.25,
      normal: 1.5,
      relaxed: 1.75,
    },
  },
  
  // Spacing - Apple's 8pt grid system
  spacing: {
    0: '0',
    1: '0.25rem',   // 4px
    2: '0.5rem',    // 8px
    3: '0.75rem',   // 12px
    4: '1rem',      // 16px
    5: '1.25rem',   // 20px
    6: '1.5rem',    // 24px
    8: '2rem',      // 32px
    10: '2.5rem',   // 40px
    12: '3rem',     // 48px
    16: '4rem',     // 64px
    20: '5rem',     // 80px
    24: '6rem',     // 96px
  },
  
  // Border Radius - Apple's consistent curves
  borderRadius: {
    none: '0',
    sm: '0.375rem',    // 6px
    base: '0.5rem',    // 8px
    md: '0.75rem',     // 12px
    lg: '1rem',        // 16px
    xl: '1.5rem',      // 24px
    '2xl': '2rem',     // 32px
    full: '9999px',
  },
  
  // Shadows - Apple's subtle depth
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    base: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    floating: '0 8px 32px rgba(0, 0, 0, 0.12)',
  },
  
  // Animation - Apple's fluid motion
  animation: {
    duration: {
      fast: '150ms',
      normal: '300ms',
      slow: '500ms',
    },
    easing: {
      default: 'ease-out',
      in: 'ease-in',
      out: 'ease-out',
      inOut: 'ease-in-out',
      spring: 'ease-out',
    },
    // For Framer Motion (array format)
    framerEasing: {
      default: [0.4, 0.0, 0.2, 1],
      in: [0.4, 0.0, 1, 1],
      out: [0.0, 0.0, 0.2, 1],
      inOut: [0.4, 0.0, 0.2, 1],
      spring: [0.175, 0.885, 0.32, 1.275],
    },
  },
  
  // Breakpoints
  breakpoints: {
    sm: '640px',
    md: '768px', 
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  },
  
  // Z-index scale
  zIndex: {
    dropdown: 1000,
    sticky: 1020,
    fixed: 1030,
    modal: 1040,
    popover: 1050,
    tooltip: 1060,
  }
};

// Utility functions for theme access
export const getColor = (colorPath) => {
  const keys = colorPath.split('.');
  let value = theme.colors;
  
  for (const key of keys) {
    value = value[key];
    if (!value) return null;
  }
  
  return value;
};

export const getSpacing = (size) => theme.spacing[size] || size;
export const getBorderRadius = (size) => theme.borderRadius[size] || size;
export const getShadow = (size) => theme.shadows[size] || 'none';