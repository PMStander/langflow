# Supabase Auth Integration

This document provides detailed information about the Supabase Auth integration in Langflow.

## Overview

Langflow now supports authentication through Supabase Auth, allowing you to leverage Supabase's authentication system while preserving Langflow's existing functionality. This integration enables:

- User registration and login through Supabase Auth
- Synchronization of users between Supabase and Langflow's internal database
- Preservation of Langflow's role-based access control
- Automatic assignment of superuser role to the first user

## Prerequisites

To use Supabase Auth with Langflow, you need:

1. A Supabase project with Auth enabled
2. The Supabase project URL
3. The Supabase anon key

## Configuration

### Environment Variables

Add the following environment variables to your `.env` file:

```
# Supabase Auth Configuration
# Set to true to enable Supabase Auth
LANGFLOW_SUPABASE_AUTH_ENABLED=true
LANGFLOW_SUPABASE_URL=https://your-project-id.supabase.co
LANGFLOW_SUPABASE_KEY=your-supabase-anon-key
```

Replace `your-project-id` and `your-supabase-anon-key` with your actual Supabase project ID and anon key.

### Database Migration

The Supabase Auth integration requires a new field in the User model to store the Supabase user ID. This migration is automatically applied when Langflow starts with `LANGFLOW_FIX_MIGRATIONS=true` in your `.env` file.

## How It Works

### User Registration

When a user registers:

1. A user is created in Supabase Auth
2. A corresponding user is created in Langflow's internal database
3. The Supabase user ID is stored in the internal user record
4. If this is the first user, they are assigned the superuser role

### User Login

When a user logs in:

1. The system tries to authenticate with Supabase Auth
2. If successful, it finds or creates the corresponding internal user
3. If Supabase Auth fails or is disabled, it falls back to internal authentication
4. Authentication tokens for both systems are returned to the client

### Token Management

The system manages two types of tokens:

1. **Internal Tokens**: JWT tokens used for Langflow's internal authentication
2. **Supabase Tokens**: Tokens used for Supabase Auth

Both types of tokens are returned to the client and stored in cookies.

### User Synchronization

Users are synchronized between Supabase and Langflow's internal database:

- When a user signs up or logs in with Supabase Auth, a corresponding user is created or updated in Langflow's internal database
- The Supabase user ID is stored in the internal user record to link the two accounts

## API Endpoints

The Supabase Auth integration adds or modifies the following API endpoints:

- `/api/v1/register`: Register a new user with Supabase Auth and internal database
- `/api/v1/login`: Log in with Supabase Auth or internal authentication
- `/api/v1/logout`: Log out from both Supabase Auth and internal authentication

## Supabase Auth Features

By integrating with Supabase Auth, you can leverage the following features:

- Email verification
- Password reset
- OAuth providers (Google, GitHub, etc.)
- Multi-factor authentication
- User management through Supabase dashboard

To enable these features, you need to configure them in your Supabase project.

## Troubleshooting

If you encounter issues with Supabase Auth integration:

1. Check that your environment variables are correctly set
2. Ensure that your Supabase project is properly configured
3. Check the Langflow logs for any authentication-related errors
4. Verify that the database migration for the `supabase_user_id` field has been applied

## Limitations

- The Supabase Auth integration currently supports email/password authentication only
- OAuth providers require additional frontend integration
- User roles are managed by Langflow, not Supabase

## Security Considerations

- Supabase Auth tokens are stored in cookies
- Internal tokens are stored in HTTP-only cookies
- Passwords are never stored in Langflow's database in plain text
- All communication with Supabase is done over HTTPS
