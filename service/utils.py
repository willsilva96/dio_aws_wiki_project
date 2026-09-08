from pathlib import Path

DIR = Path(__file__).resolve().parent.parent

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

# Arqui retorno os bytes de um arquivo
def get_document_bytes(file_name: str) -> bytearray:
    with open(file_name, "rb") as file:
        file = file.read()
        doc_bytes = bytearray(file)

        print(f"Document data read from {file_name}")

    return doc_bytes

