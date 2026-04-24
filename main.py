from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from PIL import Image
import pillow_heif
import uuid
import io
import os
import requests

app = FastAPI()

pillow_heif.register_heif_opener()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET = "drive-carmanager"
API_KEY = os.getenv("API_KEY")


async def verify_key(request: Request):
    key = request.headers.get("x-api-key")

    if not key or key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.post("/convert")
async def convert(file: UploadFile = File(...), request: Request = None):
    await verify_key(request)

    file_id = str(uuid.uuid4())
    jpg_name = f"{file_id}.jpg"

    content = await file.read()

    heif_file = pillow_heif.read_heif(content)
    image = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw"
    )

    buffer = io.BytesIO()
    image.convert("RGB").save(buffer, format="JPEG")
    buffer.seek(0)

    upload_url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/uploads/{jpg_name}"

    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg"
    }

    requests.post(upload_url, data=buffer.read(), headers=headers)

    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/uploads/{jpg_name}"

    return {"url": public_url}