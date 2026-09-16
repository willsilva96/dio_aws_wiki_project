import json
from connections import get_agent

def extract_metadata(
        agent,
        markdown_text: str
) -> dict:

    prompt = f"""
        Analise o documento corporativo abaixo e extraia as informações estritamente em formato JSON:
        {{
            "data_reuniao": "YYYY-MM-DD ou null se não identificada",
            "tema_principal": "Resumo em 1 frase do objetivo do documento",
            "participantes": ["lista com os nomes dos participantes"],
            "decisoes_tomadas": ["lista de decisões aprovadas"],
            "responsaveis": ["lista de pessoas que receberam tarefas"],
            "proximos_passos": ["lista de ações pendentes com prazos se houver"],
            "nivel_confidencialidade": "Publico, Interno ou Confidencial"
        }}

        Documento:fiz
        \"\"\"{markdown_text[:4000]}\"\"\"

        IMPORTANTE: Responda APENAS o JSON puro, sem textos introdutórios ou explicações.
        """

    response = agent(prompt)

    text_response = response.mensage if hasattr(response, "message") else str(response)

    text_clean = text_response.strip().replace("'''json","").replace("'''","").strip()

    try:
        metadata = json.loads(text_clean)
        return metadata

    except Exception as e:
        print(f"[JSON WARNING]: Could not parse response as JSON: {e}")
        return {"raw_response": text_response}