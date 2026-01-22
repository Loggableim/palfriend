import React, { useState, useEffect, useRef } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  TextField,
  IconButton,
  Chip,
  List,
  ListItem,
  Paper,
  Tooltip,
  Button
} from '@mui/material';
import {
  Clear as ClearIcon,
  Download as DownloadIcon,
  Search as SearchIcon
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';

import socketService from '../utils/socket';

function Logs() {
  const { t } = useTranslation();
  const [logs, setLogs] = useState([]);
  const [filter, setFilter] = useState('');
  const [autoScroll, setAutoScroll] = useState(true);
  const logsEndRef = useRef(null);

  useEffect(() => {
    const handleLog = (log) => {
      setLogs(prev => [...prev, log].slice(-1000)); // Keep last 1000 logs
    };

    socketService.on('log', handleLog);

    return () => {
      socketService.off('log', handleLog);
    };
  }, []);

  useEffect(() => {
    if (autoScroll && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll]);

  const filteredLogs = logs.filter(log =>
    filter === '' ||
    log.message.toLowerCase().includes(filter.toLowerCase()) ||
    log.level.toLowerCase().includes(filter.toLowerCase())
  );

  const handleClear = () => {
    setLogs([]);
  };

  const handleDownload = () => {
    const content = logs.map(log => 
      `[${new Date(log.timestamp * 1000).toISOString()}] ${log.level}: ${log.message}`
    ).join('\n');
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `logs-${Date.now()}.txt`;
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  const getLevelColor = (level) => {
    switch (level.toUpperCase()) {
      case 'ERROR': return 'error';
      case 'WARNING': return 'warning';
      case 'INFO': return 'info';
      case 'DEBUG': return 'default';
      default: return 'default';
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleTimeString();
  };

  return (
    <Box>
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
            <TextField
              size="small"
              placeholder={t('search_logs')}
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
              }}
              sx={{ flexGrow: 1, minWidth: 200 }}
            />
            <Tooltip title={t('clear_logs')}>
              <IconButton onClick={handleClear} color="error">
                <ClearIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title={t('download_logs')}>
              <IconButton onClick={handleDownload} color="primary">
                <DownloadIcon />
              </IconButton>
            </Tooltip>
            <Button
              variant={autoScroll ? 'contained' : 'outlined'}
              size="small"
              onClick={() => setAutoScroll(!autoScroll)}
            >
              Auto-scroll
            </Button>
          </Box>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            Showing {filteredLogs.length} of {logs.length} logs
          </Typography>
        </CardContent>
      </Card>

      <Paper
        sx={{
          height: 'calc(100vh - 350px)',
          overflow: 'auto',
          p: 2,
          backgroundColor: 'background.paper'
        }}
      >
        {filteredLogs.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <Typography variant="h6" color="text.secondary">
              {t('no_logs')}
            </Typography>
          </Box>
        ) : (
          <List>
            <AnimatePresence>
              {filteredLogs.map((log, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <ListItem
                    sx={{
                      display: 'flex',
                      gap: 2,
                      alignItems: 'flex-start',
                      py: 1,
                      borderBottom: '1px solid',
                      borderColor: 'divider',
                      fontFamily: 'monospace'
                    }}
                  >
                    <Typography
                      variant="caption"
                      sx={{ minWidth: 80, color: 'text.secondary' }}
                    >
                      {formatTime(log.timestamp)}
                    </Typography>
                    <Chip
                      label={log.level}
                      color={getLevelColor(log.level)}
                      size="small"
                      sx={{ minWidth: 80 }}
                    />
                    <Typography
                      variant="body2"
                      sx={{ flexGrow: 1, wordBreak: 'break-word' }}
                    >
                      {log.message}
                    </Typography>
                  </ListItem>
                </motion.div>
              ))}
            </AnimatePresence>
            <div ref={logsEndRef} />
          </List>
        )}
      </Paper>
    </Box>
  );
}

export default Logs;
