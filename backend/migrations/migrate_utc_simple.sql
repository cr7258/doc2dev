-- Simple UTC migration script
-- This script converts existing timestamp data from UTC+8 to UTC

-- Check current timezone and time
SELECT 'Current timezone and time comparison:' as info;
SELECT @@global.time_zone as global_tz, @@session.time_zone as session_tz, NOW() as local_now, UTC_TIMESTAMP() as utc_now;

-- Show sample data before migration
SELECT 'Sample data BEFORE migration:' as info;
SELECT id, name, created_at, updated_at FROM doc2dev.repositories ORDER BY id DESC LIMIT 3;

-- Convert doc2dev.repositories table
USE doc2dev;
UPDATE repositories 
SET 
    created_at = DATE_SUB(created_at, INTERVAL 8 HOUR),
    updated_at = DATE_SUB(updated_at, INTERVAL 8 HOUR)
WHERE created_at IS NOT NULL OR updated_at IS NOT NULL;

SELECT CONCAT('Updated ', ROW_COUNT(), ' records in doc2dev.repositories') as result;

-- Convert doc2dev_users.users table  
USE doc2dev_users;
UPDATE users 
SET 
    created_at = DATE_SUB(created_at, INTERVAL 8 HOUR),
    updated_at = DATE_SUB(updated_at, INTERVAL 8 HOUR)
WHERE created_at IS NOT NULL OR updated_at IS NOT NULL;

SELECT CONCAT('Updated ', ROW_COUNT(), ' records in doc2dev_users.users') as result;

-- Show sample data after migration
USE doc2dev;
SELECT 'Sample data AFTER migration:' as info;
SELECT id, name, created_at, updated_at FROM repositories ORDER BY id DESC LIMIT 3;

SELECT 'Migration completed! All timestamps converted from UTC+8 to UTC.' as final_message;
