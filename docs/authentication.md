# Langflow Authentication System

Langflow provides a flexible authentication system that supports both internal authentication and Supabase Auth integration. This document explains how the authentication system works and how to configure it.

## Authentication Methods

Langflow supports two authentication methods:

1. **Internal Authentication**: The default authentication method that uses Langflow's built-in user management system.
2. **Supabase Auth**: Integration with Supabase Auth for user management and authentication.

Both methods can be used simultaneously, providing a seamless authentication experience for users.

## Configuration

### Internal Authentication

Internal authentication is enabled by default and requires no additional configuration. You can configure the following settings in your `.env` file:

```
# Set AUTO_LOGIN to false if you want to disable auto login
# and use the login form to login. LANGFLOW_SUPERUSER and LANGFLOW_SUPERUSER_PASSWORD
# must be set if AUTO_LOGIN is set to false
LANGFLOW_AUTO_LOGIN=true

# Superuser username
LANGFLOW_SUPERUSER=admin

# Superuser password
LANGFLOW_SUPERUSER_PASSWORD=admin
```

### Supabase Auth Integration

To enable Supabase Auth integration, you need to set the following environment variables in your `.env` file:

```
# Supabase Auth Configuration
# Set to true to enable Supabase Auth
LANGFLOW_SUPABASE_AUTH_ENABLED=true
LANGFLOW_SUPABASE_URL=https://your-project-id.supabase.co
LANGFLOW_SUPABASE_KEY=your-supabase-anon-key
```

Replace `your-project-id` and `your-supabase-anon-key` with your actual Supabase project ID and anon key.

## User Management

### User Creation

Users can be created in two ways:

1. **Internal User Creation**: Users are created in Langflow's internal database.
2. **Supabase User Creation**: When Supabase Auth is enabled, users are created in both Supabase and Langflow's internal database.

The first user created in the system is automatically assigned the superuser role, regardless of the authentication method used.

### User Synchronization

When Supabase Auth is enabled, users are synchronized between Supabase and Langflow's internal database:

- When a user signs up or logs in with Supabase Auth, a corresponding user is created or updated in Langflow's internal database.
- The Supabase user ID is stored in the internal user record to link the two accounts.

## Authentication Flow

### Registration

When a user registers:

1. If Supabase Auth is enabled, the user is created in Supabase Auth.
2. The user is created in Langflow's internal database.
3. If this is the first user, they are assigned the superuser role.
4. Authentication tokens are generated and returned to the client.

### Login

When a user logs in:

1. If Supabase Auth is enabled, the system tries to authenticate with Supabase Auth first.
2. If Supabase Auth succeeds, the system finds or creates the corresponding internal user.
3. If Supabase Auth fails or is disabled, the system falls back to internal authentication.
4. Authentication tokens are generated and returned to the client.

### Token Management

The authentication system manages two types of tokens:

1. **Internal Tokens**: JWT tokens used for internal authentication.
2. **Supabase Tokens**: Tokens used for Supabase Auth (when enabled).

Both types of tokens are returned to the client and stored in cookies.

### Logout

When a user logs out:

1. Internal authentication tokens are cleared.
2. If Supabase Auth is enabled, Supabase authentication tokens are cleared and the Supabase session is terminated.

## API Endpoints

The authentication system provides the following API endpoints:

- `/api/v1/login`: Log in with username and password
- `/api/v1/register`: Register a new user
- `/api/v1/logout`: Log out the current user
- `/api/v1/refresh`: Refresh the authentication tokens
- `/api/v1/auto_login`: Auto-login for development (if enabled)

## Security Considerations

- All passwords are hashed using bcrypt before being stored in the database.
- Authentication tokens have configurable expiration times.
- Refresh tokens are used to obtain new access tokens without requiring the user to log in again.
- HTTP-only cookies are used to store tokens to prevent XSS attacks.

## Troubleshooting

If you encounter issues with authentication:

1. Check that your environment variables are correctly set.
2. Ensure that your Supabase project is properly configured (if using Supabase Auth).
3. Check the Langflow logs for any authentication-related errors.
4. Verify that the database migration for the `supabase_user_id` field has been applied.

## Extending the Authentication System

The authentication system is designed to be extensible. You can add support for additional authentication methods by:

1. Creating a new authentication service.
2. Updating the `authenticate_user` function to support the new method.
3. Adding the necessary API endpoints for the new method.
