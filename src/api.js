import axios from 'axios';

export const fetchNews = async (params = {}) => {
  const response = await axios.get('/api/news', { params });
  return response.data;
};
