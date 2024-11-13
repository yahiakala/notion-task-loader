import anvil.server
import anvil.http
import anvil.users
import anvil.secrets
from anvil.tables import app_tables


NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def get_headers(api_key):
    """Get headers required for Notion API calls
    
    Args:
        api_key: The Notion API key to use for authorization
    """
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION
    }


def create_task(title, description, database_id, api_key, notion_user_id=None, status=None):
    """Create a new task page in Notion database using REST API
    
    Args:
        title (str): Title of the task
        description (str): Description of the task
        database_id (str): ID of the Notion database to create task in
        api_key (str): Notion API key for authorization
        notion_user_id (str, optional): Notion user ID to assign task to
        status (str, optional): Status of the task. If None, status won't be included.
        
    Returns:
        dict: Created page object from Notion
    """
    try:
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
        
        # Add status if provided
        if status is not None:
            data["properties"]["Status"] = {
                "status": {
                    "name": status
                }
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
            headers=get_headers(api_key),
            json=data,
            json_response=True
        )
        
        return response
        
    except anvil.http.HttpError as e:
        raise Exception(f"Failed to create Notion task: {str(e)}")
