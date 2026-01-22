import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Paper
} from '@mui/material';
import {
  Comment as CommentIcon,
  CardGiftcard as GiftIcon,
  PersonAdd as FollowIcon,
  Share as ShareIcon,
  ThumbUp as LikeIcon,
  PersonAddAlt as JoinIcon
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';

import socketService from '../utils/socket';

function Events() {
  const { t } = useTranslation();
  const [events, setEvents] = useState([]);
  const [stats, setStats] = useState({
    comments: 0,
    gifts: 0,
    followers: 0,
    likes: 0,
    joins: 0,
    shares: 0
  });

  useEffect(() => {
    // Listen for various event types through logs
    const handleLog = (log) => {
      const message = log.message.toLowerCase();
      
      // Parse event from log message
      let eventType = null;
      let eventData = { message: log.message, timestamp: log.timestamp };

      if (message.includes('kommentar') || message.includes('comment')) {
        eventType = 'comment';
        setStats(prev => ({ ...prev, comments: prev.comments + 1 }));
      } else if (message.includes('gift') || message.includes('geschenk')) {
        eventType = 'gift';
        setStats(prev => ({ ...prev, gifts: prev.gifts + 1 }));
      } else if (message.includes('follow')) {
        eventType = 'follow';
        setStats(prev => ({ ...prev, followers: prev.followers + 1 }));
      } else if (message.includes('like')) {
        eventType = 'like';
        setStats(prev => ({ ...prev, likes: prev.likes + 1 }));
      } else if (message.includes('join') || message.includes('beitritt')) {
        eventType = 'join';
        setStats(prev => ({ ...prev, joins: prev.joins + 1 }));
      } else if (message.includes('share')) {
        eventType = 'share';
        setStats(prev => ({ ...prev, shares: prev.shares + 1 }));
      }

      if (eventType) {
        setEvents(prev => [{
          ...eventData,
          type: eventType,
          id: Date.now() + Math.random()
        }, ...prev].slice(0, 100)); // Keep last 100 events
      }
    };

    socketService.on('log', handleLog);

    return () => {
      socketService.off('log', handleLog);
    };
  }, []);

  const getEventIcon = (type) => {
    switch (type) {
      case 'comment': return <CommentIcon />;
      case 'gift': return <GiftIcon />;
      case 'follow': return <FollowIcon />;
      case 'like': return <LikeIcon />;
      case 'join': return <JoinIcon />;
      case 'share': return <ShareIcon />;
      default: return <CommentIcon />;
    }
  };

  const getEventColor = (type) => {
    switch (type) {
      case 'comment': return 'info';
      case 'gift': return 'warning';
      case 'follow': return 'success';
      case 'like': return 'error';
      case 'join': return 'primary';
      case 'share': return 'secondary';
      default: return 'default';
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleTimeString();
  };

  const StatCard = ({ icon, label, value, color }) => (
    <motion.div
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box>
              <Typography color="text.secondary" variant="body2" gutterBottom>
                {label}
              </Typography>
              <Typography variant="h4">{value}</Typography>
            </Box>
            <Avatar sx={{ bgcolor: `${color}.main`, width: 56, height: 56 }}>
              {icon}
            </Avatar>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );

  return (
    <Box>
      {/* Event Statistics */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            icon={<CommentIcon />}
            label={t('comments')}
            value={stats.comments}
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            icon={<GiftIcon />}
            label={t('gifts')}
            value={stats.gifts}
            color="warning"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            icon={<FollowIcon />}
            label={t('followers')}
            value={stats.followers}
            color="success"
          />
        </Grid>
      </Grid>

      {/* Event Stream */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {t('real_time_updates')}
          </Typography>
          <Paper
            sx={{
              height: 'calc(100vh - 450px)',
              overflow: 'auto',
              mt: 2
            }}
          >
            {events.length === 0 ? (
              <Box sx={{ textAlign: 'center', py: 8 }}>
                <Typography variant="h6" color="text.secondary">
                  No events yet
                </Typography>
              </Box>
            ) : (
              <List>
                <AnimatePresence>
                  {events.map((event) => (
                    <motion.div
                      key={event.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.2 }}
                    >
                      <ListItem
                        sx={{
                          borderBottom: '1px solid',
                          borderColor: 'divider'
                        }}
                      >
                        <ListItemAvatar>
                          <Avatar sx={{ bgcolor: `${getEventColor(event.type)}.main` }}>
                            {getEventIcon(event.type)}
                          </Avatar>
                        </ListItemAvatar>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                              <Chip
                                label={event.type}
                                color={getEventColor(event.type)}
                                size="small"
                              />
                              <Typography variant="caption" color="text.secondary">
                                {formatTime(event.timestamp)}
                              </Typography>
                            </Box>
                          }
                          secondary={event.message}
                        />
                      </ListItem>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </List>
            )}
          </Paper>
        </CardContent>
      </Card>
    </Box>
  );
}

export default Events;
