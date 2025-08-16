
from database import Database
from datetime import datetime
import os
from functools import partial
from ttkbootstrap.dialogs import Messagebox

db = Database()
datas = []
def convert_date_format(date_str):  # chuyển chuỗi sang định dạng time
        if not date_str or not date_str.strip():
            return None
        try:
            return datetime.strptime(date_str.strip(), '%d-%m-%Y')
        except ValueError:
            return None

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
        Messagebox.show_error("Sai Folder", "Lỗi")
    else:
        from interface import open_second_window
        open_second_window(frame,folder_path)
        frame.withdraw()
def check_date_format(date_str):
    try:
        datetime.strptime(date_str, "%d/%m/%Y")
        return True
    except ValueError:        
        return False
def chuan_hoa_chuoi(text):
    text = text.strip().lower()
    # Chỉ cho phép chữ, số, khoảng trắng, dấu gạch ngang, gạch dưới
    if re.search(r"[^a-z0-9\s\-_]", text):
        return None
    return text
def check_nsx_hsd(nsx,hsd):
        cNSX = check_date_format(nsx)
        cHSD= check_date_format(hsd)
        if cHSD <= cNSX:
            Messagebox.show_error("Lỗi", "Lỗi xung đột date!")
            return
def insert_database(data = None,tmp = False):
    datas.append(data)
    if len(datas) == 100:
        db.insert_label(datas)
        datas.clear()
    if tmp and datas:
        db.insert_label(datas)
        datas.clear()
    #hàm update data         
def update_database(data, image_name):
    if not data or not image_name:
        Messagebox.show_error("Lỗi", "Thiếu dữ liệu hoặc tên ảnh!")
        return False

    result = db.update_product(image_name, data)
    if result:
        Messagebox.show_info("Thành công", f"Cập nhật sản phẩm {image_name} thành công!")
    else:
        Messagebox.show_error("Thất bại", f"Cập nhật sản phẩm {image_name} thất bại!")
    return result

def validate_data(stats,folder,images,idx,frame):
    list_stats = []
    image_base64 = image_to_base64(os.path.join(folder,images[idx]))
    stats["image_base64"] = image_base64
    stats["image_path"] = os.path.join(folder,images[idx])
    stats["image_name"] = images[idx]
    list_stats.append(stats)
    
    if not any(stats):
        Messagebox.show_error("Lỗi", "Vui lòng nhập thông tin!")
        return
    
    if not check_valid_data(stats):
        return

      ###########
    # viết lại info_Text sao cho nó in ra đúng định dạng
    info_text = info_text(
    f"Tên sản phẩm: {stats.get('product_name', '')}\n"
    f"Nhà sản xuất:\n"
    f"    Tên: {stats.get('manufacturer', {}).get('company_name', '')}\n"
    f"    Địa chỉ: {stats.get('manufacturer', {}).get('address', '')}\n"
    f"    SĐT: {stats.get('manufacturer', {}).get('phone', '')}\n"
    f"Nhà phân phối:\n"
    f"    Tên: {stats.get('importer', {}).get('company_name', '')}\n"
    f"    Địa chỉ: {stats.get('importer', {}).get('address', '')}\n"
    f"    SĐT: {stats.get('importer', {}).get('phone', '')}\n"
    f"Ngày sản xuất: {stats.get('manufacturing_date', '')}\n"
    f"Hạn sử dụng: {stats.get('expiry_date', '')}\n"
    f"Loại sản phẩm: {stats.get('type', '')}"
)
            # Hộp thoại hỏi yes no
    confirm = Messagebox.yesno()(
            "Xác nhận thông tin",
            f"Bạn đã nhập:\n\n{info_text}\n\nBạn có chắc chắn muốn lưu?"
        )
    if confirm == "Yes":
        Messagebox.show_info("Thành công", "Dữ liệu đã được lưu!")
        from interface import next_image
        
        
        for key, value in stats.items():
            if key not in ["image_base64","image_path","image_name"]:
                if key == "manufacturer" or key == "importer":
                    for k,item in value.items():
                        stats[key][k] = item.get()
                        item.delete(0,"end")
                else:
                    stats[key] = value.get()
                    value.delete(0, "end")
        next_image(folder,frame)
        #insert_database(list_stats)
    else:
        Messagebox.show_info("Hủy", "Dữ liệu chưa được lưu.")
    ####################
    # viết hàm kiểm tra dữ liệu nếu có 1 cái nào sai báo lỗi và kết thúc hàm 
def check_valid_data(stats):
    # Kiểm tra tên sản phẩm
    if not stats.get("product_name") or not chuan_hoa_chuoi(stats["product_name"]):
        Messagebox.show_error("Lỗi", "Tên sản phẩm không hợp lệ!")
        return False
    
    # Kiểm tra nhà sản xuất
    manufacturer = stats.get("manufacturer", {})
    if not manufacturer.get("company_name") or not chuan_hoa_chuoi(manufacturer["company_name"]):
        Messagebox.show_error("Lỗi", "Tên nhà sản xuất không hợp lệ!")
        return False
    if not manufacturer.get("address"):
        Messagebox.show_error("Lỗi", "Địa chỉ nhà sản xuất không được để trống!")
        return False
    if not manufacturer.get("phone") or not manufacturer["phone"].isdigit():
        Messagebox.show_error("Lỗi", "SĐT nhà sản xuất phải là số!")
        return False

    # Kiểm tra nhà phân phối
    importer = stats.get("importer", {})
    if not importer.get("company_name") or not chuan_hoa_chuoi(importer["company_name"]):
        Messagebox.show_error("Lỗi", "Tên nhà phân phối không hợp lệ!")
        return False
    if not importer.get("address"):
        Messagebox.show_error("Lỗi", "Địa chỉ nhà phân phối không được để trống!")
        return False
    if not importer.get("phone") or not importer["phone"].isdigit():
        Messagebox.show_error("Lỗi", "SĐT nhà phân phối phải là số!")
        return False

    # Kiểm tra ngày sản xuất, hạn sử dụng
    nsx = stats.get("manufacturing_date", "")
    hsd = stats.get("expiry_date", "")
    if not check_date_format(nsx):
        Messagebox.show_error("Lỗi", "Ngày sản xuất không đúng định dạng dd/mm/YYYY!")
        return False
    if not check_date_format(hsd):
        Messagebox.show_error("Lỗi", "Hạn sử dụng không đúng định dạng dd/mm/YYYY!")
        return False
    if datetime.strptime(hsd, "%d/%m/%Y") <= datetime.strptime(nsx, "%d/%m/%Y"):
        Messagebox.show_error("Lỗi", "Hạn sử dụng phải lớn hơn ngày sản xuất!")
        return False

    # Kiểm tra loại sản phẩm
    if not stats.get("type") or not chuan_hoa_chuoi(stats["type"]):
        Messagebox.show_error("Lỗi", "Loại sản phẩm không hợp lệ!")
        return False

    return True
    



    
