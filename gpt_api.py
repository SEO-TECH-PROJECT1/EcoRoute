from openai import OpenAI
import os
from dotenv import load_dotenv, dotenv_values
from pprint import pprint


load_dotenv()
API_TOKEN = os.getenv('OAI_TOKEN')
GPT_MODEL = "gpt-4o"
client = OpenAI()

def chat_call(context):
    
    return client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=context,
        tools = tools,
        tool_choice="auto",
        max_tokens=300,
        temperature=0
    )


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_map",
            "description": "create a SQL query to get the map of a previous route",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {
                        "type": "string",
                        "description": "Address of the origin eg. '123 Main St, City, State, Zip'"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Address of the destination eg. '123 Main St, City, State, Zip'"
                    },
                    "query": {
                        "type": "string",
                        "description": """
                            SQL query extracting info to answer the user's question.
                            SQL should be written using this FORMAT:
                            SELECT * FROM routes WHERE start_location = (ORIGIN), AND end_location = (DESTINATION);
                            The query should be returned in plain text, not in JSON.
                            """
                    }
                },
                "required": ["origin", "destination", "query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_origin_destination",
            "description": "gets origin and destination of a new route request",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {
                        "type": "string",
                        "description": "Address of the origin eg. '123 Main St, City, State, Zip'"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Address of the destination eg. '123 Main St, City, State, Zip'"
                    },
                },
                "required": ["origin", "destination"]
            }
        }
    },
]

question = "Can you get me the route from 502 Chcauncey St, Brooklyn, NY to Park Place, New York, NY?"

context = [{"role": "user", "content": question}]

response = chat_call(context)



res_data = response.choices[0].message
res_tools = res_data.tool_calls


tool_id = res_tools[0].id
tool_function_name = res_tools[0].function.name
res_args = eval(res_tools[0].function.arguments)

print(tool_id)
print(tool_function_name)
print(res_args["origin"])
print(res_args["destination"])





# print(response.choices[0].message)





