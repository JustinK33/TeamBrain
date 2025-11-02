from fastapi import FastAPI
from app.db.database import engine, Base
from app.routers import auth, users

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(users.router)