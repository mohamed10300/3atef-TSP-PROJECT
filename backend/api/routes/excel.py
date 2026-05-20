"""POST /api/excel/upload — upload and parse Excel vendor/competitor sheet."""
import os
import uuid
import math
from fastapi import APIRouter, File, UploadFile, HTTPException
from backend.utils.excel_parser import parse_vendor_sheet, parse_competitor_sheet, preview_excel
from backend.utils.logger import get_logger

router = APIRouter(prefix="/api/excel", tags=["excel"])
logger = get_logger(__name__)
UPLOAD_DIR = "uploads"

def _clean(obj):
    """Recursively replace nan/inf floats with None for JSON safety."""
    if isinstance(obj, float):
        return None if (math.isnan(obj) or math.isinf(obj)) else obj
    if isinstance(obj, dict):
        return {k: _clean(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_clean(i) for i in obj]
    return obj

@router.post("/upload")
async def upload_excel(file: UploadFile = File(...)):
    if not file.filename.endswith((".xlsx", ".xls", ".csv")):
        raise HTTPException(status_code=400, detail="Only Excel/CSV files are accepted (.xlsx, .xls, .csv)")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    save_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
    try:
        content = await file.read()
        with open(save_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File save failed: {e}")
    try:
        vendor = parse_vendor_sheet(save_path)
        competitor = parse_competitor_sheet(save_path)
        preview = preview_excel(save_path, rows=10)
    except Exception as e:
        logger.error(f"excel upload parse error: {e}")
        raise HTTPException(status_code=422, detail=f"Failed to parse file: {e}")
    return _clean({
        "file_path": save_path,
        "vendor_rows": len(vendor),
        "competitor_rows": len(competitor),
        "preview": preview,
        "vendor_prices": vendor,
        "competitor_prices": competitor,
    })
