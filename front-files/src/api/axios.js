// src/api/axios.js
import axios from 'axios';

const axiosInstance = axios.create({
    baseURL: process.env.REACT_APP_API_URL || 'http://localhost:3001', // Tu backend URL
    headers: {
        'Content-Type': 'application/json',
    },
});

// Interceptor para agregar el token JWT a cada request
axiosInstance.interceptors.request.use(
    config => {
        const token = localStorage.getItem('jwt_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    error => Promise.reject(error)
);

// Interceptor para manejar tokens expirados o inválidos
axiosInstance.interceptors.response.use(
    response => response,
    async error => {
        const originalRequest = error.config;
        if (error.response.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            localStorage.removeItem('jwt_token');
            delete axiosInstance.defaults.headers.common['Authorization'];
            // Opcional: redireccionar al login si no estamos ya allí
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export default axiosInstance;