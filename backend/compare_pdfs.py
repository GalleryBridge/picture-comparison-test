from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from pdf2image import convert_from_bytes
import cv2
import numpy as np
from io import BytesIO
from PIL import Image

app = FastAPI(title="PDF Compare API", description="Compare two PDFs and return the difference")

@app.post("/compare")
async def compare_pdfs(file_a: UploadFile = File(...), file_b: UploadFile = File(...)):
  # 读取pdf文件
  pdf1_bytes = await file_a.read()
  pdf2_bytes = await file_b.read()

  # PDF -> 图片