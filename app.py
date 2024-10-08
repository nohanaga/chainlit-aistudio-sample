import chainlit as cl
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

AZURE_ENDPOINT_KEY = os.environ['AZURE_ENDPOINT_KEY']
AZURE_ENDPOINT_URL = os.environ['AZURE_ENDPOINT_URL']
AZURE_MODEL_DEPLOYMENT = os.environ['AZURE_MODEL_DEPLOYMENT']

# Usage example
url = AZURE_ENDPOINT_URL
api_key = AZURE_ENDPOINT_KEY
deployment_name =AZURE_MODEL_DEPLOYMENT

if not api_key:
    raise Exception("A key should be provided to invoke the endpoint")


def allow_self_signed_https(allowed):
    if allowed:
        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

def call_azure_ml_endpoint(url, api_key, data, deployment_name=None):
    allow_self_signed_https(True)

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + api_key
    }

    if deployment_name:
        headers['azureml-model-deployment'] = deployment_name

    try:
        response = requests.post(url, headers=headers, json=data, verify=False)

        response.raise_for_status()

        # Decode the JSON response to get a Python dictionary
        decoded_response = json.loads(response.content.decode('utf-8'))
        return decoded_response

    except requests.exceptions.HTTPError as error:
        error_message = {
            'status_code': error.response.status_code,
            'headers': error.response.headers,
            'body': json.loads(error.response.content.decode('utf-8'))
        }
        return error_message


# チャットが開始されたときに実行される関数
@cl.on_chat_start  
async def on_chat_start():
    await cl.Message(content="Azure OpenAI 日本の歴史アシスタントが起動しました！メッセージを入力してください！").send()

@cl.on_message
async def on_message(message: cl.Message):
    data ={
        "topic": message.content
    }
    #data = {"chat_history": [], 'question': message.content}

    response = call_azure_ml_endpoint(url, api_key, data, deployment_name)
    await cl.Message(content=response['result']).send()
