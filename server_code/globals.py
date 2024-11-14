# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import anvil.server
import anvil.tables.query as q
import anvil.users
from anvil.tables import app_tables
from anvil_squared.helpers import print_timestamp

from .helpers import get_permissions, usertenant_row_to_dict, validate_user


# --------------------
# Non tenanted globals
# --------------------
@anvil.server.callable(require_user=True)
def get_data(key):
    print_timestamp(f"get_data: {key}")
    # user = anvil.users.get_user(allow_remembered=True)
    if key == "all_permissions":
        return get_all_permissions()


@anvil.server.callable()
def get_tenant_single(user=None, tenant=None):
    """Get the tenant in this instance."""
    user = anvil.users.get_user(allow_remembered=True)
    tenant = tenant or app_tables.tenants.get()

    if not tenant:
        return None

    tenant_dict = {"id": tenant.get_id(), "name": tenant["name"]}
    if user:
        tenant, usertenant, permissions = validate_user(
            tenant.get_id(), user, tenant=tenant
        )
        if "delete_members" in permissions:
            # TODO: do not return client writable
            return app_tables.tenants.client_writable().get()

    return tenant_dict


def get_tenant_notion_info(tenant_id, user):
    """Get Notion-related information for a tenant"""
    tenant, usertenant, permissions = validate_user(tenant_id, user)

    if "delete_members" not in permissions:
        return None

    return {
        "notion_api_key": tenant["notion_api_key"],
        "notion_db_id": tenant["notion_db_id"],
        "notion_user_mapping": tenant["notion_user_mapping"],
        "notion_users": tenant["notion_users"]
    }


def get_all_permissions():
    return [i["name"] for i in app_tables.permissions.search()]


# ----------------
# Tenanted globals
# ----------------
@anvil.server.callable(require_user=True)
def get_tenanted_data(tenant_id, key):
    print_timestamp(f"get_tenanted_data: {key}")
    user = anvil.users.get_user(allow_remembered=True)
    # todo: verify tenant here?

    if key == "users":
        return get_users_iterable(tenant_id, user)
    elif key == "permissions":
        return get_permissions(tenant_id, user)
    elif key == "roles":
        return get_roles(tenant_id, user)
    elif key == "tenant_notion_info":
        return get_tenant_notion_info(tenant_id, user)
    elif key == "usertenant":
        return get_usertenant_dict(tenant_id)


def get_users_iterable(tenant_id, user):
    """Get an iterable of the users."""
    tenant, usertenant, permissions = validate_user(tenant_id, user)
    if "see_members" not in permissions:
        return []
    return app_tables.usertenant.client_readable(
        q.only_cols("user", "first_name", "last_name", "notes", "notion_user_id"),
        tenant=tenant,
    ).search()


def get_roles(tenant_id, user, usertenant=None, permissions=None, tenant=None):
    from .helpers import role_row_to_dict

    tenant, usertenant, permissions = validate_user(
        tenant_id, user, usertenant, permissions, tenant
    )
    if "see_forum" in permissions:
        role_search = app_tables.roles.search(tenant=tenant)

        role_list = [role_row_to_dict(i) for i in role_search]
        return role_list
    return []


@anvil.server.callable(require_user=True)
def get_usertenant_dict(tenant_id):
    """Get user tenant data including Notion settings"""
    user = anvil.users.get_user(allow_remembered=True)
    tenant, usertenant, permissions = validate_user(tenant_id, user)

    data = usertenant_row_to_dict(usertenant)
    return data


@anvil.server.callable(require_user=True)
def save_user_notion_mappings(tenant_id, mappings):
    """Save notion user mappings for app users

    Args:
        tenant_id: ID of the tenant
        mappings: List of dicts with:
            - email: App user's email
            - notion_user_id: Selected Notion user ID
    """
    user = anvil.users.get_user(allow_remembered=True)
    tenant, usertenant, permissions = validate_user(tenant_id, user)

    # Require admin permission
    if "delete_members" not in permissions:
        return None

        # Update the notion user ID
        usertenant["notion_user_mapping"] = mappings
