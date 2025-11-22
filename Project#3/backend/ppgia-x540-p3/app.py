##
# app.py @ Project#3/backend/ppgia-x540-p3
# ----------------------------------
# Chalice application for the PPGIA X540 Project 3 backend.
# Author: Jonas de Araújo Luz Jr.
# Date: 2024-06-15
##
import time
import uuid

from chalice.app import (
    Chalice,
    Response,
    BadRequestError,
)

import chalicelib.config as config
from chalicelib.bedrock import invoke_agent
from chalicelib.dynamodb import sessions_table
from chalicelib.polly import synthetize


app = Chalice(app_name=config.APP_NAME)
app.debug = True


@app.route('/', methods=['GET'])
def index_get():
    """
    Endpoint raiz simples de verificação (GET).
    """
    return {
        "message": "PPGIA X540 Project 3 Backend is running.",
        "timestamp": int(time.time()),
    }

#region Interaction Endpoints -------------------------------------------------
@app.route('/chat/{session_id}', methods=['POST', 'PUT'], 
           content_types=['application/json'])
def chat(session_id: str):
    """
    Endpoint to interact with a specific session (POST, PUT).
    """
    request = app.current_request
    user_input = request.json_body.get("message", "")
    if not user_input:
        raise BadRequestError("Missing 'message' in request body.")
    print(f"Received message for session {session_id}: {user_input}")

    # Process user input and generate a response
    response = process_user_input(session_id, user_input)
    
    return {
        "session_id": session_id, 
        "response": response
    }

def process_user_input(session_id: str, user_input: str) -> str:
    """
    Process the user input and generate a response.
    This is a placeholder function and should be replaced with actual logic.
    """
    # For demonstration, we just echo the input
    return f"Echo from session {session_id}: {user_input}"
#endregion Interaction Endpoints ----------------------------------------------

# region Session Management Endpoints -----------------------------------------
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


@app.route('/session/close/{session_id}', methods=['DELETE'])
def session_close(session_id: str):
    """
    Close an existing conversation session.
    """
    timestamp = int(time.time())

    # Update the session status to 'closed' in DynamoDB
    response = sessions_table.update_item(
        Key={'conversation_id': session_id},
        UpdateExpression="SET #s = :s, closed_at = :ca",
        ExpressionAttributeNames={'#s': 'status'},
        ExpressionAttributeValues={
            ':s': 'closed',
            ':ca': timestamp,
        },
        ReturnValues="UPDATED_NEW"
    )

    return {
        "session_id": session_id,
        "closed_at": timestamp,
        "updated_attributes": response.get('Attributes', {})
    }
# endregion Session Management Endpoints --------------------------------------

# region LLM agent Endpoints --------------------------------------------------
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
# endregion LLM agent Endpoints ------------------------------------------------

# region TTS Endpoints --------------------------------------------------------
@app.route('/tts/synthetize', methods=['POST'], content_types=['application/json'])
def tts_synthetize():
    """
    Endpoint to synthesize speech from text (POST).
    """
    request = app.current_request
    text = request.json_body.get("text", "")
    if not text:
        raise BadRequestError("Missing 'text' in request body.")

    try:
        audio = synthetize(text)
    except Exception as e:
        raise BadRequestError(f"Error synthesizing speech: {str(e)}")

    return Response(
        body=audio, 
        status_code=200,
        headers={
            'Content-Type': 'audio/mpeg',
            'Content-Length': str(len(audio)),
            'Content-Disposition': 'inline; filename="speech.mp3"'
            #'Content-Disposition': 'attachment; filename="speech.mp3"'
        },
    )

    # url = s3_client.generate_presigned_url(
    #     'get_object',
    #     Params={'Bucket': bucket, 'Key': key},
    #     ExpiresIn=300  # 5 minutos
    # )
    # return {'audio_url': url}

# endregion TTS Endpoints -----------------------------------------------------
