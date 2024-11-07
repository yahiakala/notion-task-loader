import anvil.server
from openai import OpenAI
import anvil.secrets
import anvil.tables
import anvil.tables.query as q
from anvil.tables import app_tables


system_prompt = """
You are an AI assistant that extracts action items from meeting
transcripts.

For each action item you identify:

1. Create a clear, concise title (1 line)
2. Write a detailed description explaining the context and what needs
to be done (1 paragraph)

Return the results as a JSON object.
Example format:

[
    {
        "title": "Set up weekly team sync"
        "description": "Schedule a recurring team sync meeting every Monday at 10am to discuss project progress and blockers. This was identified as necessary due to communication gaps mentioned in the transcript."
    },
    {
        "title": "Update documentation"
        "description": "Review and update the API documentation to include the new endpoints discussed in the meeting. Several team members mentioned outdated documentation causing confusion."
    }
]

BE STRICT IN THIS FORMAT.
"""


@anvil.server.background_task
def process_transcript_background(transcript):
    """Background task to process transcript with OpenAI API."""
    # Get API key from Anvil secrets
    api_key = anvil.secrets.get_secret('OPENAI_API_KEY')
    
    client = OpenAI(api_key=api_key)

    user_prompt = (
        "Please analyze this transcript and extract all action items:\n\n"
        f"{transcript}\n\n"
        "Remember to format the response as a Python list of dicts with "
        "'title' and 'description' keys."
    )

    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",  # Using the model with 128k context window
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=4000  # Allowing for lengthy responses
    )
    

    return response.choices[0].message.content

    # The response will be a string representation of a Python list of dicts
    # We need to evaluate it safely to convert it to actual Python objects
    # import ast
    # try:
    #     action_items = ast.literal_eval(response.choices[0].message.content)
    #     return action_items
    # except Exception as e:
    #     # If there's any error in parsing, return an empty list
    #     print(f"Error parsing OpenAI response: {str(e)}")
    #     return []


@anvil.server.callable
def process_transcript(transcript):
    """Start background processing and return task ID."""
    # Start background task
    task = anvil.server.launch_background_task('process_transcript_background', transcript)
    return task
