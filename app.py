from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
from agent import analyze_person

app = FastAPI()

class Request(BaseModel):
    description: str

@app.get("/", response_class=HTMLResponse)
async def home():
    return open("index.html").read()

@app.post("/analyze")
async def analyze(req: Request):
    result = analyze_person(req.description)
    return {"character_sheet": result}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)