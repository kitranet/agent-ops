import axios from 'axios';

const API_BASE = 'http://localhost:8000/agents';

export const fetchAgents = async (params = {}) => {
  const response = await axios.get(`${API_BASE}/export`, { params });
  return response.data;
};
