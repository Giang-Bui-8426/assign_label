
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
             
def update_database(data,....): ################## viết hàm này data update sẽ truyền vào hàm update trong database của t
    pass 
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
    ####################
    # viết hàm kiểm tra dữ liệu nếu có 1 cái nào sai báo lỗi và kết thúc hàm 
    
    ###########
    # viết lại info_Text sao cho nó in ra đúng định dạng
    info_text = info_text = (
            f"Tên sản phẩm: {stats[""]}\n"
            f"Nhà sản xuất:\n"
            f"    Tên: {stats[1]}\n"
            f"    Địa chỉ: {stats[2]}\n"
            f"    SĐT: {stats[3]}\n"
            f"Nhà phân phối:\n"
            f"    Tên: {stats[4]}\n"
            f"    Địa chỉ: {stats[5]}\n"
            f"    SĐT: {stats[6]}\n"
            f"Ngày sản xuất: {stats[7]}\n"
            f"Hạn sử dụng: {stats[8]}\n"
            f"Loại sản phẩm: {stats[9]}"
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
    