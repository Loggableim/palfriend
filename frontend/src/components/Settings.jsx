import React, { useState, useEffect, useCallback } from 'react';
import {
  Grid,
  Card,
  Typography,
  TextField,
  Button,
  Box,
  Slider,
  Switch,
  FormControlLabel,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Snackbar,
  Alert,
  IconButton,
  InputAdornment
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Save as SaveIcon,
  Upload as UploadIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';

import { getSettings, updateSettings, exportSettings, importSettings, getDevices } from '../utils/api';

function Settings() {
  const { t } = useTranslation();
  const [settings, setSettings] = useState(null);
  const [devices, setDevices] = useState([]);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [showApiKey, setShowApiKey] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadSettings();
    loadDevices();
  }, []);

  const loadSettings = async () => {
    try {
      const response = await getSettings();
      if (response.data.success) {
        setSettings(response.data.data);
      }
    } catch (error) {
      showSnackbar(t('settings_load_error'), 'error');
    }
  };

  const loadDevices = async () => {
    try {
      const response = await getDevices();
      if (response.data.success) {
        setDevices(response.data.data);
      }
    } catch (error) {
      console.error('Failed to load devices:', error);
    }
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      await updateSettings(settings);
      showSnackbar(t('settings_saved'), 'success');
    } catch (error) {
      showSnackbar('Failed to save settings', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format) => {
    try {
      const response = await exportSettings(format);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `settings.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      showSnackbar('Failed to export settings', 'error');
    }
  };

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      try {
        await importSettings(acceptedFiles[0]);
        await loadSettings();
        showSnackbar(t('file_imported'), 'success');
      } catch (error) {
        showSnackbar(t('file_import_error'), 'error');
      }
    }
  }, [t]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/json': ['.json'], 'application/x-yaml': ['.yaml', '.yml'] },
    multiple: false
  });

  const showSnackbar = (message, severity) => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const updateSetting = (section, key, value) => {
    setSettings(prev => ({
      ...prev,
      [section]: { ...prev[section], [key]: value }
    }));
  };

  if (!settings) {
    return <Typography>Loading...</Typography>;
  }

  return (
    <Box>
      {/* Action Buttons */}
      <Box sx={{ mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <Button
          variant="contained"
          color="primary"
          startIcon={<SaveIcon />}
          onClick={handleSave}
          disabled={loading}
          size="large"
        >
          {t('save')}
        </Button>
        <Button
          variant="outlined"
          startIcon={<DownloadIcon />}
          onClick={() => handleExport('json')}
        >
          {t('export')} JSON
        </Button>
        <Button
          variant="outlined"
          startIcon={<DownloadIcon />}
          onClick={() => handleExport('yaml')}
        >
          {t('export')} YAML
        </Button>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={loadSettings}
        >
          Reload
        </Button>
      </Box>

      {/* Drag and Drop Import */}
      <motion.div
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <Card
          {...getRootProps()}
          sx={{
            mb: 3,
            p: 3,
            border: '2px dashed',
            borderColor: isDragActive ? 'primary.main' : 'grey.400',
            backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
            cursor: 'pointer',
            transition: 'all 0.3s ease'
          }}
        >
          <input {...getInputProps()} />
          <Box sx={{ textAlign: 'center' }}>
            <UploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
            <Typography variant="h6">{t('import_settings')}</Typography>
            <Typography variant="body2" color="text.secondary">
              {t('drag_drop_hint')}
            </Typography>
          </Box>
        </Card>
      </motion.div>

      {/* Settings Sections */}
      <Grid container spacing={2}>
        {/* TikTok Settings */}
        <Grid item xs={12}>
          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">{t('tiktok_settings')}</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label={t('tiktok_handle')}
                    value={settings.tiktok?.unique_id || ''}
                    onChange={(e) => updateSetting('tiktok', 'unique_id', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label={t('tiktok_session_id')}
                    type={showApiKey ? 'text' : 'password'}
                    value={settings.tiktok?.session_id || ''}
                    onChange={(e) => updateSetting('tiktok', 'session_id', e.target.value)}
                    InputProps={{
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton onClick={() => setShowApiKey(!showApiKey)} edge="end">
                            {showApiKey ? <VisibilityOffIcon /> : <VisibilityIcon />}
                          </IconButton>
                        </InputAdornment>
                      )
                    }}
                  />
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        </Grid>

        {/* Animaze Settings */}
        <Grid item xs={12}>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">{t('animaze_settings')}</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label={t('animaze_host')}
                    value={settings.animaze?.host || ''}
                    onChange={(e) => updateSetting('animaze', 'host', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label={t('animaze_port')}
                    type="number"
                    value={settings.animaze?.port || 9000}
                    onChange={(e) => updateSetting('animaze', 'port', parseInt(e.target.value))}
                  />
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        </Grid>

        {/* OpenAI Settings */}
        <Grid item xs={12}>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">{t('openai_settings')}</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label={t('openai_api_key')}
                    type={showApiKey ? 'text' : 'password'}
                    value={settings.openai?.api_key || ''}
                    onChange={(e) => updateSetting('openai', 'api_key', e.target.value)}
                    InputProps={{
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton onClick={() => setShowApiKey(!showApiKey)} edge="end">
                            {showApiKey ? <VisibilityOffIcon /> : <VisibilityIcon />}
                          </IconButton>
                        </InputAdornment>
                      )
                    }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>{t('openai_model')}</InputLabel>
                    <Select
                      value={settings.openai?.model || 'gpt-4o-mini'}
                      onChange={(e) => updateSetting('openai', 'model', e.target.value)}
                      label={t('openai_model')}
                    >
                      <MenuItem value="gpt-4o-mini">GPT-4o Mini</MenuItem>
                      <MenuItem value="gpt-4o">GPT-4o</MenuItem>
                      <MenuItem value="gpt-4-turbo">GPT-4 Turbo</MenuItem>
                      <MenuItem value="gpt-3.5-turbo">GPT-3.5 Turbo</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        </Grid>

        {/* Comment Settings */}
        <Grid item xs={12}>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">{t('comment_settings')}</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={Boolean(settings.comment?.enabled)}
                        onChange={(e) => updateSetting('comment', 'enabled', e.target.checked ? 1 : 0)}
                      />
                    }
                    label={t('comment_enabled')}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography gutterBottom>{t('global_cooldown')}</Typography>
                  <Slider
                    value={settings.comment?.global_cooldown || 6}
                    onChange={(e, val) => updateSetting('comment', 'global_cooldown', val)}
                    min={1}
                    max={60}
                    valueLabelDisplay="auto"
                    marks={[
                      { value: 1, label: '1s' },
                      { value: 30, label: '30s' },
                      { value: 60, label: '60s' }
                    ]}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography gutterBottom>{t('per_user_cooldown')}</Typography>
                  <Slider
                    value={settings.comment?.per_user_cooldown || 15}
                    onChange={(e, val) => updateSetting('comment', 'per_user_cooldown', val)}
                    min={5}
                    max={120}
                    valueLabelDisplay="auto"
                    marks={[
                      { value: 5, label: '5s' },
                      { value: 60, label: '60s' },
                      { value: 120, label: '120s' }
                    ]}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label={t('max_replies_per_min')}
                    type="number"
                    value={settings.comment?.max_replies_per_min || 20}
                    onChange={(e) => updateSetting('comment', 'max_replies_per_min', parseInt(e.target.value))}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography gutterBottom>{t('reply_threshold')}</Typography>
                  <Slider
                    value={settings.comment?.reply_threshold || 0.6}
                    onChange={(e, val) => updateSetting('comment', 'reply_threshold', val)}
                    min={0}
                    max={1}
                    step={0.1}
                    valueLabelDisplay="auto"
                    marks={[
                      { value: 0, label: '0' },
                      { value: 0.5, label: '0.5' },
                      { value: 1, label: '1' }
                    ]}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={Boolean(settings.comment?.respond_to_greetings)}
                        onChange={(e) => updateSetting('comment', 'respond_to_greetings', e.target.checked ? 1 : 0)}
                      />
                    }
                    label={t('respond_to_greetings')}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={Boolean(settings.comment?.respond_to_thanks)}
                        onChange={(e) => updateSetting('comment', 'respond_to_thanks', e.target.checked ? 1 : 0)}
                      />
                    }
                    label={t('respond_to_thanks')}
                  />
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        </Grid>

        {/* Microphone Settings */}
        <Grid item xs={12}>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">{t('microphone_settings')}</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={Boolean(settings.microphone?.enabled)}
                        onChange={(e) => updateSetting('microphone', 'enabled', e.target.checked ? 1 : 0)}
                      />
                    }
                    label={t('mic_enabled')}
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>{t('mic_device')}</InputLabel>
                    <Select
                      value={settings.microphone?.device || ''}
                      onChange={(e) => updateSetting('microphone', 'device', e.target.value)}
                      label={t('mic_device')}
                    >
                      <MenuItem value="">Default</MenuItem>
                      {devices.map((dev) => (
                        <MenuItem key={dev.id} value={dev.id.toString()}>
                          {dev.name} ({dev.channels} channels)
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  <Typography gutterBottom>{t('silence_threshold')}</Typography>
                  <Slider
                    value={settings.microphone?.silence_threshold || 0.02}
                    onChange={(e, val) => updateSetting('microphone', 'silence_threshold', val)}
                    min={0}
                    max={1}
                    step={0.01}
                    valueLabelDisplay="auto"
                  />
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        </Grid>

        {/* Join Settings */}
        <Grid item xs={12}>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">{t('join_settings')}</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={Boolean(settings.join_rules?.enabled)}
                        onChange={(e) => updateSetting('join_rules', 'enabled', e.target.checked ? 1 : 0)}
                      />
                    }
                    label={t('join_enabled')}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label={t('greet_after_seconds')}
                    type="number"
                    value={settings.join_rules?.greet_after_seconds || 30}
                    onChange={(e) => updateSetting('join_rules', 'greet_after_seconds', parseInt(e.target.value))}
                  />
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        </Grid>
      </Grid>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', right: 'right' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default Settings;
