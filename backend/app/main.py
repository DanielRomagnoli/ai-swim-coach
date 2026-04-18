from fastapi import FastAPI
from app.routes import upload

app = FastAPI()

app.include_router(upload.router)

@app.get("/")
def root():
    return {"message": "Swim AI Coach API running"}