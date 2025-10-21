# app/main.py

from fastapi import FastAPI

app = FastAPI(title="SmartSave API", version="1.0.0")


@app.get("/")
def root():
    return {"message": "SmartSave API is running "}
