/**
 * Reusable ConnectionStatus component
 * Displays connection status with animated indicator
 * 
 * Usage:
 * <ConnectionStatus service="TikTok" connected={true} />
 */

import React from 'react';
import { Box, Typography } from '@mui/material';
import {
  CheckCircle as ConnectedIcon,
  Cancel as DisconnectedIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';

/**
 * ConnectionStatus Component
 * 
 * @param {Object} props
 * @param {string} props.service - Service name key for translation (e.g., 'tiktok', 'animaze', 'microphone')
 * @param {boolean} props.connected - Whether the service is connected
 * @param {Object} [props.sx] - Additional MUI sx styles
 */
function ConnectionStatus({ service, connected, sx = {}, ...props }) {
  const { t } = useTranslation();
  
  return (
    <Box 
      sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: 1.5, 
        mb: 1.5,
        ...sx 
      }} 
      {...props}
    >
      <motion.div
        animate={{ 
          scale: connected ? [1, 1.15, 1] : 1,
          opacity: connected ? 1 : 0.7,
        }}
        transition={{ 
          repeat: connected ? Infinity : 0, 
          duration: 2,
          ease: 'easeInOut',
        }}
      >
        {connected ? (
          <ConnectedIcon color="success" sx={{ fontSize: 24 }} />
        ) : (
          <DisconnectedIcon color="error" sx={{ fontSize: 24 }} />
        )}
      </motion.div>
      <Typography variant="body1">
        {t(service)}:{' '}
        <Typography 
          component="span" 
          fontWeight={600}
          color={connected ? 'success.main' : 'error.main'}
        >
          {t(connected ? 'connected' : 'disconnected')}
        </Typography>
      </Typography>
    </Box>
  );
}

export default ConnectionStatus;
