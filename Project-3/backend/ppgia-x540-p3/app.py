##
# app.py @ Project#3/backend/ppgia-x540-p3
# ----------------------------------
# Chalice application for the PPGIA X540 Project 3 backend.
# Author: Jonas de Araújo Luz Jr.
# Last Update: 2025-11-27
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
from chalicelib.dynamodb import (
    create_session,
    close_session
)
from chalicelib.polly import synthetize
from chalicelib.s3 import (
    upload_audio_file, create_presigned_upload_url
)
from chalicelib.transcribe import (
    start_transcription_job,
    get_transcription_result
)


app = Chalice(app_name=config.APP_NAME)
app.debug = True


@app.route('/', methods=['GET'])
def index_get() -> Response:
    """
    Root endpoint to check if the backend is running (GET).
    """
    return Response(body={
        "message": "PPGIA X540 Project 3 Backend is running.",
        "timestamp": int(time.time()),
    }, status_code=200, headers={'Content-Type': 'application/json'})


#region Session Management Endpoints ------------------------------------------
#
@app.route('/session/init/{user_id}', methods=['POST'])
def session_init(user_id: str):
    """
    Initialize a new conversation session.
    Returns a new session ID.
    """
    # Stores the new session in DynamoDB
    conversation_id, timestamp = create_session(user_id)
    return {
        "session_id": conversation_id,
        "created_at": timestamp,
    }


@app.route('/session/close/{session_id}', methods=['DELETE'])
def session_close(session_id: str):
    """
    Close an existing conversation session.
    """
    timestamp = int(time.time())

    # Update the session status to 'closed' in DynamoDB
    response = close_session(session_id)
    return {
        "session_id": session_id,
        "closed_at": response
    }
#
#endregion Session Management Endpoints ---------------------------------------

#region Transcription Endpoints -----------------------------------------------
#
@app.route('/transcript/get-upload-url', methods=['POST'])
def get_upload_url() -> Response:
    """
    Endpoint to get a presigned URL for uploading an audio file (POST).
    """
    request = app.current_request
    body = getattr(request, 'json_body', {})
    filename = body.get('filename', 'upload.wav')
    content_type = body.get('content_type', 'audio/wav')

    # Generate a unique key
    ext = filename.split('.')[-1] if '.' in filename else 'wav'
    s3_key = f"uploads/{uuid.uuid4()}.{ext}"
    
    # Generate the URL (using helper)
    presigned_url = create_presigned_upload_url(s3_key, content_type)
    
    return Response(
        body={
            "upload_url": presigned_url,
            "s3_key": s3_key
        },
        status_code=200,
        headers={'Content-Type': 'application/json'}
    )

@app.route('/transcript/start', methods=['POST'])
def start_transcription() -> Response:
    """
    Endpoint to manually start a transcription job for an S3 object (POST).
    """
    request = app.current_request
    body = getattr(request, 'json_body', {})
    s3_key = body.get('s3_key', '')
    if not s3_key:
        raise BadRequestError("Missing 's3_key' in request body.")
    bucket_name = config.S3_AUDIO_BUCKET
    s3_uri = f"s3://{bucket_name}/{s3_key}"

    # Generate a unique job name for AWS Transcribe
    job_name = f"ppgia-x540-transcription-{uuid.uuid4()}"

    try:
        start_transcription_job(s3_uri, job_name)
        app.log.info(f"Started transcription job '{job_name}' for S3 URI: '{s3_uri}'")
        return Response(
            body={
                "job_name": job_name,
                "s3_uri": s3_uri,
                "status": "IN_PROGRESS",
                "transcript": ""
            },
            status_code=200,
            headers={'Content-Type': 'application/json'}
        )
    except Exception as e:
        app.log.error(f"Failed to start transcription job for '{s3_uri}': {str(e)}")
        raise BadRequestError(f"Failed to start transcription job: {str(e)}") from e

@app.route('/transcript/download/{job_name}', methods=['GET'])
def get_transcript(job_name: str) -> Response:
    """
    Endpoint to get the transcription result for a given job ID (GET).
    """
    try:
        status, transcript_text = get_transcription_result(job_name)
    except Exception as e:
        raise BadRequestError(f"Error retrieving transcription result: {str(e)}") from e

    return Response(
        body={
            "job_name": job_name,
            "status": status,
            "transcript": transcript_text
        },
        status_code=200,
        headers={'Content-Type': 'application/json'}
    )
#
#endregion Transcription Endpoints --------------------------------------------

#region Interaction Endpoints -------------------------------------------------
#
@app.route('/chat/{session_id}', methods=['POST', 'PUT'], 
           content_types=['application/json'])
def chat(session_id: str) -> Response:
    """
    Endpoint to interact with a specific session (POST, PUT).
    """
    request = app.current_request
    data = getattr(request, 'json_body', {})
    user_input = data.get("message", "")
    if not user_input:
        raise BadRequestError("Missing 'message' in request body.")

    # Process user input and generate a response
    response = process_user_input(session_id, user_input)
    return response

def process_user_input(session_id: str, user_input: str) -> Response:
    """Process user input, invoke LLM, synthesize audio, store in S3 and return JSON with URL."""
    # 1. Retrieve session context from DynamoDB (if needed)
    pass

    # 2. Generate response using LLM agent
    reply = invoke_agent(user_input, session_id=session_id)

    # 3. Generate speech using TTS (if needed)
    try:
        audio = synthetize(reply)
    except Exception as e:
        raise BadRequestError(f"Error synthesizing speech: {str(e)}")

    # Upload audio to S3
    filename = f"sessions/{session_id}/{uuid.uuid4()}.ogg"
    try: 
        s3_ps_url = upload_audio_file(filename, audio, 'audio/ogg')
    except Exception as e:
        raise BadRequestError(f"Error uploading audio to S3: {str(e)}")

    # Return JSON response (do not stream audio directly)
    return Response(
        body={
            'session_id': session_id,
            'message': reply,
            'audio_url': s3_ps_url,
            'audio_key': filename,
            'expires_in': 300
        },
        status_code=200,
        headers={'Content-Type': 'application/json'}
    )
#
#endregion Interaction Endpoints ----------------------------------------------

# region Service checking Endpoints -------------------------------------------
#
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
    data = getattr(request, 'json_body', {}) or {}
    text = data.get("text", "")
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
#
#endregion Service checking Endpoints ----------------------------------------
