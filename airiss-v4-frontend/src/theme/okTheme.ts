import { createTheme } from '@mui/material/styles';

// OK금융그룹 색상 팔레트 - EHR 시스템과 통일
const okColors = {
  primary: '#FF6B00',      // OK 메인 오렌지 (EHR과 동일)
  primaryHover: '#E55A00', // 호버 상태
  primaryLight: '#FFF4ED', // 밝은 오렌지
  secondary: '#55474A',    // OK 브라운
  warning: '#FFAA00',      // OK 액센트 옐로우
  grey: '#E3DFDA',         // OK 브랜드 그레이
  white: '#FFFFFF',
  black: '#1A1A1A',        // 브랜드 다크
  darkGrey: '#6B7280',     // 텍스트 그레이
  lightGrey: '#F9FAFB',    // 배경 그레이
  success: '#10B981',      // 성공 (EHR과 동일)
  error: '#EF4444',        // 에러 (EHR과 동일)
  info: '#FF6B00',         // 정보 (오렌지로 통일)
};

const theme = createTheme({
  palette: {
    primary: {
      main: okColors.primary,
      light: okColors.primaryLight,
      dark: okColors.primaryHover,
      contrastText: okColors.white,
    },
    secondary: {
      main: okColors.secondary,
      light: '#7A6D70',
      dark: '#3A2D30',
      contrastText: okColors.white,
    },
    warning: {
      main: okColors.warning,
      light: '#FFF8E6',
      dark: '#E69900',
      contrastText: okColors.black,
    },
    error: {
      main: okColors.error,
    },
    success: {
      main: okColors.success,
    },
    info: {
      main: okColors.info,
    },
    grey: {
      50: okColors.lightGrey,
      100: '#F3F4F6',
      200: '#E5E7EB',
      300: '#D1D5DB',
      400: '#9CA3AF',
      500: okColors.darkGrey,
      600: '#4B5563',
      700: '#374151',
      800: '#1F2937',
      900: okColors.black,
    },
    background: {
      default: '#F9FAFB',
      paper: okColors.white,
    },
  },
  typography: {
    fontFamily: "'Pretendard', 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif",
    h1: {
      fontWeight: 700,
      fontSize: '2.25rem',
      letterSpacing: '-0.02em',
      color: okColors.black,
    },
    h2: {
      fontWeight: 700,
      fontSize: '1.875rem',
      letterSpacing: '-0.01em',
      color: okColors.black,
    },
    h3: {
      fontWeight: 600,
      fontSize: '1.5rem',
      letterSpacing: '-0.01em',
      color: okColors.black,
    },
    h4: {
      fontWeight: 600,
      fontSize: '1.25rem',
      letterSpacing: '-0.01em',
      color: okColors.black,
    },
    h5: {
      fontWeight: 500,
      fontSize: '1.125rem',
      color: okColors.black,
    },
    h6: {
      fontWeight: 500,
      fontSize: '1rem',
      color: okColors.black,
    },
    subtitle1: {
      fontWeight: 500,
      fontSize: '1rem',
      lineHeight: 1.6,
      color: okColors.darkGrey,
    },
    subtitle2: {
      fontWeight: 500,
      fontSize: '0.875rem',
      lineHeight: 1.57,
      color: okColors.darkGrey,
    },
    body1: {
      fontWeight: 400,
      fontSize: '1rem',
      lineHeight: 1.6,
      color: okColors.darkGrey,
    },
    body2: {
      fontWeight: 400,
      fontSize: '0.875rem',
      lineHeight: 1.5,
      color: okColors.darkGrey,
    },
    button: {
      fontWeight: 600,
      fontSize: '0.875rem',
      letterSpacing: '0.02em',
      textTransform: 'none',
    },
    caption: {
      fontWeight: 400,
      fontSize: '0.75rem',
      lineHeight: 1.66,
      color: okColors.darkGrey,
    },
    overline: {
      fontWeight: 600,
      fontSize: '0.75rem',
      letterSpacing: '0.08em',
      textTransform: 'uppercase',
      color: okColors.darkGrey,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          padding: '12px 24px',
          fontWeight: 600,
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          textTransform: 'none',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 8px 24px rgba(255, 107, 0, 0.2)',
          },
        },
        contained: {
          background: 'linear-gradient(135deg, #FF6B00 0%, #FFAA00 100%)',
          boxShadow: '0 4px 16px rgba(255, 107, 0, 0.2)',
          '&:hover': {
            background: 'linear-gradient(135deg, #E55A00 0%, #E69900 100%)',
          },
        },
        outlined: {
          borderColor: okColors.primary,
          color: okColors.primary,
          '&:hover': {
            borderColor: okColors.primaryHover,
            backgroundColor: okColors.primaryLight,
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0 4px 24px rgba(0, 0, 0, 0.06)',
          border: '1px solid rgba(0, 0, 0, 0.05)',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            boxShadow: '0 12px 32px rgba(255, 107, 0, 0.08)',
            transform: 'translateY(-4px)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0 4px 24px rgba(0, 0, 0, 0.06)',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
          backgroundColor: okColors.white,
          color: okColors.black,
          backdropFilter: 'blur(10px)',
          background: 'rgba(255, 255, 255, 0.95)',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 500,
          borderRadius: 8,
        },
        colorPrimary: {
          backgroundColor: okColors.primaryLight,
          color: okColors.primary,
        },
      },
    },
    MuiTypography: {
      styleOverrides: {
        root: {
          fontFamily: "'Pretendard', 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif",
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 12,
            '&:hover fieldset': {
              borderColor: okColors.primary,
            },
            '&.Mui-focused fieldset': {
              borderColor: okColors.primary,
              borderWidth: 2,
            },
          },
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          padding: '16px',
          borderBottom: `1px solid ${okColors.grey}40`,
        },
        head: {
          fontWeight: 600,
          backgroundColor: okColors.lightGrey,
          color: okColors.black,
        },
      },
    },
  },
});

export default theme;