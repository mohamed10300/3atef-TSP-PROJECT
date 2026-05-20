import pandas as pd
import math

VENDOR_COLUMNS = ["hotel_name", "vendor_price", "room_type"]
COMPETITOR_COLUMNS = ["hotel_name", "competitor_price"]


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
        .str.replace(r"[^a-z0-9_]", "", regex=True)
    )
    return df


def _safe_float(val):
    try:
        f = float(val)
        return None if math.isnan(f) or math.isinf(f) else round(f, 2)
    except Exception:
        return None


def _map_company_format(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}
    if "hotel" in df.columns:
        rename_map["hotel"] = "hotel_name"
    if "rhk" in df.columns:
        rename_map["rhk"] = "competitor_price"
    if "our_price" in df.columns:
        rename_map["our_price"] = "vendor_price"
    for col in ["bookingcom", "booking_com", "booking"]:
        if col in df.columns and "booking_price" not in df.columns:
            rename_map[col] = "booking_price"
    for col in ["review_booking", "review"]:
        if col in df.columns and "review_score" not in df.columns:
            rename_map[col] = "review_score"
    if "rate" in df.columns:
        rename_map["rate"] = "star_rating"
    return df.rename(columns=rename_map)


def _load_and_clean(path: str, sheet_index: int = 0) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name=sheet_index, header=0)
    df = _normalize_columns(df)
    df = _map_company_format(df)
    if "hotel_name" in df.columns:
        df = df[df["hotel_name"].notna()]
        df = df[df["hotel_name"].astype(str).str.strip() != ""]
        df = df[~df["hotel_name"].astype(str).str.strip().isin(["All", "Sel.", "nan", "Hotel", "Hotel "])]
    return df


def parse_vendor_sheet(path: str, sheet_name: str = "Vendor") -> dict:
    try:
        df = _load_and_clean(path, sheet_index=0)
    except Exception as e:
        raise ValueError(f"Could not parse Excel file: {e}")

    if "hotel_name" not in df.columns:
        raise ValueError(f"Could not find hotel name column. Found: {df.columns.tolist()}")

    price_col = None
    for col in ["vendor_price", "competitor_price", "booking_price"]:
        if col in df.columns:
            price_col = col
            break

    if price_col is None:
        raise ValueError(f"Could not find any price column. Found: {df.columns.tolist()}")

    df = df.dropna(subset=["hotel_name", price_col])
    df[price_col] = pd.to_numeric(df[price_col], errors="coerce").round(2)
    df = df.dropna(subset=[price_col])

    result = {}
    for _, row in df.iterrows():
        name = str(row["hotel_name"]).strip()
        if not name or name.lower() == "nan":
            continue
        result[name] = {
            "vendor_price": _safe_float(row[price_col]),
            "room_type": "",
            "star_rating": _safe_float(row.get("star_rating")) if "star_rating" in df.columns else None,
            "distance": _safe_float(row.get("distance")) if "distance" in df.columns else None,
            "review_score": _safe_float(row.get("review_score")) if "review_score" in df.columns else None,
            "booking_price": _safe_float(row.get("booking_price")) if "booking_price" in df.columns else None,
        }
    return result


def parse_competitor_sheet(path: str, sheet_name: str = "Competitor") -> dict:
    try:
        df = _load_and_clean(path, sheet_index=0)
    except Exception:
        return {}
    if "hotel_name" not in df.columns or "competitor_price" not in df.columns:
        return {}
    df = df.dropna(subset=["hotel_name", "competitor_price"])
    df["competitor_price"] = pd.to_numeric(df["competitor_price"], errors="coerce").round(2)
    df = df.dropna(subset=["competitor_price"])
    return {str(row["hotel_name"]).strip(): _safe_float(row["competitor_price"]) for _, row in df.iterrows()}


def preview_excel(path: str, rows: int = 10) -> list:
    df = _load_and_clean(path, sheet_index=0)
    return df.head(rows).to_dict(orient="records")