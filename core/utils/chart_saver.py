import os
import json
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

DASHBOARD_DIR = "data/dashboards"

def save_chart(chart_json: str):
    """
    Salva um gráfico JSON em um arquivo no diretório de dashboards.

    Args:
        chart_json (str): A string JSON do gráfico Plotly.
    """
    try:
        # Garantir que o diretório de dashboards exista
        os.makedirs(DASHBOARD_DIR, exist_ok=True)

        # Extrair o título do gráfico do JSON para usar no nome do arquivo
        chart_data = json.loads(chart_json)
        title = chart_data.get("layout", {}).get("title", {}).get("text", "grafico-sem-titulo")
        
        # Limpar o título para criar um nome de arquivo seguro
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_')).rstrip()
        safe_title = safe_title.replace(" ", "_").lower()

        # Criar um nome de arquivo único
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{timestamp}_{safe_title}_{unique_id}.json"
        filepath = os.path.join(DASHBOARD_DIR, filename)

        # Salvar o arquivo
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(chart_json)
        
        logger.info(f"Gráfico salvo com sucesso em: {filepath}")

    except Exception as e:
        logger.error(f"Erro ao salvar o gráfico: {e}", exc_info=True)
