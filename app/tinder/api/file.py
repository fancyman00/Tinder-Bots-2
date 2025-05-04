
import os
from fastapi import APIRouter, File, Form, UploadFile

images_dir = "C:/Users/fancy/Documents/WORK/Tinder-Bots/storage/tinder"

file_router = APIRouter(prefix="/bot/Tinder/file", tags=["Bot Tinder"])

@file_router.post("/upload-images/{bot_id}")
async def upload_images(
    bot_id: int,
    files: list[UploadFile] = File(...),
):
    try:
        responses = []
        bot_image_dir = f"{images_dir}/{bot_id}"
        if not os.path.isdir(bot_image_dir):
            os.mkdir(bot_image_dir)
        for file in files:
            contents = await file.read()
            file_path = f"{bot_image_dir}/{file.filename}"
            with open(file_path, "wb") as f:
                f.write(contents)
            responses.append({
                "filename": file.filename,
                "size": len(contents),
                "status": "success"
            })
        return {"results": responses}
    except Exception as e:
        return {"error": str(e)}