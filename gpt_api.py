import openai
import os




API_KEY = os.environ.get("OAI_TOKEN")

def chat_call(context):
            openai.api_key = API_KEY
            return openai.ChatCompletion.create(
            model="gpt-4o",
            messages = context)
            