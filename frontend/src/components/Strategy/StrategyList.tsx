/**
 * Strategy List Component
 * VELOX Trading Platform
 */
import React, { useEffect, useState } from 'react';
import { apiClient } from '../../services/api';
import { Play, Pause, Square } from 'lucide-react';

interface Strategy {
  id: string;
  name: string;
  strategy_type: string;
  status: string;
  mode: string;
}

export const StrategyList: React.FC = () => {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStrategies();
  }, []);

  const loadStrategies = async () => {
    try {
      const data = await apiClient.getStrategies();
      setStrategies(data);
    } catch (error) {
      console.error('Failed to load strategies:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleActivate = async (id: string) => {
    try {
      await apiClient.activateStrategy(id);
      loadStrategies();
    } catch (error) {
      console.error('Failed to activate strategy:', error);
    }
  };

  const handlePause = async (id: string) => {
    try {
      await apiClient.pauseStrategy(id);
      loadStrategies();
    } catch (error) {
      console.error('Failed to pause strategy:', error);
    }
  };

  const handleStop = async (id: string) => {
    try {
      await apiClient.stopStrategy(id);
      loadStrategies();
    } catch (error) {
      console.error('Failed to stop strategy:', error);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="space-y-4">
      {strategies.map((strategy) => (
        <div key={strategy.id} className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold">{strategy.name}</h3>
              <p className="text-sm text-gray-600">{strategy.strategy_type}</p>
              <div className="mt-2 flex items-center space-x-2">
                <span className={`px-2 py-1 text-xs rounded ${
                  strategy.status === 'PAPER_TRADING' ? 'bg-green-100 text-green-800' :
                  strategy.status === 'PAUSED' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {strategy.status}
                </span>
                <span className="px-2 py-1 text-xs rounded bg-blue-100 text-blue-800">
                  {strategy.mode}
                </span>
              </div>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => handleActivate(strategy.id)}
                className="p-2 text-green-600 hover:bg-green-50 rounded"
                title="Activate"
              >
                <Play className="h-5 w-5" />
              </button>
              <button
                onClick={() => handlePause(strategy.id)}
                className="p-2 text-yellow-600 hover:bg-yellow-50 rounded"
                title="Pause"
              >
                <Pause className="h-5 w-5" />
              </button>
              <button
                onClick={() => handleStop(strategy.id)}
                className="p-2 text-red-600 hover:bg-red-50 rounded"
                title="Stop"
              >
                <Square className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
