from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

app.include_router(molecules.router)
app.include_router(reactions.router)
app.include_router(elements.router)
app.include_router(catalog.router)
app.include_router(profile.router)

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
