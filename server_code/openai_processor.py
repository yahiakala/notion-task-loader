import anvil.server
from openai import OpenAI
import anvil.secrets
from pydantic import BaseModel


class ActionItem(BaseModel):
    title: str
    description: str


system_prompt = """
You are an AI assistant that extracts action items from meeting
transcripts.

For each action item you identify:

1. Create a clear, concise title (1 line)
2. Write a detailed description explaining the context and what needs
to be done (1 paragraph)
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
        "Extract action items with titles and descriptions."
    )

    completion = client.chat.completions.create(
        model="gpt-4o-2024-08-06",  # Using model with 128k context window
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=4000,
        response_format=ActionItem
    )

    return completion.choices[0].message.parsed


@anvil.server.callable
def process_transcript(transcript):
    """Start background processing and return task ID."""
    # Start background task
    task = anvil.server.launch_background_task('process_transcript_background', transcript)
    return task
