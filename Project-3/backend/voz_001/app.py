import os
import json
import uuid
import time
import base64
import urllib.request

import boto3
from chalice import Chalice, BadRequestError, Response

app = Chalice(app_name='chalice-ai-audio-translate')

s3 = boto3.client('s3')
transcribe = boto3.client('transcribe')
translate = boto3.client('translate')

AUDIO_BUCKET = os.environ.get('AUDIO_BUCKET', 'meu-bucket-audio')
TRANSCRIBE_OUTPUT_BUCKET = os.environ.get('TRANSCRIBE_OUTPUT_BUCKET', AUDIO_BUCKET)
DEFAULT_SOURCE_LANG = os.environ.get('DEFAULT_SOURCE_LANG', 'pt-BR')
DEFAULT_TARGET_LANG = os.environ.get('DEFAULT_TARGET_LANG', 'en')


@app.route('/translate-audio-file', methods=['POST'], content_types=['application/json'])
def translate_audio_file():
    req = app.current_request
    try:
        body = req.json_body or {}
    except Exception:
        raise BadRequestError("Body precisa ser JSON válido.")
    result = _process_audio_payload(body, request_type="file")
    return Response(
        status_code=200,
        headers={"Content-Type": "application/json"},
        body=json.dumps(result, ensure_ascii=False)
    )


@app.route('/translate-audio-live', methods=['POST'], content_types=['application/json'])
def translate_audio_live():
    req = app.current_request
    try:
        body = req.json_body or {}
    except Exception:
        raise BadRequestError("Body precisa ser JSON válido.")
    result = _process_audio_payload(body, request_type="live")
    return Response(
        status_code=200,
        headers={"Content-Type": "application/json"},
        body=json.dumps(result, ensure_ascii=False)
    )


def _process_audio_payload(body: dict, request_type: str):
    audio_b64 = body.get('audio_base64')
    if not audio_b64:
        raise BadRequestError("Campo 'audio_base64' é obrigatório.")
    source_lang = body.get('source_lang', DEFAULT_SOURCE_LANG)
    target_lang = body.get('target_lang', DEFAULT_TARGET_LANG)
    extension = body.get('extension', 'wav')
    try:
        audio_bytes = base64.b64decode(audio_b64)
    except Exception:
        raise BadRequestError("audio_base64 inválido (não foi possível decodificar).")
    object_key = f"{request_type}/uploads/{uuid.uuid4()}.{extension}"
    s3.put_object(
        Bucket=AUDIO_BUCKET,
        Key=object_key,
        Body=audio_bytes
    )
    media_uri = f"s3://{AUDIO_BUCKET}/{object_key}"
    job_name = f"job-{request_type}-{uuid.uuid4()}"
    transcript_text = run_transcription_job(
        job_name=job_name,
        media_uri=media_uri,
        media_format=extension,
        language_code=source_lang,
        output_bucket=TRANSCRIBE_OUTPUT_BUCKET
    )
    translated_text = translate_text(
        text=transcript_text,
        source_lang=_normalize_lang_for_translate(source_lang),
        target_lang=target_lang
    )
    return {
        "mode": request_type,
        "transcript": transcript_text,
        "translated_text": translated_text,
        "source_lang": source_lang,
        "target_lang": target_lang
    }


def run_transcription_job(job_name, media_uri, media_format, language_code, output_bucket):
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': media_uri},
        MediaFormat=media_format,
        LanguageCode=language_code,
        OutputBucketName=output_bucket,
    )
    while True:
        job = transcribe.get_transcription_job(
            TranscriptionJobName=job_name
        )['TranscriptionJob']
        status = job['TranscriptionJobStatus']
        if status in ('COMPLETED', 'FAILED'):
            break
        time.sleep(3)
    if status == 'FAILED':
        raise Exception(f"Transcription job failed: {job.get('FailureReason')}")
    transcript_uri = job['Transcript']['TranscriptFileUri']
    with urllib.request.urlopen(transcript_uri) as f:
        transcript_json = json.loads(f.read().decode('utf-8'))
    transcript_text = transcript_json['results']['transcripts'][0]['transcript']
    return transcript_text


def translate_text(text, source_lang, target_lang):
    resp = translate.translate_text(
        Text=text,
        SourceLanguageCode=source_lang,
        TargetLanguageCode=target_lang
    )
    return resp['TranslatedText']


def _normalize_lang_for_translate(transcribe_lang_code: str) -> str:
    if not transcribe_lang_code:
        return 'auto'
    return transcribe_lang_code.split('-')[0]
