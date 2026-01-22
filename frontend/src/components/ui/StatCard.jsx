/**
 * Reusable StatCard component
 * Displays a statistic with an icon in a card format
 * 
 * Usage:
 * <StatCard
 *   icon={PeopleIcon}
 *   label="Viewers"
 *   value={142}
 *   color="primary.main"
 * />
 */

import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';
import { motion } from 'framer-motion';

/**
 * StatCard Component
 * 
 * @param {Object} props
 * @param {React.ElementType} props.icon - MUI Icon component
 * @param {string} props.label - Label text
 * @param {string|number} props.value - Value to display
 * @param {string} props.color - MUI color string (e.g., 'primary.main', 'success.main')
 * @param {Object} [props.sx] - Additional MUI sx styles
 */
function StatCard({ icon: Icon, label, value, color, sx = {}, ...props }) {
  return (
    <motion.div
      whileHover={{ scale: 1.03, transition: { duration: 0.2 } }}
      whileTap={{ scale: 0.98 }}
    >
      <Card sx={sx} {...props}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box>
              <Typography color="text.secondary" variant="body2" gutterBottom>
                {label}
              </Typography>
              <Typography variant="h4" component="div" fontWeight={600}>
                {typeof value === 'number' ? value.toLocaleString() : value}
              </Typography>
            </Box>
            <Icon sx={{ fontSize: 48, color }} />
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );
}

export default StatCard;
