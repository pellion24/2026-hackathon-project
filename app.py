from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
import tempfile
import os
import uvicorn
import uuid
from agent import analyze_person
from dnd_pdf_filler_simple.generate_character import generate_character_sheet

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


class Request(BaseModel):
    description: str

@app.get("/", response_class=HTMLResponse)
async def home():
    return open("index.html").read()

@app.post("/analyze")
async def analyze(req: Request):
    result = analyze_person(req.description)
    #here is json

    # Strip markdown code fences if present
    result = result.strip()
    if result.startswith("```json"):
        result = result[7:]  # Remove ```json
    elif result.startswith("```"):
        result = result[3:]  # Remove ```
    if result.endswith("```"):
        result = result[:-3]  # Remove trailing ```
    result = result.strip()

    try:
        character = json.loads(result)
    except json.JSONDecodeError:
        return {"error": "Failed to parse character sheet", "raw": result}

    # 2. Save JSON to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(character, f)
        temp_json_path = f.name

    # 3. Generate PDF
    try:
        pdf_path = generate_character_sheet(temp_json_path, output_folder="/tmp/sheets")
        final_path = f"/tmp/sheets/{uuid.uuid4()}.pdf"
        os.rename(pdf_path, final_path)
        filename = os.path.basename(final_path)
        return {"pdf_url": f"/pdf/{filename}"}
        #return FileResponse(pdf_path, filename=os.path.basename(pdf_path), media_type="application/pdf")
    except Exception as e:
        return {"error": "Failed to generate PDF", "details": str(e)}
    finally:
        os.unlink(temp_json_path)
    #return {"character_sheet": result}


@app.get("/pdf/{filename}")
async def serve_pdf(filename: str):
    return FileResponse(f"/tmp/sheets/{filename}", media_type="application/pdf")

@app.get("/character", response_class=HTMLResponse)
async def character():
    return open("character.html").read()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)