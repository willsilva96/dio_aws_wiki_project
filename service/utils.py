import io
import os
import csv
from pypdf import PdfReader
from pathlib import Path
from botocore.exceptions import ClientError
from typing import Optional
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from log import process_logger
load_dotenv()

log = process_logger()

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
        enable_object_lock: bool = True,
        trace_id: Optional[str] = None,
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
    log.info(
        f"Bucket '{bucket_name}' sucessfully created",
        extra={
            "batch_id": trace_id,
            "service": "S3",
            "status": "SUCESS",
            "document": bucket_name
        }
    )

# Gestão de buckets
def management_bucket(
        aws_s3_connection,
        bucket_name: str, 
        mode=None,
        trace_id: Optional[str] = None):

    if mode is None:
        return []
    
    try:
        aws_s3_connection.head_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' it already exists")

    except ClientError:
        log.info(
                f"Bucket '{bucket_name} not found. Creatiing..",
                    extra={
                        "batch_id": trace_id,
                        "service": "S3",
                        "status": "BUCKET_NOT_FOUND",
                        "document": bucket_name
                    })
        create_bucket(aws_s3_connection, 
                    bucket_name,
                    trace_id=trace_id)

    return aws_s3_connection

# Upload de documentos para S3 usando criptografia KMS
def upload_documents_kms(
        aws_s3_connection,
        file_path: str,
        bucket_name: str,
        s3_key: str,
        kms_key_id: Optional[str] = None,
        trace_id: Optional[str] = None
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
        log.info(
            f"File upload on S3 with KMS, on bucket '{bucket_name}'",
            extra={
                "trace_id": trace_id,
                "service": "S3",
                "status": "SUCESS",
                "document": f"{s3_key} for S3 Bucket: {bucket_name}"
            })
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
def apply_object_immutability(
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

def pdf_to_markdown(
        content_pdf_bytes: bytes) -> str:

    reader = PdfReader(io.BytesIO(content_pdf_bytes))

    lines_markdrown = []
    
    for index, page in enumerate(reader.pages, start=1):
        text_page = page.extract_text() or ""
        text_clean = text_page.strip()

        if text_clean:
            lines_markdrown.append(f"## Page {index}\n")
            lines_markdrown.append(text_clean)
            lines_markdrown.append("\n---\n")

    return "\n".join(lines_markdrown)

# Processa textract para markdown
def process_textract_to_markdown(
        textract_client,
        bucket: str,
        s3_key: str
) -> str:
    response = textract_client.detect_document_text(
        Document={"S3Object": {"Bucket": bucket, "Name": s3_key}}
    )

    lines_markdown = [f"# Transaction OCR: {s3_key.split("/")[-1]}\n"]

    for item in response.get("Blocks",[]):
        if item.get("BlockType") == "LINE":
            text_line = item.get("Text", "").strip()
            if text_line:
                lines_markdown.append(text_line)

    return "\n\n".join(lines_markdown)

                
# Salvar arquivo csv com AWS Lambda
def file_to_lambda(
        aws_s3_connection,
        bucket: str,
        s3_key: str,
        bucket_destination: str,
        s3_key_destionation: str,
        file_type: str,
        mode = None,
        trace_id: Optional[str] = None
) -> bool:
    from connections import get_s3_connection
    textract_client = get_s3_connection(mode=mode, service="textract",batch_id=trace_id)
    
    try:
        log.info(
            f"Read {s3_key} from bucket {bucket}",
            extra={
                "trace_id": trace_id,
                "service": "Lambda",
                "status": "Info",
                "document": f"{s3_key}, from {bucket}"
            })
        
        object_file = aws_s3_connection.get_object(Bucket=bucket, Key=s3_key)
        bytes_file = object_file["Body"].read()

        markdown_content = ""

        if file_type == ".csv":
            markdown_content = csv_to_markdown(bytes_file)

        elif file_type == ".pdf":
            markdown_content = pdf_to_markdown(bytes_file)

            if len(markdown_content.strip()) <50:
                log.info(
                    "PDF does not contais readable text. Send to Textract...",
                    extra={
                        "trace_id": trace_id,
                        "service": "Textract",
                        "status": "OCR_REQUIRED",
                        "document": s3_key
                    })
                process_textract_to_markdown(
                    textract_client=textract_client,
                    bucket=bucket,
                    s3_key=s3_key
                )

        elif file_type in [".txt", ".md",".docx"]:
            markdown_content = bytes_file.decode("utf-8-sig")

        elif file_type in [".png",".jpg",".jpeg"]:
            
            markdown_content = process_textract_to_markdown(
                textract_client=textract_client,
                bucket=bucket,
                s3_key=s3_key
            )

        else:
            log.info(
                f"Type '{file_type}' is not supported",
                extra={
                "trace_id": trace_id,
                "service": "Lambda",
                "status": "FAILED",
                "document": f"{file_type}, {s3_key}"
                })           
        
        management_bucket(
            aws_s3_connection=aws_s3_connection,
            bucket_name=bucket_destination,
            mode=mode)
        
        aws_s3_connection.put_object(
            Bucket=bucket_destination,
            Key=s3_key_destionation,
            Body=markdown_content.encode("utf-8"),
            ContentType="text/markdown"
        )

        log.info(
            f"Markdown saved on: s3://{bucket_destination}/{s3_key_destionation}",
            extra={
                "trace_id": trace_id,
                "service": "S3",
                "status": "SUCESS",
                "documents": s3_key_destionation
            })
        
        return True

    except ClientError as e:
            log.info(
                "Client Error",
                extra={
                    "trace_id": trace_id,
                    "service": "Lambda",
                    "status": "CLIENT_ERROR",
                    "document": e
                }
            )

def send_logs_s3(
        aws_s3_connection,
        bucket_logs: str,
        file_logs
):
    s3_key_log = f"audit_logs/{datetime.now().strftime("%Y-%m-%d")}/execution.log"

    aws_s3_connection.upload_file(
        Filename=file_logs,
        Bucket=bucket_logs,
        Key=s3_key_log
    )

    print(f"[AUDIT] Log saved on S3://{bucket_logs}/{s3_key_log}")

    