from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
import tempfile
import os
import uvicorn
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
        
        # Get the character class for the frontend
        char_class = character.get("class", "Unknown")
        
        # Read PDF and return with custom header containing class info
        with open(pdf_path, "rb") as pdf_file:
            pdf_content = pdf_file.read()
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{os.path.basename(pdf_path)}"',
                "X-Character-Class": char_class,
                "Access-Control-Expose-Headers": "X-Character-Class"
            }
        )
    except Exception as e:
        return {"error": "Failed to generate PDF", "details": str(e)}
    finally:
        os.unlink(temp_json_path)
    #return {"character_sheet": result}


@app.get("/test-bard-pdf")
async def test_bard_pdf():
    """Generate and serve the bard character sheet PDF for testing"""
    import pathlib
    
    # Use pathlib for cross-platform path handling
    base_dir = pathlib.Path(__file__).parent
    json_path = base_dir / "dnd_pdf_filler_simple" / "examples" / "Character.bard.level3.json"
    output_folder = base_dir / "dnd_pdf_filler_simple" / "generated_character_sheets"
    
    try:
        pdf_path = generate_character_sheet(str(json_path), output_folder=str(output_folder))
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename="SilviusNightwhisper_Level3.pdf"
        )
    except Exception as e:
        import traceback
        return {"error": "Failed to generate PDF", "details": str(e), "traceback": traceback.format_exc()}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)