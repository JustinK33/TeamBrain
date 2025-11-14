from fastapi import FastAPI
from app.db.database import engine, Base
from app.routers import auth, users, spaces, messages
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # allow GET, POST, PUT, DELETE, OPTIONS, etc.
    allow_headers=["*"],  # allow Content-Type, Authorization, etc.
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(spaces.router)
app.include_router(messages.router)