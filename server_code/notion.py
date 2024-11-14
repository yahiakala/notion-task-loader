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


import anvil.http
import anvil.secrets
import anvil.server
import anvil.users

# from anvil.tables import app_tables


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
        "Notion-Version": NOTION_VERSION,
    }


def get_workspace_users(api_key):
    """Get list of users in the Notion workspace

    Args:
        api_key: The Notion API key to use for authorization

    Returns:
        list: List of user objects from Notion
    """
    try:
        response = anvil.http.request(
            url=f"{NOTION_API_URL}/users",
            method="GET",
            headers=get_headers(api_key),
            json=True,
            timeout=30,
        )
        return response.get("results", [])
    except anvil.http.HttpError as e:
        print(f"Error getting workspace users: {e.status}")
        print(e.content)
        raise Exception("Failed to get workspace users")


@anvil.server.callable
def get_notion_users(api_key):
    """Get list of users in the Notion workspace

    Args:
        api_key: The Notion API key to use for authorization

    Returns:
        list: List of user objects from Notion containing:
            - id: User's Notion ID
            - name: User's name
            - avatar_url: URL of user's avatar
            - type: Type of user (person/bot)
            - person: Additional person info if type is person
    """
    return get_workspace_users(api_key)


def create_task(
    title, description, database_id, api_key, notion_user_id=None, status=None
):
    """Create a new task page in Notion database using REST API

    Args:
        title (str): Title of the task
        description (str): Description of the task
        database_id (str): ID of the Notion database to create task in
        api_key (str): Notion API key for authorization
        notion_user_id (str, optional): Notion user ID to assign task to
        status (str, optional): Status of the task.
          If None, status won't be included.

    Returns:
        dict: Created page object from Notion
    """
    # Prepare request body
    data = {
        "parent": {"type": "database_id", "database_id": database_id},
        "properties": {
            "title": {"title": [{"type": "text", "text": {"content": title}}]}
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": description}}]
                },
            }
        ],
    }

    # Add status if provided
    if status is not None:
        data["properties"]["Status"] = {"status": {"name": status}}

    # Add assignee if we have the user's Notion ID
    if notion_user_id:
        data["properties"]["Assignee"] = {"people": [{"id": notion_user_id}]}

    # Make API request
    try:
        return anvil.http.request(
            url=f"{NOTION_API_URL}/pages",
            method="POST",
            headers=get_headers(api_key),
            data=data,
            json=True,
            timeout=30,
        )
    except anvil.http.HttpError as e:
        print(e.status)
        print(e.content)
        raise Exception
