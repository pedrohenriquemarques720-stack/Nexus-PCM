from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from pathlib import Path
import logging
import webbrowser
import threading

PRODUCT_NAME = "Nexus PCM"
PRODUCT_VERSION = "1.0.0"
PRODUCT_TAGLINE = "Sistema de Manutenção Industrial"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

TEMPLATES_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🚀 Iniciando {PRODUCT_NAME} v{PRODUCT_VERSION}")
    
    from app.core.database import engine, Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    await engine.dispose()

app = FastAPI(
    title=PRODUCT_NAME,
    description=PRODUCT_TAGLINE,
    version=PRODUCT_VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    html_path = TEMPLATES_DIR / "dashboard.html"
    if html_path.exists():
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
            content = content.replace("{{PRODUCT_NAME}}", PRODUCT_NAME)
            content = content.replace("{{PRODUCT_VERSION}}", PRODUCT_VERSION)
            return HTMLResponse(content=content)
    return HTMLResponse(content="<h1>Dashboard não encontrado</h1>", status_code=404)

@app.get("/health")
async def health():
    return {
        "product": PRODUCT_NAME,
        "version": PRODUCT_VERSION,
        "status": "healthy",
        "endpoints": "/docs, /api/v1"
    }

from app.api.v1.router import api_router
app.include_router(api_router, prefix="/api/v1")

def open_browser():
    """Abre o navegador automaticamente após o servidor iniciar"""
    webbrowser.open("http://localhost:8000")

if __name__ == "__main__":
    import uvicorn
    
    # Abre o navegador após 1.5 segundos (tempo para o servidor iniciar)
    timer = threading.Timer(1.5, open_browser)
    timer.start()
    
    uvicorn.run(app, host="0.0.0.0", port=8000)