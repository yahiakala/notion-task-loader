# Database Schema Documentation

This document outlines the database structure for the Notion Task Loader application.

## Tables Overview

The application uses 5 main tables:
1. Users - Stores user authentication and profile data
2. Tenants - Manages tenant-specific configurations
3. Roles - Defines user roles within tenants
4. Permissions - Stores available permissions
5. UserTenant - Links users to tenants with their roles

## Detailed Table Structures

### Users Table
Stores user authentication and profile information.

| Column Name | Type | Description |
|------------|------|-------------|
| email | string | User's email address |
| enabled | boolean | Whether the user account is active |
| last_login | datetime | Timestamp of user's last login |
| password_hash | string | Hashed user password |
| n_password_failures | number | Count of failed password attempts |
| confirmed_email | boolean | Whether email has been confirmed |
| remembered_logins | simpleObject | Stored login session data |
| mfa | simpleObject | Multi-factor authentication settings |
| signed_up | datetime | Account creation timestamp |
| email_confirmation_key | string | Key for email verification |

### Tenants Table
Manages tenant-specific configurations.

| Column Name | Type | Description |
|------------|------|-------------|
| name | string | Tenant name |
| new_roles | simpleObject | Role configuration data |
| notion_api_key | string | Notion API integration key for the team workspace |
| notion_db_id | string | Notion database identifier for the team task database |
| notion_user_mapping | simpleObject | Maps app user emails to Notion user IDs |
| notion_users | simpleObject | Cached list of Notion workspace users |

### Roles Table
Defines roles within tenants.

| Column Name | Type | Description |
|------------|------|-------------|
| name | string | Role name |
| permissions | link_multiple | Links to permissions table |
| tenant | link_single | Link to associated tenant |
| can_edit | boolean | Whether user can make edits to this role |

### Permissions Table
Stores available permissions.

| Column Name | Type | Description |
|------------|------|-------------|
| name | string | Permission name |
| description | string | Permission description |

### UserTenant Table
Links users to tenants and their roles.

| Column Name | Type | Description |
|------------|------|-------------|
| user | link_single | Link to users table |
| tenant | link_single | Link to tenants table |
| roles | link_multiple | Links to roles table |
| notion_user_id | string | User's Notion user ID |
| notion_team_user_id | string | User's Notion team ID |
| notion_task_db_id | string | User's personal Notion task database ID |
| notion_api_key | string | User's personal Notion API key |

## Relationships

1. **User-Tenant Relationship**
   - Many-to-Many relationship through UserTenant table
   - Users can belong to multiple tenants
   - Tenants can have multiple users

2. **Role-Permission Relationship**
   - Many-to-Many relationship
   - Roles can have multiple permissions
   - Permissions can be assigned to multiple roles

3. **Role-Tenant Relationship**
   - Many-to-One relationship
   - Each role belongs to one tenant
   - Tenants can have multiple roles

## Access Control

- All tables have server-side "full" access
- Client-side access is set to "none" for all tables
- This indicates a security model where all database operations must go through server-side functions

## Notes

1. The schema implements a multi-tenant architecture with role-based access control (RBAC)
2. MFA (Multi-Factor Authentication) is supported through the users table
3. Notion integration is supported at both tenant and user levels:
   - Tenant level: API key, database ID, user mappings, and cached users
   - User level: Personal API key, user IDs, and task database ID
4. The system supports email verification and login session management
5. Password security features include failure counting and hashing
6. Notion user mappings are stored at the tenant level to maintain a centralized mapping between app users and Notion users
7. Notion users are cached at the tenant level to improve performance when displaying user dropdowns
