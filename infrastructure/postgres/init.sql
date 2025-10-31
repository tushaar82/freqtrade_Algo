-- VELOX Trading Platform Database Initialization
-- Created: 2025-10-31

-- Create database (already created by Docker, but included for reference)
-- CREATE DATABASE velox_trading;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For text search

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE velox_trading TO velox;

-- Create schema for partitioned tables (future use)
CREATE SCHEMA IF NOT EXISTS partitions;

-- Initial setup complete
SELECT 'VELOX Trading Platform database initialized successfully' AS status;
