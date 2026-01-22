import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

export const getSettings = () => api.get('/settings');
export const updateSettings = (data) => api.put('/settings', data);
export const exportSettings = (format = 'json') => 
  api.get(`/settings/export?format=${format}`, { responseType: 'blob' });
export const importSettings = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/settings/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};
export const getStatus = () => api.get('/status');
export const startApp = () => api.post('/start');
export const stopApp = () => api.post('/stop');
export const getMemory = () => api.get('/memory');
export const getDevices = () => api.get('/devices');
export const getDefaults = () => api.get('/defaults');

export default api;
