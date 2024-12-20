from anvil.tables import app_tables
import anvil.tables.query as q
# from anvil_squared.helpers import print_timestamp
import anvil.secrets


role_dict = {
    'Member': ['see_profile'],
    'Admin': ['see_profile', 'see_members', 'edit_members', 'delete_members', 'delete_admin', 'edit_roles'],
}

perm_list = []
for key, val in role_dict.items():
    perm_list = perm_list + val

perm_list = list(set(perm_list))


def print_timestamp(input_str):
    import datetime as dt
    import pytz
    eastern_tz = pytz.timezone('US/Eastern')
    current_time = dt.datetime.now(eastern_tz)
    formatted_time = current_time.strftime('%H:%M:%S.%f')
    print(f"{input_str} : {formatted_time}")


def verify_tenant(tenant_id, user, tenant=None, usertenant=None):
    """Verify a user is in this tenant."""
    tenant = tenant or app_tables.tenants.get_by_id(tenant_id)
    usertenant = usertenant or app_tables.usertenant.get(user=user, tenant=tenant)

    if usertenant['tenant'] == tenant:
        return tenant

    raise Exception('User does not belong to this tenant.')


def get_usertenant(tenant_id, user, tenant=None):
    """Get a usertenant. A user with no tenant will be added to this tenant."""
    tenant = tenant or app_tables.tenants.get_by_id(tenant_id)
    
    if not app_tables.usertenant.get(user=user, tenant=tenant):
        new_roles = get_new_user_roles(None, tenant)
        usertenant = app_tables.usertenant.add_row(user=user, tenant=tenant, roles=new_roles)
    else:
        usertenant = app_tables.usertenant.get(user=user, tenant=tenant)
    return usertenant


def get_new_user_roles(tenant_id, tenant=None):
    """Assign a brand new user a role in this tenant."""
    tenant = tenant or app_tables.tenants.get_by_id(tenant_id)
    new_roles = app_tables.roles.search(
        tenant=tenant,
        name=q.any_of(*tenant['new_roles']),
        can_edit=q.not_(True)
    )
    return list(new_roles)


def get_user_roles(tenant_id, user, usertenant=None, tenant=None):
    """Get names of roles for a user in a tenant."""
    tenant = tenant if tenant is not None else verify_tenant(tenant_id, user, usertenant=usertenant)
    usertenant = usertenant if usertenant is not None else app_tables.usertenant.get(user=user, tenant=tenant)

    roles = []
    if usertenant['roles']:
        for role in usertenant['roles']:
            roles.append(role['name'])
    return list(set(roles))


def get_permissions(tenant_id, user, tenant=None, usertenant=None):
    """Get the permissions of a user in a particular tenant."""
    tenant = tenant if tenant is not None else verify_tenant(tenant_id, user, usertenant=usertenant)
    usertenant = usertenant if usertenant is not None else app_tables.usertenant.get(user=user, tenant=tenant)
        
    user_permissions = []
    if usertenant['roles']:
        for role in usertenant['roles']:
            if role['permissions']:
                for permission in role['permissions']:
                    user_permissions.append(permission['name'])

    return list(set(user_permissions))


def validate_user(tenant_id, user, usertenant=None, permissions=None, tenant=None):
    usertenant = usertenant if usertenant is not None else get_usertenant(tenant_id, user, tenant=tenant)
    tenant = tenant if tenant is not None else verify_tenant(tenant_id, user, usertenant=usertenant)
    permissions = permissions if permissions is not None else get_permissions(tenant_id, user, usertenant=usertenant, tenant=tenant)
    return tenant, usertenant, permissions


def get_users_with_permission(tenant_id, permission, tenant=None):
    tenant = tenant or app_tables.tenants.get_by_id(tenant_id)
    perm_row = app_tables.permissions.get(name=permission)
    role_rows = app_tables.roles.search(permissions=[perm_row], tenant=tenant)
    usertenant_list = []
    for role in role_rows:
        usertenants = app_tables.usertenant.search(roles=[role], tenant=tenant)
        for usertenant in usertenants:
            if usertenant not in usertenant_list:
                usertenant_list.append(usertenant)
    for i in usertenant_list:
        print(i['user']['email'])
    return usertenant_list


def upsert_role(usertenant, role_name):
    role = app_tables.roles.get(tenant=usertenant['tenant'], name=role_name)
    if not usertenant['roles']:
        usertenant['roles'] = [role]
    elif role not in usertenant['roles']:
        usertenant['roles'] = usertenant['roles'] + [role]
    return usertenant


def remove_role(usertenant, role_names):
    usertenant['roles'] = [i for i in usertenant['roles'] if i['name'] not in role_names]
    if len(usertenant['roles']) == 0:
        # Deal with a quirk of empty lists.
        usertenant['roles'] = None
    return usertenant


def populate_permissions():
    """Populate the permissions table."""
    print_timestamp('populate_permissions')
    if len(app_tables.permissions.search()) == 0:
        for perm in perm_list:
            app_tables.permissions.add_row(name=perm)


def populate_roles(tenant):
    """Some basic roles."""
    print_timestamp('populate_roles')
    
    for key, val in role_dict.items():
        perm_rows = app_tables.permissions.search(name=q.any_of(*val))
        if len(perm_rows) == 0:
            populate_permissions()
            perm_rows = app_tables.permissions.search(name=q.any_of(*val))
            
        is_it_there = app_tables.roles.get(name=key, tenant=tenant)
        if not is_it_there:
            app_tables.roles.add_row(name=key, tenant=tenant, permissions=list(perm_rows), can_edit=False)
    return app_tables.roles.search(tenant=tenant)


def decrypt(something):
    if something:
        return anvil.secrets.decrypt_with_key("encryption_key", something)
    else:
        return ''


def list_to_csv(data):
    """Output a list of dicts to csv."""
    import io
    import csv
    import anvil.media
    
    output = io.StringIO()
    
    # Create a CSV writer object
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    # Write the header
    writer.writeheader()
    # Write the data
    for row in data:
        writer.writerow(row)
    # Get the CSV content
    csv_content = output.getvalue()
    # Close the string buffer
    output.close()
    
    # Create a media object from the CSV content
    csv_file = anvil.BlobMedia('text/csv', csv_content.encode('utf-8'), 'data.csv')
    return csv_file


# --------------------
# Return rows as dicts
# --------------------
def usertenant_row_to_dict(row):
    row_dict = {
        'notion_api_key': row['notion_api_key'],
        'notion_team_user_id': row['notion_team_user_id'],
        'notion_task_db_id': row['notion_task_db_id'],
        'notion_user_id': row['notion_user_id'],
        'notion_users_personal': row['notion_users_personal'],
        'notion_users_team': row['notion_users_team'],
        'email': row['user']['email'],
        'last_login': row['user']['last_login'],
        'signed_up': row['user']['signed_up'],
        'permissions': get_permissions(None, row['user'], tenant=row['tenant'], usertenant=row),
        'roles': get_user_roles(None, None, row, row['tenant'])
    }
    return row_dict


def role_row_to_dict(role):
    if role['permissions']:
        role_perm = [j['name'] for j in role['permissions']]
    else:
        role_perm = []
    return {
        'name': role['name'],
        'last_update': role['last_update'],
        'guides': app_tables.rolefiles.search(role=role),
        'permissions': role_perm,
        'can_edit': role['can_edit']
    }