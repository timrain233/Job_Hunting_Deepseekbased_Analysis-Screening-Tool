import json
import os
from openai import OpenAI
from prompts import assistant_instructions
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL')

client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)


def create_assistant(client):
    assistant_file_path = 'assistant.json'

    if os.path.exists(assistant_file_path):
        with open(assistant_file_path, 'r') as file:
            assistant_data = json.load(file)
            assistant_id = assistant_data['assistant_id']
        print("Loaded existing assistant ID.")
    else:
        file = client.files.create(
            file=open("resume/my_cover.pdf", "rb"),
            purpose='assistants',
        )

        assistant = client.beta.assistants.create(
            instructions=assistant_instructions,
            model="gpt-3.5-turbo-1106",
            tools=[
                {
                    "type": "retrieval"
                },
            ],
            file_ids=[file.id],
        )

        with open(assistant_file_path, 'w') as file:
            json.dump({'assistant_id': assistant.id}, file)
        print("Created a new assistant and saved the ID.")

        assistant_id = assistant.id

    return assistant_id