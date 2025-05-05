from openai import AzureOpenAI
import os

# may change in the future
# https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#rest-api-versioning
api_version = "2024-10-21"

from dotenv import load_dotenv
load_dotenv()

# gets the API Key from environment variable AZURE_OPENAI_API_KEY
client = AzureOpenAI(
    #api_version=api_version,
    # https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#create-a-resource
    base_url="https://takin-research.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-10-21",
    #azure_deployment="gpt-4o",
    api_key=os.getenv("azure_4o_API_KEY"),
    api_version=api_version
)

completion = client.chat.completions.create(
    model="gpt-4o",  # e.g. gpt-35-instant
    messages=[
        {
            "role": "user",
            "content": "tell me a short joke.",
        },
    ],
)
print(completion.to_json())