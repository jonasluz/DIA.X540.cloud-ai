##
# app.py @ Project#3/backend/ppgia-x540-p3
# ----------------------------------
# Chalice application for the PPGIA X540 Project 3 backend.
# Author: Jonas de Araújo Luz Jr.
# Date: 2024-06-15
##
import os

import boto3
from chalice import Chalice, BadRequestError


# region Chalice app and Bedrock Agent client setup ---------------------------

app = Chalice(app_name='ppgia-x540-p3')

# Lê config do ambiente (setaremos no config.json)
REGION = os.environ.get("AWS_REGION", "us-east-1")
AGENT_ID = os.environ.get("BEDROCK_AGENT_ID")
AGENT_ALIAS_ID = os.environ.get("BEDROCK_AGENT_ALIAS_ID")

if not AGENT_ID or not AGENT_ALIAS_ID:
    # Falha cedo se não estiver configurado
    raise RuntimeError(
        "BEDROCK_AGENT_ID e BEDROCK_AGENT_ALIAS_ID precisam estar definidos "
        "como variáveis de ambiente da Lambda."
    )

# Cliente do *Agents for Amazon Bedrock Runtime*
# https://boto3.amazonaws.com/.../bedrock-agent-runtime.html :contentReference[oaicite:3]{index=3}
bedrock_agent_client = boto3.client(
    "bedrock-agent-runtime",
    region_name=REGION,
)


def _invoke_agent(prompt: str, session_id: str = "test-session") -> str:
    """
    Chama o Agent do Bedrock com um prompt simples e retorna o texto de resposta.
    Exemplo adaptado da doc oficial do Boto3. :contentReference[oaicite:4]{index=4}
    """
    response = bedrock_agent_client.invoke_agent(
        agentId=AGENT_ID,
        agentAliasId=AGENT_ALIAS_ID,
        sessionId=session_id,
        inputText=prompt,
    )

    completion = ""

    # A resposta vem em streaming de chunks de texto na chave "completion"
    for event in response.get("completion", []):
        chunk = event["chunk"]
        completion += chunk["bytes"].decode("utf-8")

    return completion

# endregion Chalice app and Bedrock Agent client setup ------------------------


# region Chalice app routes ---------------------------------------------------

@app.route('/agent/test', methods=['GET'])
def test_agent_get():
    """
    Endpoint simples de teste (GET). Usa um prompt fixo.
    """
    prompt = "Responda em português: diga apenas 'Olá, este é um teste do agente Bedrock via Chalice.'"
    reply = _invoke_agent(prompt)
    return {"prompt": prompt, "reply": reply}


@app.route('/agent', methods=['POST'], content_types=['application/json'])
def agent_post():
    """
    Endpoint mais geral (POST JSON):
    {
      "prompt": "...",
      "session_id": "opcional"
    }
    """
    req = app.current_request
    body = req.json_body or {}
    prompt = body.get("prompt")
    if not prompt:
        raise BadRequestError("Campo 'prompt' é obrigatório.")

    session_id = body.get("session_id", "default-session")
    reply = _invoke_agent(prompt, session_id=session_id)
    return {
        "session_id": session_id,
        "reply": reply,
    }
# endregion Chalice app routes ------------------------------------------------
