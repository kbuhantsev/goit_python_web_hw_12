from fastapi import FastAPI
from src.routes.contacts import router as contacts_router
from src.routes.tests import router as tests_router
from src.routes.auth import router as auth_router

app = FastAPI()

app.include_router(contacts_router, prefix='/api')
app.include_router(auth_router, prefix='/api')
#
app.include_router(tests_router, prefix='/api')


@app.get("/")
def root():
    return {"message": "Welcome to FastAPI!"}
