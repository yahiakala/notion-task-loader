from anvil_squared.globals import GlobalCache


_global_dict = {
    'user': None,
    'is_mobile': None,
    'customer_portal': None,
    'usermap': None,
    'permissions': None
}

Global = GlobalCache(_global_dict)