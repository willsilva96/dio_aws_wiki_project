from utils import get_document, upload_documents_kms,require_env_var, file_to_lambda
from connections import get_s3_connection

if __name__ == "__main__":
    BUCKET_NAME = "dio_project_wiki_raw_data"
    MODO = "local"
    KMS_ARN = require_env_var("AWS_KMS_KEY_ARN")
    BUCKET_FILE_PROCESS = "dio_project_wiki_raw_processed"
    KMS_ARN_FILE_PROCESS = require_env_var("AWS_KMS_KEY_ARN_PROCESS")

    s3 = get_s3_connection(
        service="s3", 
        mode=MODO)

    if s3:
        documents = get_document()
        print(f"\n[INFO] {len(documents)} enter the raw folder")

        for doc in documents:
            file_path = doc["path"]
            file_name = doc["name"]
            file_type = doc["type"]
            s3_key = f"raw/{file_name}"

            print(f"\n --- Process: {file_name} ({file_type})")

            upload_ok = upload_documents_kms(
                aws_s3_connection=s3,
                file_path=file_path,
                bucket_name=BUCKET_NAME,
                s3_key=s3_key,
                kms_key_id=KMS_ARN,
                mode=MODO
            )

            if upload_ok:
                if file_type in [".csv",".pdf",".txt",".md"]:
                    s3_key_md = f"processed/{file_name.rsplit(".", 1)[0]}.md"

                    file_to_lambda(
                        aws_s3_connection=s3,
                        bucket=BUCKET_NAME,
                        s3_key=s3_key,
                        bucket_destination=BUCKET_FILE_PROCESS,
                        s3_key_destionation=s3_key_md,
                        file_type=file_type,
                        mode=MODO
                    )