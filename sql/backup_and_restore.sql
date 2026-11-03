-- ============================================================================
-- ENTERPRISE RESOURCE & OPERATIONS MANAGEMENT SYSTEM (EROMS)
-- DATABASE BACKUP, RECOVERY & DISASTER RESTORATION PROCEDURES
-- Architect: Muhammad Afnan (https://github.com/Afnan-makstrix)
-- ============================================================================

/*
===============================================================================
1. PRODUCTION LOGICAL BACKUP (CLI / CRON)
===============================================================================
Command:
pg_dump -h localhost -p 5432 -U eroms_admin -F c -b -v -f /var/backups/eroms/eroms_enterprise_$(date +%Y%m%d_%H%M%S).dump eroms_enterprise_db

Explanation of Flags:
  -F c : Custom compressed PostgreSQL archive format (supports parallel restore & selective table recovery)
  -b   : Include large objects in dump
  -v   : Verbose progress reporting
  -f   : Output destination file path

===============================================================================
2. DISASTER RECOVERY RESTORATION (CLI)
===============================================================================
Step 1: Terminate active connections to the target database:
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE datname = 'eroms_enterprise_db' AND pid <> pg_backend_pid();

Step 2: Drop and recreate the empty target database:
DROP DATABASE IF EXISTS eroms_enterprise_db;
CREATE DATABASE eroms_enterprise_db OWNER eroms_admin;

Step 3: Execute pg_restore with multithreaded parallel worker jobs:
pg_restore -h localhost -p 5432 -U eroms_admin -d eroms_enterprise_db -v -j 4 /var/backups/eroms/eroms_enterprise_20261102_200000.dump

===============================================================================
3. PYTHON AUTOMATED CROSS-PLATFORM UTILITIES
===============================================================================
Backup:
  python scripts/backup_database.py eroms_enterprise_db

Restore:
  python scripts/restore_database.py database/backups/eroms_enterprise_db_TIMESTAMP.sql eroms_enterprise_db

===============================================================================
4. SCHEDULED DAILY MIDNIGHT BACKUP CRON CONFIGURATION
===============================================================================
0 0 * * * /usr/bin/python3 /app/scripts/backup_database.py eroms_enterprise_db >> /var/log/eroms_backup.log 2>&1
*/

-- Verification query to check database physical size, table sizes, and dead tuples:
SELECT 
    schemaname,
    relname AS table_name,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
    pg_size_pretty(pg_relation_size(relid)) AS table_data_size,
    pg_size_pretty(pg_indexes_size(relid)) AS index_size,
    n_live_tup AS live_tuples,
    n_dead_tup AS dead_tuples,
    last_vacuum,
    last_autovacuum,
    last_analyze
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC;
