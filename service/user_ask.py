import uuid
import sys
from utils import search_documents
from connections import ConnectionMode, get_s3_connection
from log import process_logger
from agents import load_skill_prompt,get_agent

log = process_logger()

def ask_wiki(
    query: str,
    mode: ConnectionMode = "local",
    BATCH_ID: str = f"batch-{uuid.uuid4().hex[:8]}"
):
    s3 = get_s3_connection(service="s3", mode=mode, batch_id=BATCH_ID, trace_id=BATCH_ID)

    bucket_processed = "dio_project_wiki_raw_processed"

    log.info(
        f"Receiving question {query}, Receiving a query and retrieving documents from S3: {bucket_processed}....",
        extra={
            "batch_id": BATCH_ID,
            "trace_id": BATCH_ID,
            "service": "LOCAL_USER_ASK",
            "level": "INFO",
            "status": "SUCESS",
            "document": {query}
        }
    )

    docs = search_documents(s3, bucket_processed, query)

    log.info(
        f"{len(docs)} document(s) uploaded to form the context." ,
        extra={
            "batch_id": BATCH_ID,
            "trace_id": BATCH_ID,
            "service": "Bedrock",
            "level": "INFO",
            "status": "SUCESS",
            "document": {query}
        }
    )

    context_str = ""
    for idx, d in enumerate(docs, 1):
        context_str += f"\n---Document [{idx}]: {d["source_file"]} ----\n"
        if d["metadata"]:
            context_str += f"Metadata: Data: {d["metadata"].get("data_reuniao")}, Tema: {d['metadata'].get("tema_principal")}\n"
        context_str += f"Content:\n {d["text"]}\n"

    system_prompt = load_skill_prompt("wiki_oracle")
    agent = get_agent(mode=mode, system_prompt=system_prompt, batch_id=BATCH_ID)

    user_prompt = f"""
    Contexto dos Documentos Corporativos da Empresa: 
    \"\"\"
    {context_str}
    \"\"\"

    Pergunta do colaborador: {query}

    Gere a reposta fundamentada citando as fontes de acordo com as instruções.    
    """

    respose = agent(user_prompt)
    raw_answer = respose.message if hasattr(respose, "message") else str(respose)

    log.info(
        f"Generating a reasoned response with the [Rag] agent",
        extra={
            "batch_id": BATCH_ID,
            "trace_id": BATCH_ID,
            "service": "Bedrock",
            "level": "INFO",
            "status": "SUCESS",
            "documents": raw_answer
        }
    )

    return raw_answer

if __name__ == "__main__":
    pergunta = "Quais foram as decisões tomadas sobre resultados de vendas e quem são o responsáveis citados?"
    if len(sys.argv) > 1:
        pergunta = " ".join(sys.argv[1:])

    ask_wiki(query=pergunta, mode="local")