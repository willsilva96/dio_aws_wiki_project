import boto3
from typing import Any, Callable, Literal, Optional, Sequence
from utils import require_env_var
from log import process_logger

log = process_logger()

ConnectionMode = Literal["local", "production"]

def get_agent(
        mode: ConnectionMode = "local",
        tools: Optional[Sequence[Callable[...,Any]]] = None,
        system_prompt: Optional[str] = None,
        batch_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        **kwargs: Any,
) -> Any:

    try:
        if mode == "local":
            from strands.models.ollama import OllamaModel

            host_str = require_env_var("OLLAMA_HOST").strip("/")
            model_str = require_env_var("OLLAMA_MODEL_CODER")

            log.info(
                f"Initializing Strands Agent with Local Ollama",
                extra={
                    "batch_id": batch_id,
                    "trace_id": trace_id,
                    "service": "Strands/Ollama",
                    "document": f"Host: {host_str}"
                }
            )

            model_instance = OllamaModel(
                host=host_str,
                model_id=model_str,
                temperature=0.1
            )

            if not system_prompt:
                system_prompt = "You are an expert in corporate governance and the extraction of metadata from minutes and corporate documents."

        elif mode == "production":
            from strands.models.bedrock import BedrockModel

            model_str = require_env_var("BEDROCK_MODEL_DEFAULT")
            require_env_var("AWS_DEFAULT_REGION")

            log.info(
                f"Initializing Strands Agent with Amazon Bedrok ({model_str})",
                extra={
                    "batch_id": batch_id,
                    "trace_id": trace_id,
                    "service": "Amazon Bedrock",
                    "status": "PROCESSING",
                    "document": f"model: {model_str}"
            })

            model_instance = BedrockModel(model_id=model_str)

            if not system_prompt:
                system_prompt = "You are an expert in corporate governance and the extraction of metadata from minutes and corporate documents."

        else:
            raise ValueError(f"[ERROR] Modo de conexão '{mode}' inválido ou não suportado.")

        from strands import Agent

        agent = Agent(
            model=model_instance,
            tools=list(tools) if tools else [],
            system_prompt=system_prompt,
            **kwargs
        )

        log.info(
            f"Agent with Strands ready for execution ({mode})",
            extra={
                "batch_id": batch_id,
                "trace_id": trace_id,
                "service": "Strands",
                "status": "SUCESS",
                "document": str(type(model_instance).__name__)
            }
        )

        return agent

    except Exception as e:
        log.error(
            f"Fail to initialize Agent ({mode}: {e})",
            extra={
                "batch_id": batch_id,
                "trace_id": trace_id,
                "service": "Strands",
                "status": "FAILED"
            }
        )
        raise e

def get_s3_connection(
        mode: ConnectionMode = "local",
        service = None,
        batch_id: Optional[str] = None,
        trace_id: Optional[str] = None
):  
    try:
        region_name = require_env_var("AWS_DEFAULT_REGION")

        endpoint_floci = require_env_var("AWS_FLOCI_ENDPOINT")
        aws_access_key_id_floci = require_env_var("AWS_FLOCI_KEY_ID")
        aws_secret_access_key_floci = require_env_var("AWS_FLOCI_SECRET_ACCESS_KEY")

        aws_access_key_id = require_env_var("AWS_KEY_ID")
        aws_secret_access_key = require_env_var("AWS_SECRET_ACCESS_KEY")

        if service is None:
            return []

        if mode == "local":
            log.info(
                f"Connecting to the LOCAL/FLOCI environment ({service})",
                extra={
                    "batch_id": batch_id,
                    "trace_id": trace_id,
                    "service": "AWS Local (FLOCI)",
                    "status": "SUCESS",
                    "documents": f"Region: {region_name}"
                }
            )

            s3_client = boto3.client(
                service_name=service,
                region_name=region_name,
                endpoint_url=endpoint_floci,
                aws_access_key_id=aws_access_key_id_floci,
                aws_secret_access_key=aws_secret_access_key_floci
            )
        elif mode == "production":
            log.info(
                f"Connecting to the AWS Production environment ({service})",
                extra={
                    "batch_id": batch_id,
                    "trace_id": trace_id,
                    "service":"AWS Production",
                    "status": "SUCESS",
                    "document": f"Region: {region_name}"

                })

            s3_client = boto3.client(
                region_name=region_name,
                service_name=service,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key

            )
        
        
        else:
            raise ValueError(f"Valid environment '{mode}'! Use 'local' or 'production'.")

        

        return s3_client

    except Exception as e:
        print(f"[ERROR] Failed to connect to {service} in ({mode}): {e}")
        log.info(f"[ERROR] Failed to connect to {service} in ({mode}): {e}")
