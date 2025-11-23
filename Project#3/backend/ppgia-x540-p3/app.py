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
    Root endpoint to check if the backend is running (GET).
    """
    return {
        "message": "PPGIA X540 Project 3 Backend is running.",
        "timestamp": int(time.time()),
    }

#region Interaction Endpoints -------------------------------------------------
@app.route('/chat/{session_id}', methods=['POST', 'PUT'], 
           content_types=['application/json'])
def chat(session_id: str) -> Response:
    """
    Endpoint to interact with a specific session (POST, PUT).
    """
    request = app.current_request
    user_input = request.json_body.get("message", "")
    if not user_input:
        raise BadRequestError("Missing 'message' in request body.")

    # Process user input and generate a response
    response = process_user_input(session_id, user_input)
    return response

def process_user_input(session_id: str, user_input: str) -> Response:
    """
    Process the user input and generate a response.
    """
    # 1. Retrieve session context from DynamoDB (if needed)
    # 2. Generate response using LLM agent
    reply = invoke_agent(user_input, session_id=session_id)

    # 3. Generate speech using TTS (if needed)
    try:
        audio = synthetize(reply)
    except Exception as e:
        raise BadRequestError(f"Error synthesizing speech: {str(e)}")

    response = Response(
        body=audio, 
        status_code=200,
        headers={
            'Content-Type': 'audio/ogg',
            'Content-Length': str(len(audio)),
            'Content-Disposition': 'inline; filename="speech.ogg"'
            #'Content-Disposition': 'attachment; filename="speech.ogg"'
        }
    )

    # 4. Update session context in DynamoDB (if needed)
    # 5. Return the generated response
    return response

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

# region Service checking Endpoints -------------------------------------------
@app.route('/agent/test', methods=['GET'])
def agent_test():
    """
    Simple test endpoint to invoke Bedrock Agent (GET).
    """
    prompt = "Responda em português: diga apenas 'Olá, este é um teste do agente Bedrock via Chalice.'"
    reply = invoke_agent(prompt)
    return {"prompt": prompt, "reply": reply}


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
            'Content-Type': 'audio/ogg',
            'Content-Length': str(len(audio)),
            'Content-Disposition': 'inline; filename="speech.ogg"'
            #'Content-Disposition': 'attachment; filename="speech.ogg"'
        },
    )

    # url = s3_client.generate_presigned_url(
    #     'get_object',
    #     Params={'Bucket': bucket, 'Key': key},
    #     ExpiresIn=300  # 5 minutos
    # )
    # return {'audio_url': url}

# endregion Service checking Endpoints ----------------------------------------
