# VELOX Trading Platform - Frontend

React + TypeScript frontend for the VELOX multi-strategy trading platform.

## Setup

```bash
npm install
```

## Configuration

Create `.env` file:
```
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_WS_URL=ws://localhost:8000/ws
```

## Development

```bash
npm start
```

Runs on http://localhost:3000

## Build

```bash
npm run build
```

## Features

- Real-time dashboard with WebSocket streaming
- Strategy management (CRUD + lifecycle control)
- Live position tracking
- P&L charts and metrics
- Authentication with JWT

## Tech Stack

- React 18
- TypeScript
- TailwindCSS
- Recharts
- Axios
- React Router
- Lucide Icons
