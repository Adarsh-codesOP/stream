import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'; // management Layer

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});


api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const endpoints = {
  login: '/auth/login',
  register: '/auth/register',
  rooms: '/rooms',
  createRoom: '/rooms',
};
