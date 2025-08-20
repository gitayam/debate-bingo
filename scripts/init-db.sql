-- Create test database for running tests
CREATE DATABASE debate_bingo_test;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE debate_bingo_dev TO postgres;
GRANT ALL PRIVILEGES ON DATABASE debate_bingo_test TO postgres;