/**
 * Reusable StatusChip component
 * Displays status information with color-coded chips
 * 
 * Usage:
 * <StatusChip status="online" label="Connected" />
 * <StatusChip status="offline" label="Disconnected" />
 */

import React from 'react';
import { Chip } from '@mui/material';
import { colors } from '../../theme/colors';

/**
 * Status color mapping
 */
const statusColors = {
  online: {
    backgroundColor: colors.success.main,
    color: colors.success.contrastText,
  },
  offline: {
    backgroundColor: colors.error.main,
    color: colors.error.contrastText,
  },
  connecting: {
    backgroundColor: colors.warning.main,
    color: colors.warning.contrastText,
  },
  idle: {
    backgroundColor: colors.grey[500],
    color: '#ffffff',
  },
  running: {
    backgroundColor: colors.success.main,
    color: colors.success.contrastText,
  },
  stopped: {
    backgroundColor: colors.grey[600],
    color: '#ffffff',
  },
  error: {
    backgroundColor: colors.error.main,
    color: colors.error.contrastText,
  },
  warning: {
    backgroundColor: colors.warning.main,
    color: colors.warning.contrastText,
  },
  info: {
    backgroundColor: colors.info.main,
    color: colors.info.contrastText,
  },
  success: {
    backgroundColor: colors.success.main,
    color: colors.success.contrastText,
  },
};

/**
 * StatusChip Component
 * 
 * @param {Object} props
 * @param {string} props.status - Status type (online, offline, connecting, idle, etc.)
 * @param {string} props.label - Label text to display
 * @param {string} [props.size='small'] - Chip size (small, medium)
 * @param {Object} [props.sx] - Additional MUI sx styles
 */
function StatusChip({ status, label, size = 'small', sx = {}, ...props }) {
  const colorStyle = statusColors[status] || statusColors.idle;
  
  return (
    <Chip
      label={label}
      size={size}
      sx={{
        ...colorStyle,
        fontWeight: 600,
        ...sx,
      }}
      {...props}
    />
  );
}

export default StatusChip;
