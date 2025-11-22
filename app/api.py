import os
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from pyngrok import ngrok
import logging

# Importar el orquestador del grafo
from app.graph.workflow import run_extraction
from app.core.telemetry import configure_telemetry

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OPSBOT_API")

# Cargar variables de entorno
load_dotenv()

# Inicializar Telemetría (LangSmith)
configure_telemetry()

app = FastAPI(
    title="OpsBot PDF Extractor API",
    description="API para extraer datos estructurados de PDFs usando LangGraph + GPT-4o",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """
    Al iniciar, configura el túnel de Ngrok si está habilitado en .env
    """
    if os.getenv("USE_NGROK", "false").lower() == "true":
        auth_token = os.getenv("NGROK_AUTHTOKEN")
        if not auth_token:
            logger.warning("⚠️ USE_NGROK es true pero falta NGROK_AUTHTOKEN.")
            return
        
        try:
            # Configurar auth token
            ngrok.set_auth_token(auth_token)
            
            # Abrir túnel al puerto 8000
            # Si tienes dominio estático: pyngrok_config... o domain="..."
            public_url = ngrok.connect(8000).public_url
            
            logger.info(f"🚀 TÚNEL NGROK ACTIVO: {public_url}")
            logger.info(f"   -> Documentación: {public_url}/docs")
            logger.info(f"   -> Endpoint Extracción: {public_url}/extract")
            
            # Guardar URL en variable de entorno para referencia (opcional)
            os.environ["NGROK_PUBLIC_URL"] = public_url
            
        except Exception as e:
            logger.error(f"❌ Error iniciando Ngrok: {e}")

@app.get("/health")
async def health_check():
    """Health check para Power Automate / Monitoring"""
    return {"status": "ok", "service": "opsbot-extractor"}

@app.post("/extract")
async def extract_pdf(file: UploadFile = File(...)):
    """
    Endpoint principal: Recibe un PDF y devuelve la extracción estructurada.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF")

    logger.info(f"📥 Recibido archivo: {file.filename}")

    try:
        # Leer bytes del archivo
        file_bytes = await file.read()
        
        # Ejecutar el grafo de extracción (LangGraph)
        # metadata inyectada para trazas en LangSmith
        metadata = {"source": "api", "filename": file.filename}
        
        result = await run_extraction(file_bytes, metadata=metadata)
        
        if result.get("error"):
            logger.error(f"Error en proceso: {result['error']}")
            return JSONResponse(
                status_code=500, 
                content={"status": "error", "message": result["error"]}
            )

        return JSONResponse(content={
            "status": "success",
            "filename": file.filename,
            "summary": result.get("summary"),
            "text_preview": result.get("extracted_text", "")[:500] + "...", # Preview
            # Nota: Las tablas pueden ser grandes, considera devolver un link o estructura simplificada
            "tables_count": len(result.get("extracted_tables", []))
        })

    except Exception as e:
        logger.error(f"🔥 Error crítico en API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Para desarrollo local directo
    uvicorn.run(app, host="0.0.0.0", port=8000)