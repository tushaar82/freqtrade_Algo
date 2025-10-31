/**
 * Navbar Component
 * VELOX Trading Platform
 */
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { LogOut, BarChart3 } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <BarChart3 className="h-8 w-8 text-primary-600" />
            <Link to="/dashboard" className="ml-2 text-xl font-bold text-gray-900">
              VELOX Trading
            </Link>
          </div>
          <div className="flex items-center space-x-4">
            <Link to="/dashboard" className="text-gray-700 hover:text-gray-900">
              Dashboard
            </Link>
            <Link to="/strategies" className="text-gray-700 hover:text-gray-900">
              Strategies
            </Link>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">{user?.email}</span>
              <button
                onClick={handleLogout}
                className="p-2 text-gray-600 hover:text-gray-900"
                title="Logout"
              >
                <LogOut className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};
