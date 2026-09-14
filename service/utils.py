import os
from pathlib import Path
from botocore.exceptions import ClientError
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

DIR = Path(__file__).resolve().parent.parent

def require_env_var(var_name: str) -> str:
    val = os.getenv(var_name)
    if val is None or not val.strip():
        raise ValueError(
            f"[CONFIG ERRO] The required environment variable {var_name} was not found or is empty"
        )

    return val.strip()

# Primeiro obtenho os atributos dos arquivos presentes na pasta raw
def get_document():
    raw_dir = DIR / "raw"

    if not raw_dir.exists():
        return []

    return [
        {
            "path": item,
            "name": item.name,
            "type": item.suffix.lower()
        }
        for item in raw_dir.iterdir()
        if item.is_file()
    ]

# Arquivo retorno os bytes de um arquivo
def get_document_bytes(file_name: str) -> bytearray:
    with open(file_name, "rb") as file:
        file = file.read()
        doc_bytes = bytearray(file)

        print(f"Document data read from {file_name}")

    return doc_bytes

# Cria um bucket do S#
def create_bucket(aws_s3_connection, bucket_name: str):
    aws_s3_connection.create_bucket(Bucket=bucket_name)
    print(f"Bucket '{bucket_name}' sucessfully created")

# Gestão de buckets
def management_bucket(bucket_name: str, mode=None):
    from connections import get_s3_connection

    if mode is None:
        return []
    
    aws_s3_connection = get_s3_connection(mode=mode,service="s3")

    try:
        aws_s3_connection.head_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' it already exists")

    except ClientError:
        print(f"Bucket '{bucket_name} not found. Creatiing...")
        create_bucket(aws_s3_connection, bucket_name)

    return aws_s3_connection

# Upload de documentos para S3 usando criptografia KMS
def upload_documents_kms(
        aws_s3_connection,
        file_path: str,
        bucket_name: str,
        s3_key: str,
        kms_key_id: Optional[str] = None
) -> bool:

    extra_args = {"ServerSideEncryption": "aws:kms"}
    if kms_key_id:
        extra_args["SSEKMSKeyId"] = kms_key_id

    try: 
        aws_s3_connection.upload_file(
        Filename=str(file_path),
        Bucket=bucket_name,
        Key=s3_key,
        ExtraArgs=extra_args
    )
        print(f"[Sucess] file upload with KMS, on bucket '{bucket_name}'")
        return True

    except ClientError as e:
        print(f"[Error] Fail to send file: {e}")
        return False


def extract_text_textract(textract_client, bucket_name: str, s3_key: str) -> str:
    try:
        response = textract_client.detect_document_text(
            Document={"S30bject": {"Bucket": bucket_name, "Name": s3_key}}
        )
        lines = [item["Text"] for item in response["Blocks"] if item["BlocksType"] == "LINE"]

        return "\n".join(lines)

    except ClientError as e:
        print(f"[Error Textract]: {e}")
        return ""
