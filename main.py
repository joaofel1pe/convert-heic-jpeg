from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import pillow_heif
import uuid
import io
import os
import requests


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://rmotors.carmanager.com.br",
        "https://api.carmanager.com.br",
        "https://convert.carmanager.com.br",
        "http://localhost:4200"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
pillow_heif.register_heif_opener()

SUPABASE_URL ="https://zykutzrqczcmsxevongl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp5a3V0enJxY3pjbXN4ZXZvbmdsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU2MTU0MjAsImV4cCI6MjA3MTE5MTQyMH0.J3zV3hEpY51Ae-_84wZz60ovkur_3xtTKgWuqv06gYI"
BUCKET = "drive-carmanager"
API_KEY = "asd"

async def verify_key(request: Request):
    key = request.headers.get("x-api-key")
    print(f"Received API key: {key}")
    if not key or key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorizedeee")


@app.post("/convert")
async def convert(arquivo: UploadFile = File(...), request: Request = None):
    print(dict(request.headers))
    await verify_key(request)

    file_id = str(uuid.uuid4())
    jpg_name = f"{file_id}.jpg"

    content = await arquivo.read()

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