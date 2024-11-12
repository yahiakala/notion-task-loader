from anvil_squared.globals import GlobalCache


_global_dict = {
    'user': None,
    'is_mobile': None,
    'customer_portal': None,
    'usertenant': None,
    'tenant': None,
    'tenant_id': None
}
_tenanted_dict = {
    'info': None,
    'permissions': None,
    'tenant_notion_info': None
}

Global = GlobalCache(_global_dict, _tenanted_dict)