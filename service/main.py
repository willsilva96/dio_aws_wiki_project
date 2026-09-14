from utils import require_env_var, management_bucket,get_document, upload_documents_kms

if __name__ == "__main__":
    BUCKET_NAME = "dio_project_wiki"
    MODO = "local"
    KMS_ARN = require_env_var("AWS_KMS_KEY_ARN")

    s3 = management_bucket(BUCKET_NAME, mode=MODO)

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
                kms_key_id=KMS_ARN
            )

            if upload_ok:
                if file_type in [".png", ".jpg",".jpeg"]:
                    print(f"-> OCR Rote: Image detect : {file_name}, send Amazon Textract")

                elif file_type == ".pdf":
                    print(f"-> Hibrid Rote: PDF detect: {file_name}. Try read with PyPDF. Fail try -> Textract")

                elif file_type == ".csv":
                    print(f"-> Tabular Rote: CSV file: {file_name}")


                    