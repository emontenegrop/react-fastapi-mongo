// src/services/api.js
import axiosInstance from '../api/axios';
import { API_CONFIG } from '../config/api';

// Base API service class
class BaseApiService {
  constructor(baseEndpoint) {
    this.baseEndpoint = baseEndpoint;
  }

  async get(endpoint = '', config = {}) {
    const response = await axiosInstance.get(`${this.baseEndpoint}${endpoint}`, config);
    return response.data;
  }

  async post(endpoint = '', data = {}, config = {}) {
    const response = await axiosInstance.post(`${this.baseEndpoint}${endpoint}`, data, config);
    return response.data;
  }

  async put(endpoint = '', data = {}, config = {}) {
    const response = await axiosInstance.put(`${this.baseEndpoint}${endpoint}`, data, config);
    return response.data;
  }

  async patch(endpoint = '', data = {}, config = {}) {
    const response = await axiosInstance.patch(`${this.baseEndpoint}${endpoint}`, data, config);
    return response.data;
  }

  async delete(endpoint = '', config = {}) {
    const response = await axiosInstance.delete(`${this.baseEndpoint}${endpoint}`, config);
    return response.data;
  }
}

// Authentication service
export class AuthService extends BaseApiService {
  constructor() {
    super(API_CONFIG.ENDPOINTS.AUTH.BASE);
  }

  async login(credentials) {
    return this.post('/login', credentials);
  }

  async logout(refreshToken) {
    return this.post('/logout', { refreshToken });
  }

  async refreshToken(refreshToken) {
    return this.post('/refresh', { refreshToken });
  }

  async forgotPassword(email) {
    return this.post('/forgot-password', { email });
  }

  async resetPassword(token, password) {
    return this.post('/reset-password', { token, password });
  }

  async changePassword(currentPassword, newPassword) {
    return this.post('/change-password', { currentPassword, newPassword });
  }

  async getMe() {
    return this.get('/me');
  }

  async updateProfile(profileData) {
    return this.put('/profile', profileData);
  }
}

// User service
export class UserService extends BaseApiService {
  constructor() {
    super(API_CONFIG.ENDPOINTS.USERS.BASE);
  }

  async getUsers(params = {}) {
    return this.get('', { params });
  }

  async getUser(id) {
    return this.get(`/${id}`);
  }

  async createUser(userData) {
    return this.post('', userData);
  }

  async updateUser(id, userData) {
    return this.put(`/${id}`, userData);
  }

  async deleteUser(id) {
    return this.delete(`/${id}`);
  }

  async getUserProfile(id) {
    return this.get(`/${id}/profile`);
  }

  async updateUserProfile(id, profileData) {
    return this.put(`/${id}/profile`, profileData);
  }

  async uploadAvatar(id, file) {
    const formData = new FormData();
    formData.append('avatar', file);
    
    return this.post(`/${id}/avatar`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  }
}

// File service
export class FileService extends BaseApiService {
  constructor() {
    super(API_CONFIG.ENDPOINTS.FILES.BASE);
  }

  async getFiles(params = {}) {
    return this.get('', { params });
  }

  async getFile(id) {
    return this.get(`/${id}`);
  }

  async uploadFile(file, metadata = {}) {
    const formData = new FormData();
    formData.append('file', file);
    
    Object.keys(metadata).forEach(key => {
      formData.append(key, metadata[key]);
    });

    return this.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: metadata.onUploadProgress
    });
  }

  async downloadFile(id) {
    return this.get(`/${id}/download`, {
      responseType: 'blob'
    });
  }

  async deleteFile(id) {
    return this.delete(`/${id}`);
  }

  async updateFile(id, metadata) {
    return this.put(`/${id}`, metadata);
  }

  async searchFiles(query, filters = {}) {
    return this.get('/search', {
      params: { query, ...filters }
    });
  }

  async getFileVersions(id) {
    return this.get(`/${id}/versions`);
  }

  async shareFile(id, shareData) {
    return this.post(`/${id}/share`, shareData);
  }
}

// Log service
export class LogService extends BaseApiService {
  constructor() {
    super(API_CONFIG.ENDPOINTS.LOGS.BASE);
  }

  async getSystemLogs(params = {}) {
    return this.get('/system', { params });
  }

  async getSecurityLogs(params = {}) {
    return this.get('/security', { params });
  }

  async getUserLogs(params = {}) {
    return this.get('/user', { params });
  }

  async logEvent(eventData) {
    return this.post('', eventData);
  }
}

// Service instances
export const authService = new AuthService();
export const userService = new UserService();
export const fileService = new FileService();
export const logService = new LogService();

// Export default API object with all services
const api = {
  auth: authService,
  users: userService,
  files: fileService,
  logs: logService
};

export default api;