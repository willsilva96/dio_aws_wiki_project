import json
from typing import List, Dict, Any, Optional
from connections import get_s3_connection
from log import process_logger

log = process_logger()

# Divide markdown em pedaços menores para facilitar o processamento

def split_markdown_into_chunks(
        markdown_text: str,
        document_name: str,
        chunk_size_words: int = 400,
        overlad_works: int = 80
) -> List[Dict[str, Any]]: 

    paragrafs = [p.strip() for p in markdown_text.split("\n\n") if p.strip()]

    chunks = []
    buffer_words = []
    chunks_index = 1
    actual_session = "Introduction"

    for paragraf in paragrafs:
        if paragraf.startswith("#"):
            actual_session = paragraf.replace("#", "").strip()

            words_paragraf = paragraf.split()

            if len(buffer_words) + len(words_paragraf) > chunk_size_words and buffer_words:
                words_chunk = " ".join(buffer_words)

                chunks_id = f"{document_name.replace('.', '_')}_chunk_{chunks_index:03d}"
                chunks.append({
                    "chunk_id": chunks_id,
                    "document_name": document_name,
                    "section": actual_session,
                    "word_count": len(buffer_words),
                    "text": words_chunk
                })

                buffer_words = buffer_words[-overlad_works:] if len(buffer_words) > overlad_works else []
                chunks_index +=1


            buffer_words.extend(words_paragraf)

            if buffer_words:
                chunks_id = f"{document_name.replace('.', '_')}_chunk_{chunks_index:03d}"
                chunks.append({
                    "chunk_id": chunks_id,
                    "document_name": document_name,
                    "section": actual_session,
                    "chunk_index": chunks_index,
                    "word_count": len(buffer_words),
                    "text": " ".join(buffer_words)
                })

    if buffer_words:
        chunks_id = f"{document_name.replace('.', '_')}_chunk_{chunks_index:03d}"
        chunks.append({
            "chunk_id": chunks_id,
            "document_name": document_name,
            "section": actual_session,
            "chunk_index": chunks_index,
            "word_count": len(buffer_words),
            "text": " ".join(buffer_words)
        })

    return chunks

# Le os arquiovos .md processados e executa recorde semanantico, e sava fatiados no s3 para base fatorial
def proces_bucket_chunking(
        aws_s3_connection,
        bucket_processed: str,
        bucket_chunks_dest: Optional[str] = None,
        batch_id: Optional[str] = None
) -> List[Dict[str, Any]]:

    log.info(
        f"Starting semantic chunking process in the bucket {bucket_processed}",
        extra={
            "batch_id": batch_id,
            "service": "Indexer/Chunking",
            "status": "PROCESSING",
            "document": bucket_processed
        })

    all_chunks = []

    try:
        response = aws_s3_connection.list_objects_v2(
            Bucket=bucket_processed,
            Prefix="processed/"
        )

        for obj in response.get("Contents", []):
            s3_key = obj["Key"]

            if s3_key.endswith(".md"):
                doc_name = s3_key.split("/")[-1]
                print(f"[CHUNKING] Slicing document: {doc_name}...")

                object_s3 = aws_s3_connection.get_object(Bucket=bucket_processed, Key=s3_key)
                markdown_text = object_s3["Body"].read().decode("utf-8")

                doc_chunks = split_markdown_into_chunks(
                    markdown_text=markdown_text,
                    document_name=doc_name,
                    chunk_size_words=350, # estrategia de tokens para processamento
                    overlad_works=70 # estrategia de tokens para processamento
                )

                all_chunks.extend(doc_chunks)
                print(f"└─ Generated {len(doc_chunks)} chunks for '{doc_name}'.")

                if bucket_chunks_dest:
                    s3_key_chunks = f"chunks/{doc_name}.chunks.json"
                    aws_s3_connection.put_object(
                        Bucket=bucket_chunks_dest,
                        Key=s3_key_chunks,
                        Body=json.dumps(doc_chunks, indent=2, ensure_ascii=False).encode("utf-8"),
                        ContentType="application/json"
                    )

            log.info(
                f"Chunking completed successfully. Total chunks generated: {len(all_chunks)}",
                extra={
                    "batch_id": batch_id,
                    "service": "Indexer/Chunking",
                    "status": f"{len(all_chunks)} chunks"
                }
            )

            return all_chunks


    except Exception as e:
        log.error(
            f"Failure during the chunking process: {e}",
            exc_info=True,
            extra={
                "batch_id": batch_id,
                "service": "Indexer",
                "status": "FAILED"
            }
        )

    return []


if __name__ == "__main__":
    MODO = "local"
    BUCKET_PROCESSED = "dio_project_wiki_raw_processed"

    s3 = get_s3_connection(service="s3",mode=MODO)

    if s3:
        chunks = proces_bucket_chunking(
            aws_s3_connection=s3,
            bucket_processed=BUCKET_PROCESSED,
            bucket_chunks_dest=BUCKET_PROCESSED,
            batch_id="batch-test-chunking"
        )

        print(f"\n A total of {len(chunks)} chunks generated in the collection!")
        if chunks:
            print("\n Example of the first generated chunk:")
            print(json.dumps(chunks[0], indent=2, ensure_ascii=False))

    