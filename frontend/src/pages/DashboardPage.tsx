/**
 * Dashboard Page
 * VELOX Trading Platform
 */
import React, { useEffect, useState } from 'react';
import { Navbar } from '../components/common/Navbar';
import { Card } from '../components/common/Card';
import { MetricsCard } from '../components/Dashboard/MetricsCard';
import { PnLChart } from '../components/Dashboard/PnLChart';
import { PositionTable } from '../components/Dashboard/PositionTable';
import { apiClient } from '../services/api';
import { useWebSocket } from '../hooks/useWebSocket';

export const DashboardPage: React.FC = () => {
  const [pnl, setPnl] = useState({ realized_pnl: 0, unrealized_pnl: 0, total_pnl: 0, daily_pnl: 0 });
  const [positions, setPositions] = useState([]);
  const [pnlHistory, setPnlHistory] = useState<Array<{ timestamp: string; pnl: number }>>([]);
  const { subscribe, on } = useWebSocket();

  useEffect(() => {
    loadData();
    
    // Subscribe to real-time updates
    subscribe(['pnl-updates', 'position-updates']);
    
    on('PNL_UPDATE', (data) => {
      setPnl(data);
      setPnlHistory(prev => [...prev, { timestamp: new Date().toLocaleTimeString(), pnl: data.total_pnl }].slice(-20));
    });
    
    on('POSITION_UPDATE', (data) => {
      setPositions(prev => {
        const index = prev.findIndex((p: any) => p.id === data.position_id);
        if (index >= 0) {
          const updated = [...prev];
          updated[index] = data;
          return updated;
        }
        return [...prev, data];
      });
    });
  }, [subscribe, on]);

  const loadData = async () => {
    try {
      const [pnlData, positionsData] = await Promise.all([
        apiClient.getPnL(),
        apiClient.getPositions()
      ]);
      setPnl(pnlData);
      setPositions(positionsData.positions || []);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <MetricsCard title="Total P&L" value={pnl.total_pnl} format="currency" />
          <MetricsCard title="Realized P&L" value={pnl.realized_pnl} format="currency" />
          <MetricsCard title="Unrealized P&L" value={pnl.unrealized_pnl} format="currency" />
          <MetricsCard title="Daily P&L" value={pnl.daily_pnl} format="currency" />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <Card title="P&L Chart">
            <PnLChart data={pnlHistory} />
          </Card>
          <Card title="Performance Metrics">
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-gray-600">Sharpe Ratio</span>
                <span className="font-semibold">0.00</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Max Drawdown</span>
                <span className="font-semibold">0.00%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Win Rate</span>
                <span className="font-semibold">0.00%</span>
              </div>
            </div>
          </Card>
        </div>

        <Card title="Active Positions">
          <PositionTable positions={positions} />
        </Card>
      </div>
    </div>
  );
};
