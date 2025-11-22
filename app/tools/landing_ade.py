import os
from pathlib import Path
from landingai_ade import LandingAIADE

def extract_markdown_with_landing_ai(file_path: str) -> str:
    """
    Utiliza la librería oficial de Landing AI para parsear un documento
    y convertirlo a formato Markdown estructurado.
    """
    # La librería busca automáticamente VISION_AGENT_API_KEY en el entorno.
    # Si quieres asegurarte, puedes verificarlo antes:
    if not os.getenv("VISION_AGENT_API_KEY"):
        raise ValueError("Falta VISION_AGENT_API_KEY en las variables de entorno.")

    try:
        # Inicializar el cliente
        client = LandingAIADE()
        
        # Llamar a la API de Parse
        # model="dpt-2-latest" es el recomendado en la documentación
        response = client.parse(
            document=Path(file_path),
            model="dpt-2-latest"
        )
        
        # Retornar el markdown generado
        return response.markdown or "[No se pudo generar Markdown]"

    except Exception as e:
        print(f"❌ Error en Landing AI: {e}")
        raise e