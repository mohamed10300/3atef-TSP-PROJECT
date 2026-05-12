import pandas as pd
from typing import Optional


VENDOR_COLUMNS = ["hotel_name", "vendor_price", "room_type"]
COMPETITOR_COLUMNS = ["hotel_name", "competitor_price"]


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
    )
    return df


def parse_vendor_sheet(path: str, sheet_name: str = "Vendor") -> dict[str, dict]:
    """Returns {hotel_name: {vendor_price, room_type}} from a vendor sheet."""
    try:
        df = pd.read_excel(path, sheet_name=sheet_name)
    except Exception:
        df = pd.read_excel(path, sheet_name=0)

    df = _normalize_columns(df)

    if "hotel_name" not in df.columns or "vendor_price" not in df.columns:
        raise ValueError(f"Excel sheet missing required columns. Found: {df.columns.tolist()}")

    df = df.dropna(subset=["hotel_name", "vendor_price"])
    df["vendor_price"] = pd.to_numeric(df["vendor_price"], errors="coerce").round(2)
    df = df.dropna(subset=["vendor_price"])

    result = {}
    for _, row in df.iterrows():
        name = str(row["hotel_name"]).strip()
        result[name] = {
            "vendor_price": float(row["vendor_price"]),
            "room_type": str(row.get("room_type", "")).strip() if "room_type" in df.columns else "",
        }
    return result


def parse_competitor_sheet(path: str, sheet_name: str = "Competitor") -> dict[str, float]:
    """Returns {hotel_name: competitor_price}."""
    try:
        df = pd.read_excel(path, sheet_name=sheet_name)
    except Exception:
        try:
            df = pd.read_excel(path, sheet_name=1)
        except Exception:
            return {}

    df = _normalize_columns(df)

    if "hotel_name" not in df.columns or "competitor_price" not in df.columns:
        return {}

    df = df.dropna(subset=["hotel_name", "competitor_price"])
    df["competitor_price"] = pd.to_numeric(df["competitor_price"], errors="coerce").round(2)
    df = df.dropna(subset=["competitor_price"])

    return {str(row["hotel_name"]).strip(): float(row["competitor_price"]) for _, row in df.iterrows()}


def preview_excel(path: str, rows: int = 10) -> list[dict]:
    df = pd.read_excel(path)
    df = _normalize_columns(df)
    return df.head(rows).to_dict(orient="records")
