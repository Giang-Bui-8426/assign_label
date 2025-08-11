import os, csv,json, base64, unicodedata
from datetime import datetime
from pymongo import MongoClient

# ====== CẤU HÌNH MONGODB (đổi nếu cần) ======
MONGO_URI  = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB   = os.getenv("MONGO_DB", "bluebank")
MONGO_COLL = os.getenv("MONGO_COLL", "sanpham")

_client = MongoClient(MONGO_URI)
_db = _client[MONGO_DB]
_coll = _db[MONGO_COLL]
_coll.create_index("Loại sản phẩm")
_coll.create_index("Tên sản phẩm")

# ====== TIỆN ÍCH NHỎ, AN TOÀN ======
_FMT = ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d")

def _norm(s: str) -> str:
    return (s or "").strip()

def _parse_date(s: str) -> str:
    s = _norm(s)
    if not s: return ""
    for f in _FMT:
        try:
            return datetime.strptime(s, f).date().isoformat()   # yyyy-mm-dd
        except ValueError:
            pass
    # nếu người dùng đã nhập đúng yyyy-mm-dd thì giữ nguyên, sai thì để trống
    try:
        datetime.fromisoformat(s); return s
    except Exception:
        return ""

def _b64_from_path(path: str) -> str:
    p = _norm(path)
    if not p: return ""
    try:
        p = unicodedata.normalize("NFC", p)
        with open(p, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return ""

# ====== API CHÍNH ======
def luu_du_lieu(
    *,
    tieu_de: str = "",
    ten_san_pham: str = "",
    loai_san_pham: str = "",
    duong_dan_anh: str = "",

    # Công ty sản xuất
    sx_ten_cong_ty: str = "",
    sx_dia_chi: str = "",
    sx_sdt: str = "",

    # Công ty nhập khẩu
    nk_ten_cong_ty: str = "",
    nk_dia_chi: str = "",
    nk_sdt: str = "",

    # Công ty xuất khẩu (nếu có)
    xk_ten_cong_ty: str = "",
    xk_dia_chi: str = "",
    xk_sdt: str = "",

    ngay_san_xuat: str = "",
    ngay_het_han: str = "",
    ngay_su_dung: str = ""
) -> str:
    """
    Lưu 1 bản ghi. Bắt buộc: loai_san_pham và (duong_dan_anh hoặc Ảnh base64 tự sinh từ path).
    Trả về id dạng chuỗi.
    """
    doc = {
        "Tiêu đề": _norm(tieu_de),
        "Tên ảnh": os.path.basename(_norm(duong_dan_anh)) if duong_dan_anh else "",
        "Đường dẫn ảnh": _norm(duong_dan_anh),
        "Ảnh base64": _b64_from_path(duong_dan_anh),

        "Tên sản phẩm": _norm(ten_san_pham),
        "Loại sản phẩm": _norm(loai_san_pham),

        "Công ty sản xuất": {
            "Tên công ty": _norm(sx_ten_cong_ty),
            "Địa chỉ": _norm(sx_dia_chi),
            "Số điện thoại": _norm(sx_sdt),
        },
        "Công ty nhập khẩu": {
            "Tên công ty": _norm(nk_ten_cong_ty),
            "Địa chỉ": _norm(nk_dia_chi),
            "Số điện thoại": _norm(nk_sdt),
        },
        "Công ty xuất khẩu": {
            "Tên công ty": _norm(xk_ten_cong_ty),
            "Địa chỉ": _norm(xk_dia_chi),
            "Số điện thoại": _norm(xk_sdt),
        },

        "Ngày sản xuất": _parse_date(ngay_san_xuat),
        "Ngày hết hạn": _parse_date(ngay_het_han),
        "Ngày sử dụng": _parse_date(ngay_su_dung),
    }

    # kiểm tra tối giản — tránh lằng nhằng
    if not doc["Loại sản phẩm"]:
        raise ValueError("Thiếu 'Loại sản phẩm'.")
    if not (doc["Đường dẫn ảnh"] or doc["Ảnh base64"]):
        raise ValueError("Thiếu ảnh (đường dẫn hoặc base64).")

    # check logic ngày nếu có đủ cặp
    if doc["Ngày sản xuất"] and doc["Ngày hết hạn"]:
        try:
            if datetime.fromisoformat(doc["Ngày hết hạn"]) < datetime.fromisoformat(doc["Ngày sản xuất"]):
                raise ValueError("Ngày hết hạn sớm hơn ngày sản xuất.")
        except Exception:
            # nếu format không hợp lệ thì bỏ qua (đã cố parse ở trên)
            pass

    res = _coll.insert_one(doc)
    return str(res.inserted_id)

def xuat_csv(duong_dan_file: str, loai_filter: str = "") -> None:
    """
    Xuất CSV theo 'Loại sản phẩm' (để trống -> xuất tất cả)
    Cột CSV giữ nguyên tên cột tiếng Việt, phẳng hoá các trường lồng nhau.
    """
    query = {"Loại sản phẩm": _norm(loai_filter)} if _norm(loai_filter) else {}
    rows = _coll.find(query).sort([("_id", -1)])

    header = [
        "Tiêu đề",
        "Tên ảnh", "Đường dẫn ảnh", "Ảnh base64",
        "Tên sản phẩm", "Loại sản phẩm",
        "Công ty sản xuất.Tên công ty", "Công ty sản xuất.Địa chỉ", "Công ty sản xuất.Số điện thoại",
        "Công ty nhập khẩu.Tên công ty", "Công ty nhập khẩu.Địa chỉ", "Công ty nhập khẩu.Số điện thoại",
        "Công ty xuất khẩu.Tên công ty", "Công ty xuất khẩu.Địa chỉ", "Công ty xuất khẩu.Số điện thoại",
        "Ngày sản xuất", "Ngày hết hạn", "Ngày sử dụng",
    ]

    with open(duong_dan_file, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for d in rows:
            sx = d.get("Công ty sản xuất", {}) or {}
            nk = d.get("Công ty nhập khẩu", {}) or {}
            xk = d.get("Công ty xuất khẩu", {}) or {}
            w.writerow([
                d.get("Tiêu đề",""),
                d.get("Tên ảnh",""), d.get("Đường dẫn ảnh",""), d.get("Ảnh base64",""),
                d.get("Tên sản phẩm",""), d.get("Loại sản phẩm",""),
                sx.get("Tên công ty",""), sx.get("Địa chỉ",""), sx.get("Số điện thoại",""),
                nk.get("Tên công ty",""), nk.get("Địa chỉ",""), nk.get("Số điện thoại",""),
                xk.get("Tên công ty",""), xk.get("Địa chỉ",""), xk.get("Số điện thoại",""),
                d.get("Ngày sản xuất",""), d.get("Ngày hết hạn",""), d.get("Ngày sử dụng",""),
            ])