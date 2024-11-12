import anvil.server
import anvil.users
from anvil.tables import app_tables

from .globals import get_permissions, get_tenant_single
from .helpers import print_timestamp, verify_tenant, validate_user, get_usertenant, get_users_with_permission, populate_roles, usertenant_row_to_dict


@anvil.server.callable(require_user=True)
def create_tenant_single():
    """Create a tenant."""
    user = anvil.users.get_user(allow_remembered=True)
    if len(app_tables.tenants.search()) != 0:
        return None

    tenant = app_tables.tenants.add_row(name='Main', new_roles=['Member'])
    _ = populate_roles(tenant)
    admin_role = app_tables.roles.get(tenant=tenant, name='Admin')
    _ = app_tables.usertenant.add_row(tenant=tenant, user=user, roles=[admin_role])
    return get_tenant_single(user, tenant)


@anvil.server.callable(require_user=True)
def save_tenant_notion(tenant_id, api_key, db_id):
    """Save Notion API key and database ID for a tenant.
    
    Args:
        tenant_id: The ID of the tenant to update
        api_key: The Notion API key for the team workspace
        db_id: The Notion database ID for the team task database
    """
    user = anvil.users.get_user(allow_remembered=True)
    
    # Validate user has permission to edit tenant settings
    tenant, usertenant, permissions = validate_user(tenant_id, user)
    if 'delete_members' not in permissions:
        raise Exception("Unauthorized")
    
    # Update tenant with new Notion info
    tenant.update(
        notion_api_key=api_key,
        notion_db_id=db_id
    )
