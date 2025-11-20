##
# app.py @ Project#3/backend/ppgia-x540-p3
# ----------------------------------
# Chalice application for the PPGIA X540 Project 3 backend.
# Author: Jonas de Araújo Luz Jr.
# Date: 2024-06-15
##
import time
import uuid

from chalice import Chalice, BadRequestError

import _chalice_config as config
from _bedrock import invoke_agent
from _dynamodb import sessions_table


app = Chalice(app_name=config.APP_NAME)


# region Chalice app routes --------------------------------------------------
@app.route('/', methods=['GET'])
def index_get():
    """
    Endpoint raiz simples de verificação (GET).
    """
    return {
        "message": "PPGIA X540 Project 3 Backend is running.",
        "timestamp": int(time.time()),
    }

@app.route('/session/init/{user_id}', methods=['POST'])
def session_init(user_id: str):
    """
    Initialize a new conversation session.
    Returns a new session ID.
    """
    conversation_id = session_id = str(uuid.uuid4())
    timestamp = int(time.time())

    # Stores the new session in DynamoDB
    sessions_table.put_item(
        Item={
            'conversation_id': conversation_id,
            'user_id': user_id,
            'created_at': timestamp,
            'status': 'active',
        }
    )
    
    return {
        "session_id": session_id,
        "created_at": timestamp,
    }

@app.route('/agent/test', methods=['GET'])
def agent_test():
    """
    Simple test endpoint to invoke Bedrock Agent (GET).
    """
    prompt = "Responda em português: diga apenas 'Olá, este é um teste do agente Bedrock via Chalice.'"
    reply = invoke_agent(prompt)
    return {"prompt": prompt, "reply": reply}

@app.route('/agent/ask', methods=['POST'])
def agent_ask():
    """
    Endpoint to ask a question to the Bedrock Agent (POST).
    """
    request = app.current_request
    question = request.json_body.get("question", "")
    if not question:
        raise BadRequestError("Missing 'question' in request body.")

    reply = invoke_agent(question)
    return {"question": question, "reply": reply}
# endregion Chalice app routes ------------------------------------------------
