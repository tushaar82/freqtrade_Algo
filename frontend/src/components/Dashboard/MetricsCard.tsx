/**
 * Metrics Card Component
 * VELOX Trading Platform
 */
import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface MetricsCardProps {
  title: string;
  value: string | number;
  change?: number;
  format?: 'currency' | 'percentage' | 'number';
}

export const MetricsCard: React.FC<MetricsCardProps> = ({ title, value, change, format = 'number' }) => {
  const formatValue = (val: string | number) => {
    if (format === 'currency') {
      return `₹${Number(val).toFixed(2)}`;
    } else if (format === 'percentage') {
      return `${Number(val).toFixed(2)}%`;
    }
    return val;
  };

  const isPositive = change !== undefined && change >= 0;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="mt-2 text-3xl font-semibold text-gray-900">{formatValue(value)}</p>
          {change !== undefined && (
            <div className={`mt-2 flex items-center text-sm ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
              {isPositive ? <TrendingUp className="h-4 w-4 mr-1" /> : <TrendingDown className="h-4 w-4 mr-1" />}
              <span>{Math.abs(change).toFixed(2)}%</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
