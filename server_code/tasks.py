import anvil.server
import anvil.users
from anvil.tables import app_tables

from .globals import get_permissions, get_tenant_single
from .helpers import print_timestamp, verify_tenant, validate_user, get_usertenant, get_users_with_permission, populate_roles, usertenant_row_to_dict
from .notion import create_task, get_workspace_users


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
        
    Returns:
        dict: Updated tenant notion info containing notion_api_key and notion_db_id
    """
    user = anvil.users.get_user(allow_remembered=True)
    
    # Validate user has permission to edit tenant settings
    tenant, usertenant, permissions = validate_user(tenant_id, user)
    if 'delete_members' not in permissions:
        raise Exception("Unauthorized")
    
    # Get and print workspace users before updating tenant
    try:
        workspace_users = get_workspace_users(api_key)
        print("Notion Workspace Users:")
        for user in workspace_users:
            print(user)
    except Exception as e:
        print(f"Error getting workspace users: {str(e)}")
        # Continue with tenant update even if getting users fails
    
    # Update tenant with new Notion info
    tenant.update(
        notion_api_key=api_key,
        notion_db_id=db_id
    )
    
    # Return updated tenant notion info
    return {
        'notion_api_key': api_key,
        'notion_db_id': db_id
    }


@anvil.server.callable(require_user=True)
def save_user_notion(tenant_id, notion_api_key, notion_db_id, notion_user_id, notion_team_user_id):
    """Save Notion settings for a user's tenant.
    
    Args:
        tenant_id: The ID of the tenant to update
        notion_api_key: The Notion API key for personal workspace
        notion_db_id: The Notion database ID for personal task database
        notion_user_id: The user's Notion user ID
        notion_team_user_id: The user's Notion team user ID
    """
    user = anvil.users.get_user(allow_remembered=True)
    tenant, usertenant, permissions = validate_user(tenant_id, user)
    
    # Update the UserTenant row with new Notion settings
    usertenant.update(
        notion_api_key=notion_api_key,
        notion_task_db_id=notion_db_id,
        notion_user_id=notion_user_id,
        notion_team_user_id=notion_team_user_id
    )
    
    return usertenant_row_to_dict(usertenant)


@anvil.server.callable(require_user=True)
def send_to_personal_notion(tenant_id, title, description):
    """Send a task to the user's personal Notion workspace.
    
    Args:
        tenant_id: The ID of the tenant
        title: The task title
        description: The task description
    """
    user = anvil.users.get_user(allow_remembered=True)
    tenant, usertenant, permissions = validate_user(tenant_id, user)
    
    # Get user's personal Notion settings
    notion_api_key = usertenant['notion_api_key']
    notion_db_id = usertenant['notion_task_db_id']
    
    if not notion_api_key or not notion_db_id:
        raise Exception("Personal Notion workspace not configured")
        
    # Create task in personal workspace without status or user assignment
    return create_task(
        title=title,
        description=description,
        database_id=notion_db_id,
        api_key=notion_api_key
    )


@anvil.server.callable(require_user=True)
def send_to_team_notion(tenant_id, title, description):
    """Send a task to the team's Notion workspace.
    
    Args:
        tenant_id: The ID of the tenant
        title: The task title
        description: The task description
    """
    user = anvil.users.get_user(allow_remembered=True)
    tenant, usertenant, permissions = validate_user(tenant_id, user)
    
    # Get team's Notion settings
    notion_api_key = tenant['notion_api_key']
    notion_db_id = tenant['notion_db_id']
    notion_team_user_id = usertenant['notion_team_user_id']
    
    if not notion_api_key or not notion_db_id:
        raise Exception("Team Notion workspace not configured")
        
    # Create task in team workspace with Draft status and user assignment
    return create_task(
        title=title,
        description=description,
        database_id=notion_db_id,
        api_key=notion_api_key,
        status="Draft"
    )
