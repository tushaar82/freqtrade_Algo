/**
 * Auth Service
 * VELOX Trading Platform
 */
import { apiClient } from './api';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
}

export const authService = {
  async login(email: string, password: string): Promise<{ user: User; access_token: string }> {
    const response = await apiClient.login(email, password);
    localStorage.setItem('access_token', response.access_token);
    localStorage.setItem('refresh_token', response.refresh_token);
    localStorage.setItem('user', JSON.stringify(response.user));
    return response;
  },

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  },

  getUser(): User | null {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  getToken(): string | null {
    return localStorage.getItem('access_token');
  },

  isAuthenticated(): boolean {
    return !!this.getToken();
  },
};
