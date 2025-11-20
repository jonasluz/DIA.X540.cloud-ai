##
# _bedrock.py
# ----------------------------------
# Bedrock agent invocation helper for the PPGIA X540 Project 3 backend.
#
##
import boto3

import chalicelib.chalice_config as config


# Bedrock Agent client setup
_bedrock_agent_client = boto3.client(
    "bedrock-agent-runtime",
    region_name=config.REGION,
)


def invoke_agent(prompt: str, session_id: str = "test-session") -> str:
    """
    Chama o Agent do Bedrock com um prompt simples e retorna o texto de resposta.
    Exemplo adaptado da doc oficial do Boto3. :contentReference[oaicite:4]{index=4}
    """
    response = _bedrock_agent_client.invoke_agent(
        agentId=config.AGENT_ID,
        agentAliasId=config.AGENT_ALIAS_ID,
        sessionId=session_id,
        inputText=prompt,
    )

    completion = ""

    # The response is a stream of events; we concatenate the 'bytes' from each chunk.
    for event in response.get("completion", []):
        chunk = event["chunk"]
        completion += chunk["bytes"].decode("utf-8")

    return completion

