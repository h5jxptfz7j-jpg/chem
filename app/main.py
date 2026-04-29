from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
from app.database import init_db, async_session, engine
from app.seed import seed_database
from app.routers import molecules, reactions, elements, catalog
from app.routers import profile

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    async with async_session() as session:
        await seed_database(session)
    yield
    await engine.dispose()

app = FastAPI(title="Telegram Mini App Chemistry", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API роутеры
app.include_router(molecules.router)
app.include_router(reactions.router)
app.include_router(elements.router)
app.include_router(catalog.router)
app.include_router(profile.router)

@app.get("/health")
async def health():
    return {"status": "ok"}

# Раздача статики (если есть папка static)
if os.path.exists("static"):
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join("static", full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse("static/index.html")
else:
    @app.get("/")
    async def root():
        return {"message": "API server running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
