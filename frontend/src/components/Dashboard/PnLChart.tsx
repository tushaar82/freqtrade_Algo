/**
 * P&L Chart Component
 * VELOX Trading Platform
 */
import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface PnLChartProps {
  data: Array<{ timestamp: string; pnl: number }>;
}

export const PnLChart: React.FC<PnLChartProps> = ({ data }) => {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="timestamp" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="pnl" stroke="#3b82f6" strokeWidth={2} name="P&L" />
      </LineChart>
    </ResponsiveContainer>
  );
};
