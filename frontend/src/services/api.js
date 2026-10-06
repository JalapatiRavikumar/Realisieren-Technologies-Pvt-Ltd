import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:8000' : '');

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes for scraping tasks
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getHealth = async () => {
  const response = await apiClient.get('/api/health');
  return response.data;
};

export const getDashboard = async () => {
  const response = await apiClient.get('/api/dashboard');
  return response.data;
};

export const getSummary = async () => {
  const response = await apiClient.get('/api/summary');
  return response.data;
};

export const getRecords = async ({ page = 1, limit = 20, source = '', search = '' } = {}) => {
  const params = { page, limit };
  if (source && source !== 'all') params.source = source;
  if (search && search.trim()) params.search = search.trim();

  const response = await apiClient.get('/api/records', { params });
  return response.data;
};

export const runScraper = async ({ source = 'all', max_pages = null } = {}) => {
  const response = await apiClient.post('/api/scrape', { source, max_pages });
  return response.data;
};

export const getDownloadCsvUrl = () => `${API_BASE_URL}/api/download/csv`;
export const getDownloadSummaryUrl = () => `${API_BASE_URL}/api/download/summary`;
