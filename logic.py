from database import Database
from datetime import datetime
import os
import base64
import tkinter.messagebox as mb
import re
import csv
import json
from collections import OrderedDict


db = Database()
datas = []

def sort_doc(doc):
    return OrderedDict([
        ("image_name", doc.get("image_name")),
        ("image_path", doc.get("image_path")),
        ("image_base64", image_to_base64(doc.get("image_path"))),
        ("product_name", doc.get("product_name")),
        ("manufacturer", doc.get("manufacturer", {})),
        ("importer", doc.get("importer", {})),
        ("manufacturing_date", doc.get("manufacturing_date")),
        ("expiry_date", doc.get("expiry_date")),
        ("type", doc.get("type"))
    ])
def is_empty(doc):
    for v in doc.values():
        if isinstance(v, dict):  # importer / manufacturer
            if any(val.strip() for val in v.values() if isinstance(val, str)):
                return False
        elif isinstance(v, str):
            if v.strip():  # có chữ
                return False
    return True
def convert_date_format(date_str):  # chuyển chuỗi sang định dạng time
        if not date_str or not date_str.strip():
            return ""
        try:
            return datetime.strptime(date_str.strip(), '%d/%m/%Y')
        except ValueError as e:
            print("error : {e}")
            return date_str
def load_data(stats,name_image):
    try:
        doc = next((d for d in datas if d.get("image_name") == name_image), {})
        if not doc:
            doc = db.get_product(name_image)
        for key, value in stats.items():
            if key not in ["image_base64", "image_path", "image_name"]:
                if key in ["manufacturer", "importer"]:
                    for k, item in value.items():
                        item.delete(0, "end")
                        item.insert(0, doc.get(key, {}).get(k, ""))
                else:
                    value.delete(0, "end")
                    value.insert(0, str(doc.get(key, "")))   
    except Exception as e:
        print(f" Lỗi trong load_data({name_image}): {e}")
def image_to_base64(image_path): # chuyen doi base64
    try:
        if image_path and os.path.exists(image_path):
            with open(image_path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        return ""
    except Exception:
        return ""
def check_folder(frame,folder):
    folder_path = folder.get().strip()
    if folder_path and not os.path.exists(folder_path):
        mb.showerror("Sai Folder", "Lỗi")
    else:
        from interface import open_second_window
        open_second_window(frame,folder_path)
        frame.withdraw()
def date_format(date_str):
    """Kiểm tra định dạng ngày"""
    if not date_str or not date_str.strip():
        return True  # Cho phép rỗng
    try:
        datetime.strptime(date_str.strip(), "%d/%m/%Y")
        return True
    except ValueError:        
        return False
def check_text(text):
    text = text.strip()
    if text and re.search(r"[!@#$%^&*?\":{}|<>]", text):
        return None
    return True
def flatten_dict(doc, parent_key='', sep='.'):
    #Hàm giúp chuyển dich lồng thành dạng phẳng để ghi CSV dễ dàng.
    items = []
    for k, v in doc.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

# Hàm xuất CSV
def export_csv(filename):
    docs = db.get_all_products()
    if not docs:
        print("Không có dữ liệu để xuất CSV.")
        return
    docs = [sort_doc(d) for d in docs]
    # Flatten dicts để lấy đủ trường trong CSV (nhất là trường nested)
    flat_docs = [flatten_dict(doc) for doc in docs]

    # Lấy tất cả keys có trong tất cả document
    keys = set()
    for doc in flat_docs:
        keys.update(doc.keys())
    keys = sorted(keys)

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(flat_docs)
    print(f"Đã xuất CSV: {filename}")

# Hàm xuất JSON
def export_json(filename):
    docs = db.get_all_products()
    if not docs:
        print("Không có dữ liệu để xuất JSON.")
        return
    docs = [sort_doc(d) for d in docs]
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=4)
    print(f"Đã xuất JSON: {filename}")
def check_phone(phone):
    """Kiểm tra số điện thoại"""
    if not phone or not phone.strip():
        return True  # Cho phép rỗng
    phone = phone.strip()
    return phone.isdigit() and len(phone) >= 8 and len(phone) <= 15
def update_database(data):
    if not data or "image_name" not in data:
        return False
    return db.update_product(data["image_name"], data)
def insert_database(data = None,tmp = False):
    global datas
    if data:
        datas.append(data)
    if len(datas) == 100:
        db.insert_label(datas)
        datas.clear()
    if tmp and datas:
        db.insert_label(datas)
        datas.clear()

