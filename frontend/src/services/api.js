/**
 * TruthLens AI - API Client Service
 * Interacts with Flask backend endpoints.
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 45000,
});

// Attach JWT token to requests if present in localStorage
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('truthlens_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const api = {
  // Health
  checkHealth: () => apiClient.get('/health'),

  // Auth
  login: (credentials) => apiClient.post('/auth/login', credentials),
  register: (userData) => apiClient.post('/auth/register', userData),
  getCurrentUser: () => apiClient.get('/auth/me'),

  // News Analysis
  analyzeText: (payload) => apiClient.post('/analyze/text', payload),
  analyzeUrl: (payload) => apiClient.post('/analyze/url', payload),
  analyzeDocument: (formData) => apiClient.post('/analyze/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  analyzeImage: (formData) => apiClient.post('/analyze/image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),

  // Dashboard & Reports
  getDashboardStats: () => apiClient.get('/dashboard/stats'),
  getModelPerformance: () => apiClient.get('/models/performance'),
  getHistory: (params) => apiClient.get('/analysis/history', { params }),
  getAnalysisDetail: (id) => apiClient.get(`/analysis/${id}`),
  deleteAnalysis: (id) => apiClient.delete(`/analysis/${id}`),
  submitReview: (payload) => apiClient.post('/review', payload),
};

export default api;
