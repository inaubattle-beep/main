from fastapi import FastAPI
from contextlib import asynccontextmanager
from memory.database import engine, Base, AsyncSessionLocal
from backend.api.endpoints import router as api_router
from core.agent_manager import load_agents_from_config
from core.task_manager import task_manager
from memory.models import User
from auth.security import get_password_hash
from sqlalchemy.future import select
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup DB dynamically
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Handle DB Seeds
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(User).where(User.username == "admin"))
        if not res.scalars().first():
            db.add(User(username="admin", hashed_password=get_password_hash("admin123"), is_admin=1))
            await db.commit()
            
        await load_agents_from_config(db, config_path="agents_config.json")
        
    # Start Execution Loop
    app.state.task_loop = asyncio.create_task(task_manager.start_loop())
    
    yield
    
    # Clean Shutdown
    task_manager.is_running = False
    app.state.task_loop.cancel()
    try:
        await app.state.task_loop
    except asyncio.CancelledError:
        pass

app = FastAPI(title="AI OS Layer", lifespan=lifespan)

app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