def check_valid_data(docs):
    # Kiểm tra tên sản phẩm
    try:
        product_name = docs.get("product_name", "")
        if not check_text(product_name):
            mb.showerror("Lỗi", "Tên sản phẩm không hợp lệ!")
            return False
        # Kiểm tra nhà nhập khẩu
        importer = docs.get("importer", {})
        if importer:
            if not check_text(importer.get("name_nhap", "")):
                mb.showerror("Lỗi", "Tên nhà nhập khẩu không hợp lệ!")
                return False
            if not check_text(importer.get("address_nhap", "")):
                mb.showerror("Lỗi", "Địa chỉ nhập khẩu không hợp lệ!")
                return False
            sdt_nhap = importer.get("sdt_nhap", "")
            if sdt_nhap and not sdt_nhap.isdigit():
                mb.showerror("Lỗi", "SĐT nhập khẩu phải là số!")
                return False
        # Kiểm tra nhà sản xuất
        manufacturer = docs.get("manufacturer", {})
        if manufacturer:
            if not check_text(manufacturer.get("name_xuat", "")):
                mb.showerror("Lỗi", "Tên nhà sản xuất không hợp lệ!")
                return False
            if not check_text(manufacturer.get("address_xuat", "")):
                mb.showerror("Lỗi", "Địa chỉ sản xuất không hợp lệ!")
                return False
            sdt_xuat = manufacturer.get("sdt_xuat", "")
            if sdt_xuat and not sdt_xuat.isdigit():
                mb.showerror("Lỗi", "SĐT sản xuất phải là số!")
                return False
        # Kiểm tra ngày sản xuất, hạn sử dụng
        nsx = docs.get("manufacturing_date", "")
        hsd = docs.get("expiry_date", "")
        if nsx and not date_format(nsx):
            mb.showerror("Lỗi", "Ngày sản xuất không đúng định dạng dd/mm/YYYY!")
            return False
        if hsd and not date_format(hsd):
            mb.showerror("Lỗi", "Hạn sử dụng không đúng định dạng dd/mm/YYYY!")
            return False
        if nsx and hsd:
            try:
                if datetime.strptime(hsd, "%d/%m/%Y") <= datetime.strptime(nsx, "%d/%m/%Y"):
                    mb.showerror("Lỗi", "Hạn sử dụng phải lớn hơn ngày sản xuất!")
                    return False
            except Exception:
                mb.showerror("Lỗi", "Ngày nhập không hợp lệ!")
                return False

        # Kiểm tra loại sản phẩm
        if not check_text(docs.get("type", "")):
            mb.showerror("Lỗi", "Loại sản phẩm không hợp lệ!")
            return False

        return True
    except Exception as e:
        print("Lỗi", f"Có lỗi xảy ra khi kiểm tra dữ liệu: {str(e)}")
        return False

def validate_data(stats,folder,images,idx,frame):
    document = {}
    for key, value in stats.items():
        if key == "manufacturer" or key == "importer":
            document[key] = {}
            for k,item in value.items():
                document[key][k] = item.get()
        else:
            document[key] = value.get()
    if is_empty(document):
        try:
            mb.showerror("Lỗi", "Vui lòng nhập thông tin!")
            return
        except Exception as e:
            print("errors", e)
    # viết hàm kiểm tra dữ liệu nếu có 1 cái nào sai báo lỗi và kết thúc hàm 
    if not check_valid_data(document):
        return
    #thêm & chuyển data
    document["image_path"] = os.path.join(folder,images[idx])
    document["image_name"] = images[idx]
    document["manufacturing_date"] = convert_date_format(document["manufacturing_date"])
    document["expiry_date"] = convert_date_format(document["expiry_date"])
    
    # format lưu ý
    info_text = (
    f"Tên sản phẩm: {document.get('product_name', '')}\n"
    f"Nhà sản xuất:\n"
    f"    Tên: {document.get('importer', {}).get('name_nhap', '')}\n"
    f"    Địa chỉ: {document.get('importer', {}).get('address_nhap', '')}\n"
    f"    SĐT: {document.get('importer', {}).get('sdt_nhap', '')}\n"
    f"Nhà phân phối:\n"
    f"    Tên: {document.get('manufacturer', {}).get('name_xuat', '')}\n"
    f"    Địa chỉ: {document.get('manufacturer', {}).get('address_xuat', '')}\n"
    f"    SĐT: {document.get('manufacturer', {}).get('sdt_xuat', '')}\n"
    f"Ngày sản xuất: {document.get('manufacturing_date', '')}\n"
    f"Hạn sử dụng: {document.get('expiry_date', '')}\n"
    f"Loại sản phẩm: {document.get('type', '')}"
    )
    
    confirm = mb.askyesno(
            "Xác nhận thông tin",
            f"Bạn đã nhập:\n\n{info_text}\n\nBạn có chắc chắn muốn lưu?"
        )
    # download dữ liệu
    if confirm:
        mb.showinfo("information", "Dữ liệu đã được lưu!")
        check = False
        for i,item in enumerate(datas):
            if item.get("image_name") == images[idx]:
                check = True
                break
        
        database = db.get_product(images[idx])
        if check:
            for i, d in enumerate(datas):
                if d.get("image_name") == images[idx]:
                    datas[i] = document
                    break
        elif database:
            update_database(document)
        else:
            insert_database(document)
        from interface import next_image
        next_image(folder,frame,stats)
    else:
        mb.showinfo("Hủy", "Dữ liệu chưa được lưu.")
    
