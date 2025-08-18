/**
 * AIRISS Design Tokens
 * 디자인 시스템 토큰 정의 - 모든 UI 요소의 기본 값
 */

// ==================== 색상 토큰 ====================
export const colors = {
  // Primary Palette
  primary: {
    50: '#FFF3E0',
    100: '#FFE0B2',
    200: '#FFCC80',
    300: '#FFB74D',
    400: '#FFA726',
    500: '#FF5722', // Main
    600: '#FB4C1F',
    700: '#E64A19',
    800: '#D84315',
    900: '#BF360C',
  },
  
  // Secondary Palette
  secondary: {
    50: '#FFF8E1',
    100: '#FFECB3',
    200: '#FFE082',
    300: '#FFD54F',
    400: '#FFCA28',
    500: '#F89C26', // Main
    600: '#FFB300',
    700: '#FFA000',
    800: '#FF8F00',
    900: '#FF6F00',
  },
  
  // Success
  success: {
    50: '#E8F5E9',
    100: '#C8E6C9',
    200: '#A5D6A7',
    300: '#81C784',
    400: '#66BB6A',
    500: '#4CAF50', // Main
    600: '#43A047',
    700: '#388E3C',
    800: '#2E7D32',
    900: '#1B5E20',
  },
  
  // Warning
  warning: {
    50: '#FFF3E0',
    100: '#FFE0B2',
    200: '#FFCC80',
    300: '#FFB74D',
    400: '#FFA726',
    500: '#FF9800', // Main
    600: '#FB8C00',
    700: '#F57C00',
    800: '#EF6C00',
    900: '#E65100',
  },
  
  // Error
  error: {
    50: '#FFEBEE',
    100: '#FFCDD2',
    200: '#EF9A9A',
    300: '#E57373',
    400: '#EF5350',
    500: '#F44336', // Main
    600: '#E53935',
    700: '#D32F2F',
    800: '#C62828',
    900: '#B71C1C',
  },
  
  // Info
  info: {
    50: '#E3F2FD',
    100: '#BBDEFB',
    200: '#90CAF9',
    300: '#64B5F6',
    400: '#42A5F5',
    500: '#2196F3', // Main
    600: '#1E88E5',
    700: '#1976D2',
    800: '#1565C0',
    900: '#0D47A1',
  },
  
  // Neutral
  neutral: {
    0: '#FFFFFF',
    50: '#FAFAFA',
    100: '#F5F5F5',
    200: '#EEEEEE',
    300: '#E0E0E0',
    400: '#BDBDBD',
    500: '#9E9E9E',
    600: '#757575',
    700: '#616161',
    800: '#424242',
    900: '#212121',
    1000: '#000000',
  },
  
  // Semantic Colors
  semantic: {
    background: '#F5F5F5',
    surface: '#FFFFFF',
    textPrimary: '#333333',
    textSecondary: '#666666',
    textDisabled: '#999999',
    divider: '#E0E0E0',
    overlay: 'rgba(0, 0, 0, 0.5)',
  },
  
  // Grade Colors
  grades: {
    S: '#4CAF50',
    'A+': '#8BC34A',
    A: '#CDDC39',
    B: '#FFC107',
    C: '#FF9800',
    D: '#F44336',
  },
  
  // Status Colors
  status: {
    active: '#4CAF50',
    inactive: '#9E9E9E',
    pending: '#FF9800',
    error: '#F44336',
    warning: '#FFC107',
    info: '#2196F3',
  },
};

