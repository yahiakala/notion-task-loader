# Globals Design Pattern

This document explains the globals design pattern used in the Notion Task Loader application, which provides a structured way to manage global state and server-side data access.

## Overview

The globals pattern consists of three main components:

1. Client-side global state (`client_code/Global.py`)
2. Server-side globals module (`server_code/globals.py`)
3. Client-server interaction through callable functions

This pattern enforces security by ensuring all database operations go through server-side functions while maintaining clean separation of concerns.

## Client-Side Global State

The client-side Global module maintains application state that needs to be accessible across different forms and components. This includes:

- User information
- Tenant ID
- Session data
- Cached data

Example usage in a form:
```python
from ...Global import Global

class MyForm:
    def form_show(self):
        tenant_id = Global.tenant_id
        data = anvil.server.call('get_tenanted_data', tenant_id, 'some_key')
```

## Server-Side Globals Structure

The server-side globals module (`server_code/globals.py`) follows a specific structure:

### 1. Non-Tenanted Globals

These are top-level functions that don't require tenant context:

```python
@anvil.server.callable(require_user=True)
def get_data(key):
    if key == 'all_permissions':
        return get_all_permissions()
```

### 2. Tenanted Globals

These functions require tenant context and follow a specific pattern:

1. A single callable entry point: `get_tenanted_data`
```python
@anvil.server.callable(require_user=True)
def get_tenanted_data(tenant_id, key):
    user = anvil.users.get_user(allow_remembered=True)
    
    if key == 'users':
        return get_users_iterable(tenant_id, user)
    elif key == 'permissions':
        return get_permissions(tenant_id, user)
```

2. Helper functions that implement specific functionality:
```python
def get_users_iterable(tenant_id, user):
    """Get an iterable of the users."""
    tenant, usertenant, permissions = validate_user(tenant_id, user)
    if 'see_members' not in permissions:
        return []
    return app_tables.usertenant.client_readable(...)
```

This structure provides several benefits:
- Centralized permission checking
- Consistent error handling
- Clear separation of concerns
- Reduced code duplication

## Function Structure

### 1. Callable Functions

Callable functions are decorated with `@anvil.server.callable` and often require authentication:
```python
@anvil.server.callable(require_user=True)
def get_tenanted_data(tenant_id, key):
    # Implementation
```

These functions:
- Are directly accessible from client code
- Handle parameter validation
- Manage user authentication
- Route to appropriate helper functions

### 2. Helper Functions

Helper functions implement specific functionality and are not directly callable:
```python
def get_tenant_notion_info(tenant_id, user):
    """Get Notion-related information for a tenant"""
    tenant, usertenant, permissions = validate_user(tenant_id, user)
    if 'delete_members' not in permissions:
        return None
    return {
        'notion_api_key': tenant['notion_api_key'],
        'notion_db_id': tenant['notion_db_id']
    }
```

These functions:
- Are called by callable functions
- Implement specific business logic
- Handle permission checking
- Access database tables

## Security Considerations

1. Permission Checking
   - Helper functions validate user permissions
   - Uses `validate_user` to check tenant access
   - Returns None or empty data if permissions are insufficient

2. Data Access
   - No direct database access from client code
   - All database operations go through server functions
   - Sensitive data is filtered before returning to client

## Best Practices

1. Always use `get_tenanted_data` for tenant-specific operations
2. Implement new functionality as helper functions
3. Add new keys to `get_tenanted_data` for accessing helper functions
4. Include proper permission checks in helper functions
5. Document function purposes and parameters
6. Use consistent error handling patterns
7. Keep helper functions focused and single-purpose

## Example Flow

1. Client needs tenant notion info:
```python
# Client code
notion_info = anvil.server.call('get_tenanted_data', Global.tenant_id, 'tenant_notion_info')
```

2. Server handles request:
```python
# Server code - callable function
@anvil.server.callable(require_user=True)
def get_tenanted_data(tenant_id, key):
    if key == 'tenant_notion_info':
        return get_tenant_notion_info(tenant_id, user)

# Server code - helper function
def get_tenant_notion_info(tenant_id, user):
    tenant, usertenant, permissions = validate_user(tenant_id, user)
    if 'delete_members' not in permissions:
        return None
    return {
        'notion_api_key': tenant['notion_api_key'],
        'notion_db_id': tenant['notion_db_id']
    }
```

This pattern ensures secure, maintainable, and scalable global state management across the application.
