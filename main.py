from fastapi import FastAPI
from src.routes.contacts import router as contacts_router

app = FastAPI()

app.include_router(contacts_router, prefix='/api')


@app.get("/")
def root():
    return {"message": "Welcome to FastAPI!"}
