# Database optimization queries for PostgreSQL
# Run these periodically to maintain performance

-- Analyze all tables (updates statistics for query planner)
ANALYZE;

-- Vacuum database (reclaim space and update statistics)
VACUUM ANALYZE;

-- Find slow queries (add to postgresql.conf: log_min_duration_statement = 1000)
-- Then check: tail -f /var/log/postgresql/postgresql-14-main.log

-- Show table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Show index sizes
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_indexes
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_relation_size(indexrelid) DESC;

-- Find missing indexes (queries doing seq scans)
SELECT 
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    seq_tup_read / seq_scan AS avg_seq_tup
FROM pg_stat_user_tables
WHERE seq_scan > 0
ORDER BY seq_tup_read DESC
LIMIT 20;

-- Show active connections
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    state,
    query_start,
    state_change
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY query_start;

-- Kill idle connections older than 1 hour
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
  AND state_change < NOW() - INTERVAL '1 hour'
  AND pid != pg_backend_pid();

-- Database cache hit ratio (should be > 99%)
SELECT 
    sum(heap_blks_read) as heap_read,
    sum(heap_blks_hit)  as heap_hit,
    (sum(heap_blks_hit) - sum(heap_blks_read)) / sum(heap_blks_hit)::float * 100 AS cache_hit_ratio
FROM pg_statio_user_tables;

-- Create useful indexes for Fikrly (if not exists)
-- Run these in your production database after deployment

-- Companies
CREATE INDEX IF NOT EXISTS idx_company_category ON frontend_company(category_fk_id);
CREATE INDEX IF NOT EXISTS idx_company_city ON frontend_company(city);
CREATE INDEX IF NOT EXISTS idx_company_verified ON frontend_company(is_verified);
CREATE INDEX IF NOT EXISTS idx_company_active ON frontend_company(is_active);
CREATE INDEX IF NOT EXISTS idx_company_rating ON frontend_company(rating DESC);

-- Reviews
CREATE INDEX IF NOT EXISTS idx_review_company ON frontend_review(company_id);
CREATE INDEX IF NOT EXISTS idx_review_author ON frontend_review(author_id);
CREATE INDEX IF NOT EXISTS idx_review_approved ON frontend_review(is_approved);
CREATE INDEX IF NOT EXISTS idx_review_created ON frontend_review(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_review_rating ON frontend_review(rating);

-- User profiles
CREATE INDEX IF NOT EXISTS idx_userprofile_user ON frontend_userprofile(user_id);
CREATE INDEX IF NOT EXISTS idx_userprofile_verified ON frontend_userprofile(email_verified);

-- Activity logs
CREATE INDEX IF NOT EXISTS idx_activitylog_company ON frontend_activitylog(company_id);
CREATE INDEX IF NOT EXISTS idx_activitylog_review ON frontend_activitylog(review_id);
CREATE INDEX IF NOT EXISTS idx_activitylog_actor ON frontend_activitylog(actor_id);
CREATE INDEX IF NOT EXISTS idx_activitylog_created ON frontend_activitylog(created_at DESC);
