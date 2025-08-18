/**
 * AIRISS Material-UI Theme Configuration
 * 통합 디자인 시스템 및 테마 설정
 * Version: 4.0
 */

import { createTheme } from '@mui/material/styles';

// 색상 팔레트 정의
const colors = {
  primary: {
    main: '#FF5722',
    light: '#FF8A65',
    dark: '#E64A19',
    contrastText: '#FFFFFF',
  },
  secondary: {
    main: '#F89C26',
    light: '#FFB74D',
    dark: '#F57C00',
    contrastText: '#FFFFFF',
  },
  success: {
    main: '#4CAF50',
    light: '#81C784',
    dark: '#388E3C',
    contrastText: '#FFFFFF',
  },
  warning: {
    main: '#FF9800',
    light: '#FFB74D',
    dark: '#F57C00',
    contrastText: '#FFFFFF',
  },
  error: {
    main: '#F44336',
    light: '#E57373',
    dark: '#D32F2F',
    contrastText: '#FFFFFF',
  },
  info: {
    main: '#2196F3',
    light: '#64B5F6',
    dark: '#1976D2',
    contrastText: '#FFFFFF',
  },
  // 등급별 색상
  grades: {
    S: '#4CAF50',
    'A+': '#8BC34A',
    A: '#CDDC39',
    B: '#FFC107',
    C: '#FF9800',
    D: '#F44336',
  },
  // 배경 색상
  background: {
    default: '#F5F5F5',
    paper: '#FFFFFF',
    dark: '#1A1A1A',
    gradient: 'linear-gradient(135deg, #FF5722 0%, #F89C26 100%)',
  },
  // 텍스트 색상
  text: {
    primary: '#333333',
    secondary: '#666666',
    disabled: '#999999',
    hint: '#BBBBBB',
  },
};

// 타이포그래피 설정
const typography = {
  fontFamily: [
    '-apple-system',
    'BlinkMacSystemFont',
    '"Segoe UI"',
    'Roboto',
    '"Noto Sans KR"',
    'sans-serif',
  ].join(','),
  h1: {
    fontSize: '2.5rem',
    fontWeight: 700,
    lineHeight: 1.2,
    letterSpacing: '-0.02em',
  },
  h2: {
    fontSize: '2rem',
    fontWeight: 600,
    lineHeight: 1.3,
    letterSpacing: '-0.01em',
  },
  h3: {
    fontSize: '1.75rem',
    fontWeight: 600,
    lineHeight: 1.4,
  },
  h4: {
    fontSize: '1.5rem',
    fontWeight: 500,
    lineHeight: 1.4,
  },
  h5: {
    fontSize: '1.25rem',
    fontWeight: 500,
    lineHeight: 1.5,
  },
  h6: {
    fontSize: '1rem',
    fontWeight: 500,
    lineHeight: 1.6,
  },
  body1: {
    fontSize: '1rem',
    lineHeight: 1.6,
  },
  body2: {
    fontSize: '0.875rem',
    lineHeight: 1.6,
  },
  button: {
    fontSize: '0.875rem',
    fontWeight: 500,
    letterSpacing: '0.02857em',
    textTransform: 'none',
  },
  caption: {
    fontSize: '0.75rem',
    lineHeight: 1.6,
  },
  overline: {
    fontSize: '0.75rem',
    fontWeight: 500,
    letterSpacing: '0.08333em',
    textTransform: 'uppercase',
  },
};

