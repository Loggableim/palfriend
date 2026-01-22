import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  LinearProgress,
  Chip,
  Paper
} from '@mui/material';
import {
  PlayArrow as StartIcon,
  Stop as StopIcon,
  CheckCircle as ConnectedIcon,
  Cancel as DisconnectedIcon,
  People as PeopleIcon,
  Comment as CommentIcon,
  CardGiftcard as GiftIcon,
  PersonAdd as FollowIcon,
  Mic as MicIcon
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

import { startApp, stopApp, getStatus, getMemory } from '../utils/api';
import socketService from '../utils/socket';

function Dashboard() {
  const { t } = useTranslation();
  const [status, setStatus] = useState({
    running: false,
    connected: { tiktok: false, animaze: false, microphone: false },
    stats: { viewers: 0, comments: 0, gifts: 0, followers: 0 },
    mic_level: 0
  });
  const [memory, setMemory] = useState({ total_users: 0, recent_activity: 0 });
  const [micHistory, setMicHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadStatus();
    loadMemory();

    // Listen to WebSocket updates
    const handleStatus = (data) => setStatus(prev => ({ ...prev, ...data }));
    const handleStatusChange = (data) => setStatus(prev => ({ ...prev, ...data }));
    const handleConnectionStatus = (data) => {
      setStatus(prev => ({
        ...prev,
        connected: { ...prev.connected, [data.service]: data.connected }
      }));
    };
    const handleStats = (data) => setStatus(prev => ({ ...prev, stats: data }));
    const handleMicLevel = (data) => {
      setStatus(prev => ({ ...prev, mic_level: data.level }));
      setMicHistory(prev => {
        const newHistory = [...prev, { time: Date.now(), level: data.level }];
        return newHistory.slice(-50); // Keep last 50 samples
      });
    };

    socketService.on('status', handleStatus);
    socketService.on('status_change', handleStatusChange);
    socketService.on('connection_status', handleConnectionStatus);
    socketService.on('stats', handleStats);
    socketService.on('mic_level', handleMicLevel);

    return () => {
      socketService.off('status', handleStatus);
      socketService.off('status_change', handleStatusChange);
      socketService.off('connection_status', handleConnectionStatus);
      socketService.off('stats', handleStats);
      socketService.off('mic_level', handleMicLevel);
    };
  }, []);

  const loadStatus = async () => {
    try {
      const response = await getStatus();
      if (response.data.success) {
        setStatus(response.data.data);
      }
    } catch (error) {
      console.error('Failed to load status:', error);
    }
  };

  const loadMemory = async () => {
    try {
      const response = await getMemory();
      if (response.data.success) {
        setMemory(response.data.data);
      }
    } catch (error) {
      console.error('Failed to load memory:', error);
    }
  };

  const handleStart = async () => {
    setLoading(true);
    try {
      await startApp();
      await loadStatus();
    } catch (error) {
      console.error('Failed to start app:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStop = async () => {
    setLoading(true);
    try {
      await stopApp();
      await loadStatus();
    } catch (error) {
      console.error('Failed to stop app:', error);
    } finally {
      setLoading(false);
    }
  };

  const ConnectionStatus = ({ service, connected }) => (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
      <motion.div
        animate={{ scale: connected ? [1, 1.2, 1] : 1 }}
        transition={{ repeat: connected ? Infinity : 0, duration: 2 }}
      >
        {connected ? (
          <ConnectedIcon color="success" />
        ) : (
          <DisconnectedIcon color="error" />
        )}
      </motion.div>
      <Typography variant="body1">
        {t(service)}: <strong>{t(connected ? 'connected' : 'disconnected')}</strong>
      </Typography>
    </Box>
  );

  const StatCard = ({ icon: Icon, label, value, color }) => (
    <motion.div
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box>
              <Typography color="text.secondary" gutterBottom>
                {label}
              </Typography>
              <Typography variant="h4" component="div">
                {value}
              </Typography>
            </Box>
            <Icon sx={{ fontSize: 48, color }} />
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );

  return (
    <Grid container spacing={3}>
      {/* Control Panel */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Box>
                <Typography variant="h5" gutterBottom>
                  {t('status')}
                </Typography>
                <Chip
                  label={t(status.running ? 'running' : 'stopped')}
                  color={status.running ? 'success' : 'default'}
                  sx={{ fontWeight: 'bold' }}
                />
              </Box>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button
                  variant="contained"
                  color="success"
                  startIcon={<StartIcon />}
                  onClick={handleStart}
                  disabled={status.running || loading}
                  size="large"
                >
                  {t('start')}
                </Button>
                <Button
                  variant="contained"
                  color="error"
                  startIcon={<StopIcon />}
                  onClick={handleStop}
                  disabled={!status.running || loading}
                  size="large"
                >
                  {t('stop')}
                </Button>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Connection Status */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              {t('connection_status')}
            </Typography>
            <ConnectionStatus service="tiktok" connected={status.connected.tiktok} />
            <ConnectionStatus service="animaze" connected={status.connected.animaze} />
            <ConnectionStatus service="microphone" connected={status.connected.microphone} />
          </CardContent>
        </Card>
      </Grid>

      {/* VU Meter */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <MicIcon />
              <Typography variant="h6">{t('mic_level')}</Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={status.mic_level * 100}
              sx={{
                height: 20,
                borderRadius: 10,
                '& .MuiLinearProgress-bar': {
                  backgroundColor: status.mic_level > 0.7 ? 'error.main' : 
                                   status.mic_level > 0.4 ? 'warning.main' : 'success.main',
                  transition: 'all 0.1s ease'
                }
              }}
            />
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
              {(status.mic_level * 100).toFixed(1)}%
            </Typography>
            
            {micHistory.length > 0 && (
              <Box sx={{ mt: 2, height: 100 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={micHistory.map((item, i) => ({ index: i, level: item.level * 100 }))}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="index" hide />
                    <YAxis domain={[0, 100]} hide />
                    <Line 
                      type="monotone" 
                      dataKey="level" 
                      stroke="#1976d2" 
                      strokeWidth={2}
                      dot={false}
                      isAnimationActive={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            )}
          </CardContent>
        </Card>
      </Grid>

      {/* Statistics */}
      <Grid item xs={12}>
        <Typography variant="h6" gutterBottom>
          {t('statistics')}
        </Typography>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          icon={PeopleIcon}
          label={t('viewers')}
          value={status.stats.viewers}
          color="primary.main"
        />
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          icon={CommentIcon}
          label={t('comments')}
          value={status.stats.comments}
          color="info.main"
        />
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          icon={GiftIcon}
          label={t('gifts')}
          value={status.stats.gifts}
          color="warning.main"
        />
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          icon={FollowIcon}
          label={t('followers')}
          value={status.stats.followers}
          color="success.main"
        />
      </Grid>

      {/* Memory Statistics */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              {t('memory_settings')}
            </Typography>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Typography color="text.secondary">{t('total_users')}</Typography>
              <Typography variant="h6">{memory.total_users}</Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography color="text.secondary">{t('recent_activity')}</Typography>
              <Typography variant="h6">{memory.recent_activity}</Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}

export default Dashboard;
