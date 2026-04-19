from fastapi import FastAPI
from app.routes import upload
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat
from fastapi.staticfiles import StaticFiles



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(chat.router)

app.mount("/processed", StaticFiles(directory="processed"), name="processed")

@app.get("/")
def root():
    return {"message": "Swim AI Coach API running"}