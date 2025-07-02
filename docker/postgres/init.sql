-- Initialize database for image2model application
-- This script runs when the PostgreSQL container starts for the first time

-- Create extensions if they don't exist
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Set timezone
SET timezone = 'UTC';

-- Create initial tables if needed (these will be created by FastAPI/SQLAlchemy migrations)
-- This file serves as a placeholder for any initial database setup

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Image2Model database initialization completed successfully';
END $$;