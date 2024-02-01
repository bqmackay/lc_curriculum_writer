from fastapi import FastAPI
import main

app = FastAPI()

@app.get('/')
async def root():
    result = main.some_func()
    return {"message": result}