// ==================== 타이포그래피 토큰 ====================
export const typography = {
  // Font Families
  fontFamily: {
    primary: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans KR", sans-serif',
    secondary: '"Roboto Mono", "Courier New", monospace',
    display: '"Poppins", "Noto Sans KR", sans-serif',
  },
  
  // Font Sizes
  fontSize: {
    xs: '0.75rem',    // 12px
    sm: '0.875rem',   // 14px
    base: '1rem',     // 16px
    lg: '1.125rem',   // 18px
    xl: '1.25rem',    // 20px
    '2xl': '1.5rem',  // 24px
    '3xl': '1.875rem', // 30px
    '4xl': '2.25rem', // 36px
    '5xl': '3rem',    // 48px
    '6xl': '3.75rem', // 60px
  },
  
  // Font Weights
  fontWeight: {
    thin: 100,
    light: 300,
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
    extrabold: 800,
    black: 900,
  },
  
  // Line Heights
  lineHeight: {
    none: 1,
    tight: 1.25,
    snug: 1.375,
    normal: 1.5,
    relaxed: 1.625,
    loose: 2,
  },
  
  // Letter Spacing
  letterSpacing: {
    tighter: '-0.05em',
    tight: '-0.025em',
    normal: '0',
    wide: '0.025em',
    wider: '0.05em',
    widest: '0.1em',
  },
};

// ==================== 간격 토큰 ====================
export const spacing = {
  0: '0',
  1: '0.25rem',  // 4px
  2: '0.5rem',   // 8px
  3: '0.75rem',  // 12px
  4: '1rem',     // 16px
  5: '1.25rem',  // 20px
  6: '1.5rem',   // 24px
  8: '2rem',     // 32px
  10: '2.5rem',  // 40px
  12: '3rem',    // 48px
  16: '4rem',    // 64px
  20: '5rem',    // 80px
  24: '6rem',    // 96px
  32: '8rem',    // 128px
  40: '10rem',   // 160px
  48: '12rem',   // 192px
  56: '14rem',   // 224px
  64: '16rem',   // 256px
};

// ==================== 크기 토큰 ====================
export const sizes = {
  // Container Sizes
  container: {
    xs: '480px',
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
    full: '100%',
  },
  
  // Component Sizes
  button: {
    sm: { height: '32px', padding: '0 12px', fontSize: '0.875rem' },
    md: { height: '40px', padding: '0 16px', fontSize: '1rem' },
    lg: { height: '48px', padding: '0 24px', fontSize: '1.125rem' },
  },
  
  input: {
    sm: { height: '32px', padding: '8px 12px', fontSize: '0.875rem' },
    md: { height: '40px', padding: '10px 16px', fontSize: '1rem' },
    lg: { height: '48px', padding: '12px 20px', fontSize: '1.125rem' },
  },
  
  icon: {
    xs: '16px',
    sm: '20px',
    md: '24px',
    lg: '32px',
    xl: '40px',
  },
};

// ==================== 테두리 토큰 ====================
export const borders = {
  // Border Widths
  width: {
    0: '0',
    1: '1px',
    2: '2px',
    4: '4px',
    8: '8px',
  },
  
  // Border Radius
  radius: {
    none: '0',
    sm: '4px',
    md: '8px',
    lg: '12px',
    xl: '16px',
    '2xl': '24px',
    full: '9999px',
  },
  
  // Border Styles
  style: {
    solid: 'solid',
    dashed: 'dashed',
    dotted: 'dotted',
    double: 'double',
    none: 'none',
  },
};

