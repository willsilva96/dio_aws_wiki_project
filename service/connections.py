import boto3
from typing import Any, Callable, Literal, Optional, Sequence

from dotenv import load_dotenv
load_dotenv()

def require_env_var(var_name: str) -> str:
    val = os.getenv(var_name)
    if val is None or not val.strip():
        raise ValueError(
            f"[CONFIG ERRO] The required environment variable {var_name} was not found or is empty"
        )

    return val.strip()

ConnectionMode = Literal["local","production"]

def get_agent(
        mode: ConnectionMode = "local",
        tools: Optional[Sequence[Callable[...,Any]]] = None,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
) -> Any:

    if mode == "local":
        from strands.models.ollama import OllamaModel

        host_str = require_env_var("OLLAMA_HOST").strip("/")
        model_str = require_env_var("OLLAMA_MODEL_CODER")

        model_instance = OllamaModel(
            host=host_str,
            model_id=model_str,
            temperature=0.1,
        )

        if not system_prompt:
            system_prompt = "Você é um especialista em criação de tools e automações com Python e Strands"

    elif mode == "production":
        from strands.models.bedrock import BedrockModel

        model_str = require_env_var("BEDROCK_MODEL_DEFAULT")
        require_env_var("AWS_DEFAULT_REGION")

        model_instance = BedrockModel(model_id=model_str)

        if not system_prompt:
            system_prompt = "Você é um especialista em criação de tools e automações com Python e Strands, rodando na AWS"

    else:
        raise ValueError(f"Modo de conexão '{mode}' inválido ou não suportado")

    from strands import Agent 

    return Agent(
        model=model_instance,
        tools=list(tools) if tools else [],
        system_prompt=system_prompt,
        **kwargs,
    )

def get_s3_connection(
        mode: ConnectionMode = "local",
        service = None
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
            print(f"[INFO] Connecting to the LOCAL/FLOCI environment")

            s3_client = boto3.client(
                service_name=service,
                region_name=region_name,
                endpoint_url=endpoint_floci,
                aws_access_key_id=aws_access_key_id_floci,
                aws_secret_access_key=aws_secret_access_key_floci
            )
        elif mode == "production":
            print("[INFO] Connecting to the AWS Production environment")

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
