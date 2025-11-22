import os

def configure_telemetry():
    """
    Configura las variables necesarias para LangSmith si están presentes en el entorno.
    """
    # Asegurar que el tracing está activo si hay key
    if os.getenv("LANGCHAIN_API_KEY"):
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        # Nombre de proyecto por defecto si no está en .env
        if not os.getenv("LANGCHAIN_PROJECT"):
            os.environ["LANGCHAIN_PROJECT"] = "opsbot-v1-default"
    else:
        # Desactivar explícitamente si no hay key para evitar warnings
        os.environ["LANGCHAIN_TRACING_V2"] = "false"