import io
import os
import csv
from pathlib import Path
from botocore.exceptions import ClientError
from typing import Optional
from datetime import datetime, timedelta, timezone
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

# Cria um bucket do S3
def create_bucket(
        aws_s3_connection, 
        bucket_name: str,
        enable_object_lock: bool = True
        ):

    if enable_object_lock:
        aws_s3_connection.create_bucket(
            Bucket=bucket_name,
            ObjectLockEnabledForBucket=True
        )

    else:
        aws_s3_connection.create_bucket(
            Bucket=bucket_name
        )
    
    print(f"Bucket '{bucket_name}' sucessfully created")

# Gestão de buckets
def management_bucket(
        aws_s3_connection,
        bucket_name: str, 
        mode=None):

    if mode is None:
        return []
    
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
        kms_key_id: Optional[str] = None,
        mode=None,
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

# Extrair texto de imagem com textract
def extract_text_textract(textract_client, bucket_name: str, s3_key: str) -> str:
    try:
        response = textract_client.detect_document_text(
            Document={"S3Object": {"Bucket": bucket_name, "Name": s3_key}}
        )
        lines = [item["Text"] for item in response["Blocks"] if item["BlockType"] == "LINE"]

        return "\n".join(lines)

    except ClientError as e:
        print(f"[Error Textract]: {e}")
        return ""

# Aplica modo de retenção para arquivos
def appl_object_immutability(
        aws_s3_connection,
        bucket_name: str,
        s3_key: str,
        retention_days: int = 365,
        mode: str = "COMPLIANCE"
) -> bool:

    expiration_date = datetime.now(timezone.utc) + timedelta(days=retention_days)

    try:
        aws_s3_connection.put_objetct_retention(
            Bucket=bucket_name,
            Key=s3_key,
            Retention={
                "Mode": mode,
                "RetatinUntilDate": expiration_date
            }
        )

        print(f"[IMMUTABILITY] File protected against deletion util {expiration_date}, Mode: {mode}")

    except Exception as e:
        print(f"[IMMUTABILITY WARNING] Objetct Lock could not be applied to...")

# Cols csv files
def format_cols_csv(col: str) -> str:
    return col.replace("_"," ").replace("-", " ").strip().title()

# Create Markdown
def csv_to_markdown(
        content_csv_bytes: bytes,
        title_document: Optional[str] = None,
        col_name: Optional[str] = None
) -> str:
    text_csv = content_csv_bytes.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text_csv))

    if not reader.fieldnames:
        return ""

    field_id = col_name if col_name else reader.fieldnames[0]

    lines_markdown = []
    if title_document:
        lines_markdown.append(f"# {title_document}\n")

    for index, line in enumerate(reader, start=1):
        value_id = line.get(field_id, f"registre {index}")
        lines_markdown.append(f"### {format_cols_csv(field_id)}:{value_id}")

        for col, value in line.items():
            if col == value_id:
                continue

            value_str = str(value).strip() if value is not None else ""

            if value_str:
                name_format = format_cols_csv(col)
                lines_markdown.append(f"- **{name_format}:** {value_str}")

        lines_markdown.append("")

    return "\n".join(lines_markdown)
                
# Salvar arquivo csv com AWS Lambda
def file_csv_lambda(
        aws_s3_connection,
        bucket: str,
        s3_key: str,
        bucket_destination: str,
        s3_key_destionation: str,
        mode = None
) -> bool:

    try:
        print(f"[LAMBDA] read {s3_key} from bucket {bucket}...")

        object_file = aws_s3_connection.get_object(Bucket=bucket, Key=s3_key)
        bytes_file = object_file["Body"].read()

        markdown = csv_to_markdown(bytes_file)

        management_bucket(
            aws_s3_connection=aws_s3_connection,
            bucket_name=bucket_destination,
            mode=mode)
        
        aws_s3_connection.put_object(
            Bucket=bucket_destination,
            Key=s3_key_destionation,
            Body=markdown,
            ContentType="text/markdown"
        )

        print(f"[SUCESSO] Markdown saved on: s3://{bucket_destination}/{s3_key_destionation}")
        return True

    except ClientError as e:
            print(f"[ERROR]: {e}")
            return False

