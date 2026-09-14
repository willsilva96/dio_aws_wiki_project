from connections import get_s3_connection
from utils import get_document

def upload_file_s3(bucket:str, kms_key_arn: None) -> bool:
    extra_args = {"ServerSideEncryption": "aws:kms"}
    if kms_key_arn:
        extra_args["SSEKMSKey"] = kms_key_arn

    files = get_document()

    print(files)

upload_file_s3("teste","sadasdasd")

