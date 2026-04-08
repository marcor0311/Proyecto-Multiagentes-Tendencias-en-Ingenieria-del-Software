import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()  # Lee .env en la raíz del proyecto

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)

def ask_azure_openai(message: str):
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

    response = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": message}],
        max_completion_tokens=200,
    )

    return response.choices[0].message.content