// 그림자 효과
const shadows = [
  'none',
  '0px 2px 4px rgba(0, 0, 0, 0.05)',
  '0px 3px 6px rgba(0, 0, 0, 0.07)',
  '0px 4px 8px rgba(0, 0, 0, 0.08)',
  '0px 5px 10px rgba(0, 0, 0, 0.09)',
  '0px 6px 12px rgba(0, 0, 0, 0.10)',
  '0px 7px 14px rgba(0, 0, 0, 0.11)',
  '0px 8px 16px rgba(0, 0, 0, 0.12)',
  '0px 9px 18px rgba(0, 0, 0, 0.13)',
  '0px 10px 20px rgba(0, 0, 0, 0.14)',
  '0px 10px 30px rgba(0, 0, 0, 0.15)',
  '0px 12px 35px rgba(0, 0, 0, 0.16)',
  '0px 14px 40px rgba(0, 0, 0, 0.17)',
  '0px 16px 45px rgba(0, 0, 0, 0.18)',
  '0px 18px 50px rgba(0, 0, 0, 0.19)',
  '0px 20px 55px rgba(0, 0, 0, 0.20)',
  '0px 22px 60px rgba(0, 0, 0, 0.21)',
  '0px 24px 65px rgba(0, 0, 0, 0.22)',
  '0px 26px 70px rgba(0, 0, 0, 0.23)',
  '0px 28px 75px rgba(0, 0, 0, 0.24)',
  '0px 30px 80px rgba(0, 0, 0, 0.25)',
  '0px 32px 85px rgba(0, 0, 0, 0.26)',
  '0px 34px 90px rgba(0, 0, 0, 0.27)',
  '0px 36px 95px rgba(0, 0, 0, 0.28)',
  '0px 38px 100px rgba(0, 0, 0, 0.30)',
];

// 컴포넌트 오버라이드
const components = {
  MuiButton: {
    styleOverrides: {
      root: {
        borderRadius: 8,
        padding: '10px 24px',
        fontSize: '0.875rem',
        fontWeight: 500,
        transition: 'all 0.3s ease',
        textTransform: 'none',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: '0 8px 16px rgba(0, 0, 0, 0.15)',
        },
      },
      contained: {
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
      },
      outlined: {
        borderWidth: 2,
        '&:hover': {
          borderWidth: 2,
        },
      },
    },
  },
  MuiCard: {
    styleOverrides: {
      root: {
        borderRadius: 15,
        boxShadow: '0 10px 30px rgba(0, 0, 0, 0.15)',
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-5px)',
          boxShadow: '0 15px 40px rgba(0, 0, 0, 0.2)',
        },
      },
    },
  },
  MuiTextField: {
    styleOverrides: {
      root: {
        '& .MuiOutlinedInput-root': {
          borderRadius: 8,
          '& fieldset': {
            borderColor: '#E0E0E0',
            borderWidth: 2,
          },
          '&:hover fieldset': {
            borderColor: colors.primary.main,
          },
          '&.Mui-focused fieldset': {
            borderColor: colors.primary.main,
            borderWidth: 2,
          },
        },
      },
    },
  },
  MuiChip: {
    styleOverrides: {
      root: {
        borderRadius: 8,
        fontWeight: 500,
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'scale(1.05)',
        },
      },
    },
  },
  MuiPaper: {
    styleOverrides: {
      root: {
        borderRadius: 12,
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
      },
      elevation1: {
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
      },
      elevation2: {
        boxShadow: '0 4px 16px rgba(0, 0, 0, 0.1)',
      },
      elevation3: {
        boxShadow: '0 8px 24px rgba(0, 0, 0, 0.12)',
      },
    },
  },
  MuiTableCell: {
    styleOverrides: {
      root: {
        borderColor: '#F0F0F0',
        padding: '16px',
      },
      head: {
        backgroundColor: '#F8F9FA',
        fontWeight: 600,
        color: colors.text.primary,
      },
    },
  },
  MuiDialog: {
    styleOverrides: {
      paper: {
        borderRadius: 16,
        padding: '8px',
      },
    },
  },
  MuiAlert: {
    styleOverrides: {
      root: {
        borderRadius: 8,
        fontSize: '0.875rem',
      },
      standardSuccess: {
        backgroundColor: '#E8F5E9',
        color: colors.success.dark,
      },
      standardError: {
        backgroundColor: '#FFEBEE',
        color: colors.error.dark,
      },
      standardWarning: {
        backgroundColor: '#FFF3E0',
        color: colors.warning.dark,
      },
      standardInfo: {
        backgroundColor: '#E3F2FD',
        color: colors.info.dark,
      },
    },
  },
  MuiTooltip: {
    styleOverrides: {
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.87)',
        borderRadius: 6,
        fontSize: '0.75rem',
        padding: '8px 12px',
      },
    },
  },
  MuiLinearProgress: {
    styleOverrides: {
      root: {
        borderRadius: 4,
        height: 8,
      },
      bar: {
        borderRadius: 4,
      },
    },
  },
  MuiCircularProgress: {
    styleOverrides: {
      root: {
        color: colors.primary.main,
      },
    },
  },
  MuiDivider: {
    styleOverrides: {
      root: {
        borderColor: '#E0E0E0',
      },
    },
  },
  MuiBackdrop: {
    styleOverrides: {
      root: {
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        backdropFilter: 'blur(4px)',
      },
    },
  },
};

