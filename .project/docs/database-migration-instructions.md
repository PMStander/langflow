# Database Migration Instructions for CRM Module Indexes

## Overview

This document provides instructions for running the database migration to add indexes to frequently queried fields in the CRM module. These indexes will improve query performance, especially for large datasets.

## Prerequisites

Before running the migration, ensure that:

1. You have the necessary permissions to modify the database schema
2. You have a backup of the database in case of any issues
3. The Langflow application is not running during the migration
4. You have the latest version of the codebase

## Migration Details

The migration will add the following indexes to the database:

1. `Task.status` - Used in dashboard queries and filtering
2. `Task.priority` - Used in filtering
3. `Task.due_date` - Used in filtering and sorting
4. `Opportunity.status` - Used in dashboard queries and filtering
5. `Opportunity.expected_close_date` - Used in filtering and sorting

## Running the Migration

### Option 1: Using Alembic (Recommended)

1. Navigate to the backend directory:

```bash
cd src/backend
```

2. Run the Alembic migration:

```bash
alembic upgrade head
```

3. Verify that the migration was successful:

```bash
alembic current
```

The output should show the latest migration ID.

### Option 2: Manual SQL Execution

If you prefer to run the SQL statements directly, you can use the following commands:

```sql
-- Add index to Task.status
CREATE INDEX IF NOT EXISTS ix_task_status ON task (status);

-- Add index to Task.priority
CREATE INDEX IF NOT EXISTS ix_task_priority ON task (priority);

-- Add index to Task.due_date
CREATE INDEX IF NOT EXISTS ix_task_due_date ON task (due_date);

-- Add index to Opportunity.status
CREATE INDEX IF NOT EXISTS ix_opportunity_status ON opportunity (status);

-- Add index to Opportunity.expected_close_date
CREATE INDEX IF NOT EXISTS ix_opportunity_expected_close_date ON opportunity (expected_close_date);
```

## Verifying the Indexes

After running the migration, you can verify that the indexes were created by running the following SQL query:

```sql
SELECT
    tablename,
    indexname,
    indexdef
FROM
    pg_indexes
WHERE
    schemaname = 'public'
    AND (tablename = 'task' OR tablename = 'opportunity')
ORDER BY
    tablename,
    indexname;
```

## Rollback Instructions

If you need to roll back the migration, you can use one of the following methods:

### Option 1: Using Alembic

```bash
cd src/backend
alembic downgrade -1
```

### Option 2: Manual SQL Execution

```sql
-- Remove index from Task.status
DROP INDEX IF EXISTS ix_task_status;

-- Remove index from Task.priority
DROP INDEX IF EXISTS ix_task_priority;

-- Remove index from Task.due_date
DROP INDEX IF EXISTS ix_task_due_date;

-- Remove index from Opportunity.status
DROP INDEX IF EXISTS ix_opportunity_status;

-- Remove index from Opportunity.expected_close_date
DROP INDEX IF EXISTS ix_opportunity_expected_close_date;
```

## Performance Impact

Adding these indexes should improve the performance of the following operations:

1. Dashboard statistics queries
2. Filtered list views
3. Sorting by indexed fields

However, there might be a slight performance impact on write operations (INSERT, UPDATE, DELETE) as the indexes need to be updated. This impact should be minimal compared to the performance gains for read operations.

## Troubleshooting

If you encounter any issues during the migration, try the following:

1. Check the Alembic logs for error messages
2. Verify that the database user has the necessary permissions
3. Ensure that there are no conflicting indexes
4. Check if the tables already have the indexes (the migration should handle this case)

If the issues persist, you can roll back the migration using the instructions above and contact the development team for assistance.
