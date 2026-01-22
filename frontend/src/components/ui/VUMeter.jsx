/**
 * Reusable VUMeter component
 * Displays audio level with color-coded progress bar and optional chart
 * 
 * Usage:
 * <VUMeter level={0.5} showChart={true} chartData={micHistory} />
 */

import React from 'react';
import { Box, Typography, LinearProgress } from '@mui/material';
import { Mic as MicIcon } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from 'recharts';
import { colors } from '../../theme/colors';

/**
 * Get VU meter color based on level
 * @param {number} level - Level from 0 to 1
 * @returns {string} Color value
 */
const getVUColor = (level) => {
  if (level > 0.7) return colors.vuMeter.high;
  if (level > 0.4) return colors.vuMeter.medium;
  return colors.vuMeter.low;
};

/**
 * VUMeter Component
 * 
 * @param {Object} props
 * @param {number} props.level - Audio level (0-1)
 * @param {boolean} [props.showChart=false] - Whether to show the history chart
 * @param {Array} [props.chartData=[]] - Array of {time, level} for chart
 * @param {string} [props.label] - Custom label (defaults to translated 'mic_level')
 * @param {Object} [props.sx] - Additional MUI sx styles
 */
function VUMeter({ level = 0, showChart = false, chartData = [], label, sx = {}, ...props }) {
  const { t } = useTranslation();
  const displayLabel = label || t('mic_level');
  const percentage = Math.min(100, Math.max(0, level * 100));
  const vuColor = getVUColor(level);
  
  return (
    <Box sx={sx} {...props}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <MicIcon color="primary" />
        <Typography variant="h6">{displayLabel}</Typography>
      </Box>
      
      <LinearProgress
        variant="determinate"
        value={percentage}
        sx={{
          height: 20,
          borderRadius: 10,
          backgroundColor: 'action.hover',
          '& .MuiLinearProgress-bar': {
            backgroundColor: vuColor,
            transition: 'all 0.1s ease',
            borderRadius: 10,
          },
        }}
      />
      
      <Typography 
        variant="caption" 
        color="text.secondary" 
        sx={{ mt: 1, display: 'block' }}
      >
        {percentage.toFixed(1)}%
      </Typography>
      
      {showChart && chartData.length > 0 && (
        <Box sx={{ mt: 2, height: 100 }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart 
              data={chartData.map((item, i) => ({ 
                index: i, 
                level: item.level * 100 
              }))}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="index" hide />
              <YAxis domain={[0, 100]} hide />
              <Line
                type="monotone"
                dataKey="level"
                stroke={colors.primary.main}
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </Box>
      )}
    </Box>
  );
}

export default VUMeter;
