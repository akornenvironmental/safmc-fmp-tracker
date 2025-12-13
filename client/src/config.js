// API Configuration
// In production (deployed on same server), use relative URLs
// In development, use localhost
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.MODE === 'production' ? '' : 'http://localhost:5001');

export default {
  API_BASE_URL,
};
