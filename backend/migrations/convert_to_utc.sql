-- Migration script to convert existing timestamp data from local time to UTC
-- This script should be run once to migrate existing data

-- Note: This assumes your MySQL server is currently set to a specific timezone
-- You may need to adjust the CONVERT_TZ function parameters based on your server's current timezone

-- For repositories table in main database (doc2dev)
USE doc2dev;

-- Update existing records to convert from local time to UTC
-- Replace 'SYSTEM' with your actual server timezone if different (e.g., '+08:00' for China)
UPDATE repositories 
SET 
    created_at = CONVERT_TZ(created_at, @@session.time_zone, '+00:00'),
    updated_at = CONVERT_TZ(updated_at, @@session.time_zone, '+00:00')
WHERE created_at IS NOT NULL OR updated_at IS NOT NULL;

-- For users table in user management database (doc2dev_users)
USE doc2dev_users;

-- Update existing user records
UPDATE users 
SET 
    created_at = CONVERT_TZ(created_at, @@session.time_zone, '+00:00'),
    updated_at = CONVERT_TZ(updated_at, @@session.time_zone, '+00:00')
WHERE created_at IS NOT NULL OR updated_at IS NOT NULL;

-- Note: For user-specific databases (doc2dev_user_*), you would need to run similar
-- UPDATE statements for each user database. This can be done programmatically
-- or manually for each existing user database.

-- Example for a specific user database (replace with actual user database name):
-- USE doc2dev_user_12345678_1234_1234_1234_123456789012;
-- UPDATE repositories 
-- SET 
--     created_at = CONVERT_TZ(created_at, @@session.time_zone, '+00:00'),
--     updated_at = CONVERT_TZ(updated_at, @@session.time_zone, '+00:00')
-- WHERE created_at IS NOT NULL OR updated_at IS NOT NULL;
