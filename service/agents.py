import json
from pathlib import Path
from typing import Optional, Dict, Any
from connections import ConnectionMode, get_agent
from log import process_logger

log = process_logger()

DIR = Path(__file__).resolve().parent

def load_skill_prompt(
        skill_name: str,
)-> str:
    skiil_file = DIR / ".skills" / f"{skill_name}.md"

    if not skiil_file.exists():
        raise FileExistsError(f"Skill file not found: {skiil_file}")

    with open(skiil_file, "r", encoding="utf-8") as f:
        return f.read()

def skill_execute(
        skill_name: str,
        markdown_text: str,
        mode: ConnectionMode = "local",
        batch_id: Optional[str] = None,
        trace_id: Optional[str] = None
)-> Dict[str, Any]:

    system_prompt = load_skill_prompt(skill_name)

    agent = get_agent(
        mode=mode,
        system_prompt=system_prompt,
        batch_id=batch_id,
        trace_id=trace_id
    )

    user_prompt = f"Analise o documento corporativo a seguir e extraia o JSON conforme suas instruções:\n\n\"\"\"\n{markdown_text[:4000]}\n\"\"\""

    response = agent(user_prompt)
    raw_text = response.message if hasattr(response, "message") else str(response)

    clean_text = raw_text.strip().replace("'''json","").replace("'''","").strip()

    try:
        return json.loads(clean_text)

    except Exception as e:
        log.info(
            f"[JSON WARNING]: Could not parse response as JSON: {e}",
            extra={
                "batch_id": batch_id,
                "trace_id": trace_id,
                "service": "Bedrock",
                "status": "ERROR",
                "message": e
            }
        )
        return {}

def enrich_documents(
        aws_s3_connection,
        bucket_processed: str,
        skill_name: str = "meta_data_governace",
        mode: ConnectionMode = "local",
        batch_id: Optional[str] = None
):
    log.info(
        f"",
        extra={
            "batch_id": batch_id,
            "service": "Strands/Bedrock",
            "status": "PROCESSING",
            "document": bucket_processed
        }
    )

    try:
        response = aws_s3_connection.list_objects_v2(
            Bucket=bucket_processed,
            Prefix="processed"
        )

        content = response.get("Contents", [])
        if not content: 
            print(f"No files in s3//{bucket_processed}/processed")
            return

        for obj in content:
            s3_key = obj["Key"]

            if s3_key.endswith(".md"):
                trace_id = f"trace-meta-{s3_key.split('/')[-1][:6]}"

                print(f"\n [ENRICHMENT] Reading: s3://{bucket_processed}/{s3_key} ")

                object_s3 = aws_s3_connection.get_object(Bucket=bucket_processed, Key=s3_key)
                markdown_text = object_s3["Body"].read().decode("utf-8")

                metadata = skill_execute(
                    skill_name=skill_name,
                    markdown_text=markdown_text,
                    mode=mode,
                    batch_id=batch_id,
                    trace_id=trace_id
                )

                metadata["source_file"] = s3_key
                metadata["batch_id"] = batch_id
                metadata["trace_id"] = trace_id

                s3_key_metadata = f"{s3_key}.metadata.json"

                aws_s3_connection.put_object(
                    Bucket=bucket_processed,
                    Key=s3_key_metadata,
                    Body=json.dumps(metadata, indent=2, ensure_ascii=False).encode("utf-8"),
                    ContentType="application/json"
                )

                log.info(
                    f"Metadata successfully persisted in s3://{bucket_processed}/{s3_key_metadata}",
                    extra={
                        "batch_id": batch_id,
                        "trace_id": trace_id,
                        "service": "S3/Bedrock",
                        "status": "SUCESS",
                        "document": s3_key_metadata
                    }
                )
    except Exception as e:
        log.error(
            f"Failure during metadata enrichment: {e}",
            exc_info=True,
            extra={
                "batch_id": batch_id,
                "service": "Bedrock",
                "status": "FAILED"
            }
        )