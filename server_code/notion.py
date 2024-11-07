import anvil.server
import anvil.http
import anvil.users
import anvil.secrets
from anvil.tables import app_tables


NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def get_headers():
    """Get headers required for Notion API calls"""
    return {
        "Authorization": f"Bearer {anvil.secrets.get_secret('NOTION_API_KEY')}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION
    }

@anvil.server.callable(require_user=True)
def create_task(title, description):
    """Create a new task page in Notion database using REST API
    
    Args:
        title (str): Title of the task
        description (str): Description of the task
        
    Returns:
        dict: Created page object from Notion
    """
    try:
        # Get current user's tenant settings
        user = anvil.users.get_user()
        usertenant = app_tables.usertenant.get(user=user)  # TODO: verify tenant
        database_id = usertenant['dev_task_db']
        
        # Get user's Notion ID (assuming it's stored in the user profile)
        notion_user_id = usertenant['notion_user_id']
        
        # Prepare request body
        data = {
            "parent": {
                "type": "database_id",
                "database_id": database_id
            },
            "properties": {
                "title": {
                    "title": [
                        {
                            "type": "text",
                            "text": {
                                "content": title
                            }
                        }
                    ]
                },
                "Status": {
                    "status": {
                        "name": "Draft"
                    }
                }
            },
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": description
                                }
                            }
                        ]
                    }
                }
            ]
        }
        
        # Add assignee if we have the user's Notion ID
        if notion_user_id:
            data["properties"]["Assignee"] = {
                "people": [
                    {
                        "id": notion_user_id
                    }
                ]
            }
        
        # Make API request
        response = anvil.http.request(
            url=f"{NOTION_API_URL}/pages",
            method="POST",
            headers=get_headers(),
            json=data,
            json_response=True
        )
        
        return response
        
    except anvil.http.HttpError as e:
        raise Exception(f"Failed to create Notion task: {str(e)}")
