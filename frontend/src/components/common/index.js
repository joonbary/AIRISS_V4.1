/**
 * AIRISS Common Component Library
 * 재사용 가능한 공통 컴포넌트 모음
 */

import React from 'react';
import {
  Card as MuiCard,
  CardContent,
  CardHeader,
  CardActions,
  Button,
  IconButton,
  Typography,
  Box,
  LinearProgress,
  Chip,
  Avatar,
  Skeleton,
  Fade,
  Grow,
  Zoom,
  Badge,
  Tooltip,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { getGradeColor, getStatusColor } from '../../theme';

// ==================== Styled Components ====================

// 그라데이션 카드
export const GradientCard = styled(MuiCard)(({ theme, gradient }) => ({
  background: gradient || `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
  color: '#FFFFFF',
  position: 'relative',
  overflow: 'hidden',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(255, 255, 255, 0.1)',
    transform: 'translateX(-100%)',
    transition: 'transform 0.6s ease',
  },
  '&:hover::before': {
    transform: 'translateX(100%)',
  },
}));

// 유리 효과 카드
export const GlassCard = styled(MuiCard)(({ theme }) => ({
  background: 'rgba(255, 255, 255, 0.95)',
  backdropFilter: 'blur(10px)',
  border: '1px solid rgba(255, 255, 255, 0.2)',
  boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.15)',
  ...(theme.palette.mode === 'dark' && {
    background: 'rgba(30, 30, 30, 0.95)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
  }),
}));

// 애니메이션 버튼
export const AnimatedButton = styled(Button)(({ theme }) => ({
  position: 'relative',
  overflow: 'hidden',
  transition: 'all 0.3s ease',
  '&::after': {
    content: '""',
    position: 'absolute',
    top: '50%',
    left: '50%',
    width: 0,
    height: 0,
    borderRadius: '50%',
    background: 'rgba(255, 255, 255, 0.5)',
    transform: 'translate(-50%, -50%)',
    transition: 'width 0.6s ease, height 0.6s ease',
  },
  '&:active::after': {
    width: '300px',
    height: '300px',
  },
}));

// ==================== 데이터 카드 컴포넌트 ====================

export const DataCard = ({ 
  title, 
  subtitle, 
  value, 
  unit, 
  icon, 
  color = 'primary',
  trend,
  loading = false,
  onClick,
  ...props 
}) => {
  return (
    <GlassCard 
      sx={{ 
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.3s ease',
        '&:hover': onClick ? {
          transform: 'translateY(-4px)',
          boxShadow: '0 12px 40px rgba(0, 0, 0, 0.15)',
        } : {},
      }}
      onClick={onClick}
      {...props}
    >
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
          <Box flex={1}>
            <Typography color="textSecondary" gutterBottom variant="caption">
              {subtitle}
            </Typography>
            <Typography variant="h5" component="h2" fontWeight="bold">
              {loading ? <Skeleton width={100} /> : title}
            </Typography>
            <Box display="flex" alignItems="baseline" gap={1} mt={2}>
              {loading ? (
                <Skeleton width={150} height={40} />
              ) : (
                <>
                  <Typography variant="h3" component="span" color={color}>
                    {value}
                  </Typography>
                  {unit && (
                    <Typography variant="body1" color="textSecondary">
                      {unit}
                    </Typography>
                  )}
                </>
              )}
            </Box>
            {trend && (
              <Box display="flex" alignItems="center" gap={0.5} mt={1}>
                <Chip
                  label={trend.label}
                  size="small"
                  color={trend.type === 'up' ? 'success' : 'error'}
                  icon={trend.icon}
                />
              </Box>
            )}
          </Box>
          {icon && (
            <Box>
              <Avatar
                sx={{
                  bgcolor: `${color}.light`,
                  color: `${color}.main`,
                  width: 56,
                  height: 56,
                }}
              >
                {icon}
              </Avatar>
            </Box>
          )}
        </Box>
      </CardContent>
    </GlassCard>
  );
};

// ==================== 진행률 카드 컴포넌트 ====================

export const ProgressCard = ({
  title,
  value,
  total,
  percentage,
  color = 'primary',
  showLabel = true,
  animated = true,
  thickness = 8,
  ...props
}) => {
  const actualPercentage = percentage || (value / total) * 100;
  
  return (
    <Card {...props}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">{title}</Typography>
          {showLabel && (
            <Typography variant="h6" color={color}>
              {actualPercentage.toFixed(1)}%
            </Typography>
          )}
        </Box>
        <LinearProgress
          variant={animated ? "indeterminate" : "determinate"}
          value={actualPercentage}
          color={color}
          sx={{
            height: thickness,
            borderRadius: thickness / 2,
            backgroundColor: (theme) => 
              theme.palette.mode === 'light' 
                ? theme.palette.grey[200] 
                : theme.palette.grey[800],
          }}
        />
        {value !== undefined && total !== undefined && (
          <Box display="flex" justifyContent="space-between" mt={1}>
            <Typography variant="caption" color="textSecondary">
              {value} / {total}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

// ==================== 상태 배지 컴포넌트 ====================

export const StatusBadge = ({ status, size = 'medium', showLabel = true, ...props }) => {
  const statusConfig = {
    online: { color: 'success', label: '온라인' },
    offline: { color: 'error', label: '오프라인' },
    busy: { color: 'warning', label: '사용 중' },
    away: { color: 'default', label: '자리 비움' },
  };

  const config = statusConfig[status] || statusConfig.offline;

  return (
    <Badge
      overlap="circular"
      anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      variant="dot"
      sx={{
        '& .MuiBadge-badge': {
          backgroundColor: (theme) => theme.palette[config.color].main,
          color: (theme) => theme.palette[config.color].main,
          boxShadow: (theme) => `0 0 0 2px ${theme.palette.background.paper}`,
          width: size === 'small' ? 8 : size === 'large' ? 16 : 12,
          height: size === 'small' ? 8 : size === 'large' ? 16 : 12,
          borderRadius: '50%',
          '&::after': {
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            borderRadius: '50%',
            animation: status === 'online' ? 'ripple 1.2s infinite ease-in-out' : 'none',
            border: '1px solid currentColor',
            content: '""',
          },
        },
        '@keyframes ripple': {
          '0%': {
            transform: 'scale(.8)',
            opacity: 1,
          },
          '100%': {
            transform: 'scale(2.4)',
            opacity: 0,
          },
        },
      }}
      {...props}
    >
      {showLabel && (
        <Chip label={config.label} size="small" color={config.color} />
      )}
    </Badge>
  );
};

// ==================== 등급 표시 컴포넌트 ====================

export const GradeBadge = ({ grade, size = 'medium', variant = 'filled' }) => {
  const color = getGradeColor(grade);
  
  const sizeMap = {
    small: { width: 24, height: 24, fontSize: '0.75rem' },
    medium: { width: 32, height: 32, fontSize: '0.875rem' },
    large: { width: 40, height: 40, fontSize: '1rem' },
  };

  return (
    <Avatar
      sx={{
        ...sizeMap[size],
        backgroundColor: variant === 'filled' ? color : 'transparent',
        color: variant === 'filled' ? '#FFFFFF' : color,
        border: variant === 'outlined' ? `2px solid ${color}` : 'none',
        fontWeight: 'bold',
      }}
    >
      {grade}
    </Avatar>
  );
};

// ==================== 스켈레톤 카드 컴포넌트 ====================

export const SkeletonCard = ({ lines = 3, showAvatar = false, showActions = false }) => {
  return (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" gap={2} mb={2}>
          {showAvatar && <Skeleton variant="circular" width={40} height={40} />}
          <Box flex={1}>
            <Skeleton variant="text" width="60%" />
            <Skeleton variant="text" width="40%" />
          </Box>
        </Box>
        {Array.from({ length: lines }).map((_, index) => (
          <Skeleton key={index} variant="text" width={`${90 - index * 10}%`} />
        ))}
      </CardContent>
      {showActions && (
        <CardActions>
          <Skeleton variant="rectangular" width={80} height={36} />
          <Skeleton variant="rectangular" width={80} height={36} />
        </CardActions>
      )}
    </Card>
  );
};

// ==================== 애니메이션 래퍼 컴포넌트 ====================

export const AnimatedContainer = ({ 
  children, 
  animation = 'fade', 
  delay = 0, 
  duration = 300,
  ...props 
}) => {
  const animationComponents = {
    fade: Fade,
    grow: Grow,
    zoom: Zoom,
  };

  const AnimationComponent = animationComponents[animation] || Fade;

  return (
    <AnimationComponent
      in={true}
      timeout={{ enter: duration, exit: duration }}
      style={{ transitionDelay: `${delay}ms` }}
      {...props}
    >
      <div>{children}</div>
    </AnimationComponent>
  );
};

// ==================== 메트릭 카드 컴포넌트 ====================

export const MetricCard = ({
  title,
  metrics = [],
  loading = false,
  ...props
}) => {
  return (
    <Card {...props}>
      <CardHeader title={title} />
      <CardContent>
        <Box display="grid" gridTemplateColumns="repeat(auto-fit, minmax(150px, 1fr))" gap={2}>
          {loading ? (
            Array.from({ length: 4 }).map((_, index) => (
              <Box key={index}>
                <Skeleton variant="text" width="80%" />
                <Skeleton variant="rectangular" height={40} />
              </Box>
            ))
          ) : (
            metrics.map((metric, index) => (
              <Box key={index}>
                <Typography variant="caption" color="textSecondary" gutterBottom>
                  {metric.label}
                </Typography>
                <Typography variant="h6" color={metric.color || 'textPrimary'}>
                  {metric.value}
                </Typography>
                {metric.change && (
                  <Typography
                    variant="caption"
                    sx={{
                      color: metric.change > 0 ? 'success.main' : 'error.main',
                    }}
                  >
                    {metric.change > 0 ? '+' : ''}{metric.change}%
                  </Typography>
                )}
              </Box>
            ))
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

// 모든 컴포넌트 내보내기
export default {
  GradientCard,
  GlassCard,
  AnimatedButton,
  DataCard,
  ProgressCard,
  StatusBadge,
  GradeBadge,
  SkeletonCard,
  AnimatedContainer,
  MetricCard,
};