// ==================== 그림자 토큰 ====================
export const shadows = {
  none: 'none',
  xs: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  sm: '0 2px 4px 0 rgba(0, 0, 0, 0.06)',
  md: '0 4px 8px 0 rgba(0, 0, 0, 0.08)',
  lg: '0 8px 16px 0 rgba(0, 0, 0, 0.10)',
  xl: '0 12px 24px 0 rgba(0, 0, 0, 0.12)',
  '2xl': '0 16px 32px 0 rgba(0, 0, 0, 0.14)',
  '3xl': '0 24px 48px 0 rgba(0, 0, 0, 0.16)',
  inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
  
  // Colored Shadows
  primary: '0 4px 14px 0 rgba(255, 87, 34, 0.39)',
  secondary: '0 4px 14px 0 rgba(248, 156, 38, 0.39)',
  success: '0 4px 14px 0 rgba(76, 175, 80, 0.39)',
  warning: '0 4px 14px 0 rgba(255, 152, 0, 0.39)',
  error: '0 4px 14px 0 rgba(244, 67, 54, 0.39)',
  
  // Elevation Shadows (Material Design)
  elevation: {
    0: 'none',
    1: '0px 2px 1px -1px rgba(0,0,0,0.2), 0px 1px 1px 0px rgba(0,0,0,0.14), 0px 1px 3px 0px rgba(0,0,0,0.12)',
    2: '0px 3px 1px -2px rgba(0,0,0,0.2), 0px 2px 2px 0px rgba(0,0,0,0.14), 0px 1px 5px 0px rgba(0,0,0,0.12)',
    3: '0px 3px 3px -2px rgba(0,0,0,0.2), 0px 3px 4px 0px rgba(0,0,0,0.14), 0px 1px 8px 0px rgba(0,0,0,0.12)',
    4: '0px 2px 4px -1px rgba(0,0,0,0.2), 0px 4px 5px 0px rgba(0,0,0,0.14), 0px 1px 10px 0px rgba(0,0,0,0.12)',
    6: '0px 3px 5px -1px rgba(0,0,0,0.2), 0px 6px 10px 0px rgba(0,0,0,0.14), 0px 1px 18px 0px rgba(0,0,0,0.12)',
    8: '0px 5px 5px -3px rgba(0,0,0,0.2), 0px 8px 10px 1px rgba(0,0,0,0.14), 0px 3px 14px 2px rgba(0,0,0,0.12)',
    12: '0px 7px 8px -4px rgba(0,0,0,0.2), 0px 12px 17px 2px rgba(0,0,0,0.14), 0px 5px 22px 4px rgba(0,0,0,0.12)',
    16: '0px 8px 10px -5px rgba(0,0,0,0.2), 0px 16px 24px 2px rgba(0,0,0,0.14), 0px 6px 30px 5px rgba(0,0,0,0.12)',
    24: '0px 11px 15px -7px rgba(0,0,0,0.2), 0px 24px 38px 3px rgba(0,0,0,0.14), 0px 9px 46px 8px rgba(0,0,0,0.12)',
  },
};

// ==================== 애니메이션 토큰 ====================
export const animation = {
  // Duration
  duration: {
    instant: '0ms',
    fast: '150ms',
    normal: '300ms',
    slow: '500ms',
    slower: '700ms',
    slowest: '1000ms',
  },
  
  // Easing
  easing: {
    linear: 'linear',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
  },
  
  // Transitions
  transition: {
    all: 'all 300ms cubic-bezier(0.4, 0, 0.2, 1)',
    colors: 'background-color 300ms, border-color 300ms, color 300ms, fill 300ms, stroke 300ms',
    opacity: 'opacity 300ms cubic-bezier(0.4, 0, 0.2, 1)',
    shadow: 'box-shadow 300ms cubic-bezier(0.4, 0, 0.2, 1)',
    transform: 'transform 300ms cubic-bezier(0.4, 0, 0.2, 1)',
  },
};

// ==================== 브레이크포인트 토큰 ====================
export const breakpoints = {
  xs: '0px',
  sm: '600px',
  md: '960px',
  lg: '1280px',
  xl: '1920px',
};

// ==================== Z-Index 토큰 ====================
export const zIndex = {
  dropdown: 1000,
  sticky: 1020,
  fixed: 1030,
  modalBackdrop: 1040,
  modal: 1050,
  popover: 1060,
  tooltip: 1070,
  notification: 1080,
};

// ==================== 유틸리티 함수 ====================

// 색상 투명도 조절
export const alpha = (color, opacity) => {
  if (color.startsWith('#')) {
    const r = parseInt(color.slice(1, 3), 16);
    const g = parseInt(color.slice(3, 5), 16);
    const b = parseInt(color.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${opacity})`;
  }
  return color;
};

// 반응형 값 생성
export const responsive = (values) => {
  const { xs, sm, md, lg, xl } = values;
  return {
    '@media (min-width: 0px)': xs,
    '@media (min-width: 600px)': sm,
    '@media (min-width: 960px)': md,
    '@media (min-width: 1280px)': lg,
    '@media (min-width: 1920px)': xl,
  };
};

// 기본 내보내기
export default {
  colors,
  typography,
  spacing,
  sizes,
  borders,
  shadows,
  animation,
  breakpoints,
  zIndex,
  alpha,
  responsive,
};