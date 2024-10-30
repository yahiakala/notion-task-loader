import anvil.server
import anvil.users
from anvil.tables import app_tables



@anvil.server.callable(require_user=True)
def get_permissions():
    # TODO: add to anvil extras
    user = anvil.users.get_user(allow_remembered=True)
    usertenant = app_tables.usertenant.get(user=user)
    try:
        user_permissions = set(
            permission["name"]
            for role in usertenant["roles"]
            for permission in role["permissions"]
        )
        return list(user_permissions)
    except TypeError:
        return []


@anvil.server.callable
def test_this():
    client_info = anvil.server.context.client
    print(client_info)
    print(client_info.type)


@anvil.server.callable(require_user=True)
def impersonate_user(email):
    # TODO: validate user
    new_user = app_tables.users.get(email=email)
    anvil.users.force_login(new_user)
    return new_user


@anvil.server.callable(require_user=True)
def get_usertenant():
    user = anvil.users.get_user(allow_remembered=True)
    if not user:
        raise ValueError('User is not logged in.')
    if not app_tables.usertenant.get(user=user):
        # TODO: add some defaults
        usertenant = app_tables.usertenant.add_row(user=user)
    else:
        usertenant = app_tables.usertenant.get(user=user)
    return usertenant