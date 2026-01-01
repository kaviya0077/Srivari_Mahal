// src/api.js
import axios from "axios";

const BASE_URL = process.env.REACT_APP_API_URL || (process.env.NODE_ENV === 'production' 
                  ? 'https://srivari-mahal.onrender.com'  // Replace with your Render URL
                  : 'http://localhost:8000/api');;

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => {
    console.error("❌ Request Error:", error);
    Promise.reject(error)
  }
);

api.interceptors.response.use(
  (response) => {
    console.log(`✅ Response from ${response.config.url}:`, response.status);
    return response;
  },
  (error) => {
    console.error("❌ API Error:", {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      data: error.response?.data,
      message: error.message,
    });
    return Promise.reject(error);
  }
);
export default api;