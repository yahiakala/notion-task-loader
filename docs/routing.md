# Routing System Documentation

## Overview

The application uses a custom routing system built on top of Anvil's routing capabilities. The routing system provides URL-based navigation with authentication checks, template management, and form caching.

## Migration from anvil_extras

The application previously used the anvil_extras routing library but has since migrated to a custom routing implementation. Key differences include:

### Nav Links vs Regular Links
Instead of using regular HTML links or anvil_extras' on_navigation method, the app uses nav links with configured path tags:
```python
self.link_home.tag.path = "/app"  # Configure path tag for navigation
```

Navigation can be triggered in two ways:
1. Through path-tagged links that work with the router
2. Programmatic navigation using router.navigate():
```python
router.navigate(path='/desired/path', query={'param': 'value'})
```

### Obsolete on_navigation Method
The anvil_extras routing library used an on_navigation method for handling route changes. This has been replaced with a more structured approach using:
- Route classes that inherit from TemplateWithContainerRoute
- Template management through 'Templates.Static' and 'Templates.Router'
- Form caching with cache_form = True
- Authentication middleware through EnsureUserMixin


## Core Components

### Route Classes

Routes are defined in `client_code/routes.py` and inherit from `TemplateWithContainerRoute`. Each route specifies:

- `template`: The template to use for rendering (either 'Templates.Static' or 'Templates.Router')
- `path`: The URL path for the route
- `form`: The form component to render
- `cache_form`: Whether to cache the form (typically set to True)

Example:
```python
class HomeRoute(EnsureUserMixin, BaseRoute):
    template = 'Templates.Router'
    path = '/app'
    form = 'Pages.Home'
    cache_form = True
```

### Authentication Routing (EnsureUserMixin)

The `EnsureUserMixin` class provides comprehensive authentication and tenant management:

1. Authentication Check:
   ```python
   def before_load(self, **loader_args):
       if not Global.user:
           raise Redirect(path="/signin")
   ```
   - Executes before loading protected routes
   - Redirects unauthenticated users to signin page

2. Tenant Management:
   - Checks for existing tenant in Global state
   - Retrieves or creates tenant if not present
   - Sets tenant ID in Global state
   - Redirects to settings if tenant setup is incomplete

3. Permission Handling:
   - Checks for 'delete_members' permission
   - Forces settings configuration for incomplete tenant setup

### Query Parameter Handling

Forms receive routing context through their constructor:

```python
def __init__(self, routing_context: router.RoutingContext, **properties):
    self.url_dict = routing_context.query
```

Query parameters are handled in several ways:

1. Sign Form:
   - Preserves query parameters when navigating between auth forms
   ```python
   def btn_signin_click(self, **event_args):
       router.navigate(path='/signin', query=self.url_dict)
   ```

2. Signin Form:
   - Handles redirect URLs through query parameters
   ```python
   def route_user(self, **event_args):
       if 'redirect' in self.url_dict and self.user:
           anvil.js.window.location.href = self.url_dict['redirect']
       elif self.user:
           router.navigate(path='/app')
   ```

3. Signup Form:
   - Maintains query parameters during auth flow
   - Supports redirect after successful signup
   ```python
   def route_user(self, **event_args):
       if 'redirect' in self.url_dict and self.user:
           Global.user = self.user
           anvil.js.window.location.href = self.url_dict['redirect']
   ```

### Router Template

The Router template (`client_code/Templates/Router/__init__.py`) manages:

1. Navigation handling:
   - Updates link states based on current route
   - Manages form loading/unloading
   - Handles navigation events

2. User state management:
   - Controls visibility of navigation items based on user authentication
   - Manages logout functionality
   - Handles permission-based navigation elements

## Available Routes

1. Public Routes:
   - `/` (Sign)
   - `/signin` (Login)
   - `/signup` (Registration)

2. Protected Routes (require authentication):
   - `/app` (Home)
   - `/app/settings` (Settings)
   - `/app/admin` (Admin)
   - `/app/tests` (Tests)

## Navigation

Navigation can be triggered in two ways:

1. Using the Router's navigation method:
```python
router.navigate(path='/desired/path', query={'param': 'value'})
```

2. Through link clicks with configured path tags:
```python
self.link_home.tag.path = "/app"
```

## Form Caching

The routing system implements form caching to improve performance:
- `cache_form = True` enables caching for a route
- Cache can be cleared using `router.clear_cache()`
- Cache is automatically cleared on logout

## Security

The routing system implements several security features:

1. Authentication checks through EnsureUserMixin
2. Permission-based navigation visibility
3. Automatic redirects for unauthenticated users
4. Tenant validation and initialization

## Best Practices

1. Always extend `BaseRoute` for new routes
2. Use `EnsureUserMixin` for protected routes
3. Configure appropriate templates based on layout needs
4. Enable form caching unless dynamic content is required
5. Clear cache when user state changes
6. Preserve query parameters during authentication flow when needed
7. Use routing context to access query parameters in forms
