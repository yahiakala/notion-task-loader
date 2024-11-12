# Authorization System

This document explains how the `validate_user` function implements security through tenant verification and role-based authorization in the Notion Task Loader application.

## Overview

The `validate_user` function serves as the central security checkpoint for all tenant-related operations. It provides two critical security features:

1. Tenant Membership Verification
2. Role-Based Access Control (RBAC)

## Function Signature

```python
def validate_user(tenant_id, user, usertenant=None, permissions=None, tenant=None):
    """
    Validates a user's access to a tenant and returns their permissions.
    
    Args:
        tenant_id: The ID of the tenant to validate against
        user: The user object to validate
        usertenant: Optional pre-fetched UserTenant row
        permissions: Optional pre-fetched permissions
        tenant: Optional pre-fetched tenant row
    
    Returns:
        tuple: (tenant, usertenant, permissions)
    """
```

## Tenant Membership Verification

The function first verifies that a user belongs to the specified tenant:

1. Checks the UserTenant table for a link between the user and tenant:
```python
usertenant = usertenant or app_tables.usertenant.get(
    user=user,
    tenant=tenant
)
```

2. If no link exists, the user is not authorized:
```python
if not usertenant:
    raise Exception("User does not belong to this tenant")
```

This ensures that users can only access data from tenants they are members of.

## Role-Based Authorization

After verifying tenant membership, the function implements RBAC by:

1. Getting the user's roles for the tenant:
```python
roles = usertenant['roles']
```

2. Aggregating permissions from all roles:
```python
all_permissions = set()
for role in roles:
    role_permissions = role['permissions']
    all_permissions.update(p['name'] for p in role_permissions)
```

### Permission Hierarchy

The system uses a hierarchical permission structure:

1. Basic permissions (e.g., 'see_members')
2. Administrative permissions (e.g., 'delete_members')
3. Tenant-specific permissions (e.g., 'edit_tenant_settings')

## Usage in Helper Functions

Helper functions use validate_user to implement security checks:

```python
def get_users_iterable(tenant_id, user):
    """Get an iterable of the users."""
    tenant, usertenant, permissions = validate_user(tenant_id, user)
    
    # Check specific permission
    if 'see_members' not in permissions:
        return []
        
    # Return data only if authorized
    return app_tables.usertenant.client_readable(
        q.only_cols('user', 'first_name', 'last_name', 'notes'),
        tenant=tenant
    )
```

### Common Pattern

1. Call validate_user to get permissions
2. Check for required permission
3. Return data or empty result based on authorization

## Integration with Globals Pattern

The validate_user function integrates with the globals pattern:

1. Used in helper functions:
```python
def get_tenant_notion_info(tenant_id, user):
    tenant, usertenant, permissions = validate_user(tenant_id, user)
    
    if 'delete_members' not in permissions:
        return None
        
    return {
        'notion_api_key': tenant['notion_api_key'],
        'notion_db_id': tenant['notion_db_id']
    }
```

2. Centralized through get_tenanted_data:
```python
@anvil.server.callable(require_user=True)
def get_tenanted_data(tenant_id, key):
    user = anvil.users.get_user(allow_remembered=True)
    # Each helper function uses validate_user internally
    if key == 'users':
        return get_users_iterable(tenant_id, user)
```

## Security Best Practices

1. Always call validate_user before accessing tenant data
2. Check specific permissions for each operation
3. Return empty/null results instead of raising errors
4. Use consistent permission names across the application
5. Cache validation results when making multiple checks

## Error Handling

The function handles several error cases:

1. Invalid tenant ID:
```python
if not tenant:
    raise Exception("Tenant not found")
```

2. User not in tenant:
```python
if not usertenant:
    raise Exception("User does not belong to this tenant")
```

3. Missing required permissions:
```python
if required_permission not in permissions:
    return None  # Or empty list/dict depending on context
```

## Example Flows

### 1. Accessing User List

```python
# Client code
users = anvil.server.call('get_tenanted_data', Global.tenant_id, 'users')

# Server code
def get_users_iterable(tenant_id, user):
    tenant, usertenant, permissions = validate_user(tenant_id, user)
    if 'see_members' not in permissions:
        return []
    return app_tables.usertenant.client_readable(...)
```

### 2. Modifying Tenant Settings

```python
# Client code
result = anvil.server.call('save_tenant_notion', api_key, db_id)

# Server code
def save_tenant_notion(tenant_id, user, api_key, db_id):
    tenant, usertenant, permissions = validate_user(tenant_id, user)
    if 'edit_tenant_settings' not in permissions:
        raise Exception("Unauthorized")
    tenant.update(notion_api_key=api_key, notion_db_id=db_id)
```

## Testing Authorization

When testing authorization:

1. Verify tenant membership checks:
```python
def test_invalid_tenant():
    with pytest.raises(Exception):
        validate_user(invalid_tenant_id, user)
```

2. Test permission checks:
```python
def test_unauthorized_access():
    result = get_users_iterable(tenant_id, user_without_permission)
    assert len(result) == 0
```

This comprehensive security system ensures that data access is properly controlled and authorized throughout the application.
