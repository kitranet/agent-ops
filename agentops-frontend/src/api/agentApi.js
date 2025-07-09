import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000';

/**
 * Fetch all agents with optional query parameters for:
 * - search
 * - sort_by
 * - sort_order
 * - status, owner, framework (for future enhancements)
 */
export const fetchAllAgents = async (params = {}) => {
  const res = await axios.get(`${API_BASE}/agents/list/all`, { params });
  return res.data;
};
