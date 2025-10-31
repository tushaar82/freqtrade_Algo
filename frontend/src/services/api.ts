/**
 * API Client
 * VELOX Trading Platform
 */
import axios, { AxiosInstance } from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth token to requests
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle 401 errors
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth
  async login(email: string, password: string) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await this.client.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  }

  async refreshToken(refreshToken: string) {
    const response = await this.client.post('/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  }

  // Strategies
  async getStrategies() {
    const response = await this.client.get('/strategies');
    return response.data;
  }

  async getStrategy(id: string) {
    const response = await this.client.get(`/strategies/${id}`);
    return response.data;
  }

  async createStrategy(data: any) {
    const response = await this.client.post('/strategies', data);
    return response.data;
  }

  async updateStrategy(id: string, data: any) {
    const response = await this.client.patch(`/strategies/${id}`, data);
    return response.data;
  }

  async activateStrategy(id: string) {
    const response = await this.client.post(`/strategies/${id}/activate`);
    return response.data;
  }

  async pauseStrategy(id: string) {
    const response = await this.client.post(`/strategies/${id}/pause`);
    return response.data;
  }

  async stopStrategy(id: string) {
    const response = await this.client.post(`/strategies/${id}/stop`);
    return response.data;
  }

  // Positions
  async getPositions() {
    const response = await this.client.get('/positions');
    return response.data;
  }

  // Analytics
  async getPnL(strategyId?: string) {
    const params = strategyId ? { strategy_id: strategyId } : {};
    const response = await this.client.get('/analytics/pnl', { params });
    return response.data;
  }

  async getMetrics(strategyId?: string) {
    const params = strategyId ? { strategy_id: strategyId } : {};
    const response = await this.client.get('/analytics/metrics', { params });
    return response.data;
  }
}

export const apiClient = new ApiClient();
