import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
} from '@mui/material';
import {
  PlayArrow as StartIcon,
  Stop as StopIcon,
  People as PeopleIcon,
  Comment as CommentIcon,
  CardGiftcard as GiftIcon,
  PersonAdd as FollowIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

import { startApp, stopApp, getStatus, getMemory } from '../utils/api';
import socketService from '../utils/socket';
import { StatusChip, StatCard, ConnectionStatus, VUMeter } from './ui';

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
                <StatusChip 
                  status={status.running ? 'running' : 'stopped'} 
                  label={t(status.running ? 'running' : 'stopped')}
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
            <VUMeter 
              level={status.mic_level} 
              showChart={micHistory.length > 0}
              chartData={micHistory}
            />
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
