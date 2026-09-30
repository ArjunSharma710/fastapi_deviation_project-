from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import deviations


app = FastAPI(
    title="AIVOA Deviation Management API",
    description="AI-powered deviation intake system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(deviations.router)


@app.get("/")
def root():
    return {"message": "AIVOA Deviation API is running"}