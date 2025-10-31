/**
 * Position Table Component
 * VELOX Trading Platform
 */
import React from 'react';

interface Position {
  id: string;
  symbol: string;
  side: string;
  quantity: number;
  entry_price: number;
  current_price: number;
  unrealized_pnl: number;
}

interface PositionTableProps {
  positions: Position[];
}

export const PositionTable: React.FC<PositionTableProps> = ({ positions }) => {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Symbol</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Side</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quantity</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Entry</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Current</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">P&L</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {positions.map((position) => (
            <tr key={position.id}>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {position.symbol}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm">
                <span className={`px-2 py-1 rounded ${position.side === 'LONG' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                  {position.side}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{position.quantity}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">₹{position.entry_price.toFixed(2)}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">₹{position.current_price.toFixed(2)}</td>
              <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${position.unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                ₹{position.unrealized_pnl.toFixed(2)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {positions.length === 0 && (
        <div className="text-center py-8 text-gray-500">No active positions</div>
      )}
    </div>
  );
};
