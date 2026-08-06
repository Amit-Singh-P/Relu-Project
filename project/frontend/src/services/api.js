import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

export const enrichCompany = async (websiteName, url) => {
  const response = await apiClient.post('/enrich', { websiteName, url });
  return response.data;
};

export const getAllResults = async () => {
  const response = await apiClient.get('/results');
  return response.data;
};

export default apiClient;
