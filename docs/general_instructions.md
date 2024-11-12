# General Instructions

This document outlines general development guidelines for the Notion Task Loader application.

## Linting

### Policy on Linting Errors

Flake8 linting errors should be **ignored** in this project. Common linting errors you may see include:

1. Line length warnings (e.g., "line too long (149 > 79 characters)")
2. Unused import warnings
3. Blank line warnings
4. Whitespace warnings

These warnings should not be addressed because:
- The project prioritizes code readability over strict PEP 8 compliance
- Some imports may be used indirectly or needed for type hints
- Line length restrictions can make code less readable when broken up
- Maintaining consistent style across the codebase is more important than fixing linting warnings

### Example

This code with linting errors:
```python
from .helpers import print_timestamp, verify_tenant, validate_user, get_usertenant, get_users_with_permission, populate_roles, usertenant_row_to_dict

def some_long_function_name_with_many_parameters(param1, param2, param3, param4, param5, param6):
    """This is a very long docstring that explains what this function does in great detail."""
    pass
```

Should be left as-is, even though it triggers linting errors about line length and imports.

## Best Practices

While linting errors should be ignored, developers should still follow these best practices:

1. Write clear, descriptive variable and function names
2. Include docstrings for functions and modules
3. Maintain consistent indentation
4. Use meaningful whitespace to improve readability
5. Follow the established patterns in the codebase

The focus should be on writing maintainable, secure code that follows the project's architectural patterns rather than strict adherence to linting rules.