// 반응형 브레이크포인트
const breakpoints = {
  values: {
    xs: 0,
    sm: 600,
    md: 960,
    lg: 1280,
    xl: 1920,
  },
};

// 간격 설정
const spacing = 8;

// 모양 설정
const shape = {
  borderRadius: 8,
};

// 트랜지션 설정
const transitions = {
  easing: {
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    easeOut: 'cubic-bezier(0.0, 0, 0.2, 1)',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    sharp: 'cubic-bezier(0.4, 0, 0.6, 1)',
  },
  duration: {
    shortest: 150,
    shorter: 200,
    short: 250,
    standard: 300,
    complex: 375,
    enteringScreen: 225,
    leavingScreen: 195,
  },
};

// 라이트 테마
export const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: colors.primary,
    secondary: colors.secondary,
    success: colors.success,
    warning: colors.warning,
    error: colors.error,
    info: colors.info,
    background: {
      default: colors.background.default,
      paper: colors.background.paper,
    },
    text: colors.text,
  },
  typography,
  shadows,
  components,
  breakpoints,
  spacing,
  shape,
  transitions,
});

// 다크 테마
export const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: colors.primary,
    secondary: colors.secondary,
    success: colors.success,
    warning: colors.warning,
    error: colors.error,
    info: colors.info,
    background: {
      default: '#121212',
      paper: '#1E1E1E',
    },
    text: {
      primary: '#FFFFFF',
      secondary: '#B0B0B0',
      disabled: '#666666',
      hint: '#808080',
    },
  },
  typography,
  shadows: shadows.map(shadow => 
    shadow === 'none' ? 'none' : shadow.replace(/rgba\(0, 0, 0,/g, 'rgba(0, 0, 0,')
  ),
  components: {
    ...components,
    MuiCard: {
      styleOverrides: {
        root: {
          ...components.MuiCard.styleOverrides.root,
          backgroundColor: '#1E1E1E',
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          borderColor: '#2C2C2C',
        },
        head: {
          backgroundColor: '#252525',
        },
      },
    },
  },
  breakpoints,
  spacing,
  shape,
  transitions,
});

// 커스텀 테마 훅
export const useAIRISSTheme = () => {
  const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const storedTheme = localStorage.getItem('airiss-theme');
  const isDarkMode = storedTheme ? storedTheme === 'dark' : prefersDarkMode;
  
  return isDarkMode ? darkTheme : lightTheme;
};

// 등급 색상 가져오기
export const getGradeColor = (grade) => {
  return colors.grades[grade] || colors.text.secondary;
};

// 상태 색상 가져오기
export const getStatusColor = (status) => {
  const statusColors = {
    active: colors.success.main,
    inactive: colors.text.disabled,
    pending: colors.warning.main,
    error: colors.error.main,
  };
  return statusColors[status] || colors.text.secondary;
};

// 기본 테마 내보내기
export default lightTheme;