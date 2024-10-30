import anvil.server
import anvil.users
from anvil.tables import app_tables
from anvil_extras.authorisation import authorisation_required
from anvil_extras import authorisation

authorisation.set_config(get_roles='usermap')


@anvil.server.callable(require_user=True)
def get_permissions():
    # TODO: add to anvil extras
    user = anvil.users.get_user(allow_remembered=True)
    usermap = app_tables.usermap.get(user=user)
    try:
        user_permissions = set(
            permission["name"]
            for role in usermap["roles"]
            for permission in role["permissions"]
        )
        return list(user_permissions)
    except TypeError:
        return []


@anvil.server.callable(require_user=True)
@authorisation_required('admin')
def do_admin():
    print('doing admin thing.')
    pass

@anvil.server.callable
def test_this():
    client_info = anvil.server.context.client
    print(client_info)
    print(client_info.type)


@anvil.server.callable(require_user=True)
@authorisation_required('dev')
def impersonate_user(email):
    new_user = app_tables.users.get(email=email)
    anvil.users.force_login(new_user)
    return new_user


@anvil.server.callable(require_user=True)
def get_usermap():
    user = anvil.users.get_user(allow_remembered=True)
    if not user:
        raise ValueError('User is not logged in.')
    if not app_tables.usermap.get(user=user):
        # TODO: add some defaults
        usermap = app_tables.usermap.add_row(user=user)
    else:
        usermap = app_tables.usermap.get(user=user)
    return usermap