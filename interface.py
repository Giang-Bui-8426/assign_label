import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from datetime import datetime
import os
from tkinter import messagebox as mb
from PIL import Image, ImageTk
from functools import partial
from logic import check_folder,insert_database,export_csv,export_json,validate_data
import csv
import json
import tkinter.font as tkFont
from database import Database
from pillow_heif import register_heif_opener

register_heif_opener()
image_files = []
index_img = 0
def load_index(folder_path):
    global index_img
    if os.path.exists("storesIndex.json"):
        with open("storesIndex.json") as file:
            stores = json.load(file)
            if stores.get("folder_path") == folder_path:
                index_img = stores.get("last_index", 0)
def show_image(folder, filename, label_widget, size=(1200, 800),rotate_angle=0):
    image_path = os.path.join(folder, filename)
    if not os.path.exists(image_path):
        label_widget.config(text="Không tìm thấy ảnh", image="")
        return      
    try:
        img = Image.open(image_path) # mở file đọc ảnh
        img.thumbnail(size, Image.Resampling.LANCZOS) #resize kích thước 
        img_tk = ImageTk.PhotoImage(img) # trung gian tkinter và pillow
        
        label_widget.image = img_tk # lưu img vào biến của tkinter 
        label_widget.config(image=img_tk, text="") # thay đổi tt hiển thị lên ảnh 
    except Exception as e:
        label_widget.config(text=f"Lỗi load ảnh: {e} ", image="")
    
def handle_files(folder_path, img_label):  # xử lí lấy file hình ảnh
    global image_files
    global index_img
    try:
        files = os.listdir(folder_path)
        image_files = [
            f for f in files if f.lower().endswith((
                ".png", ".jpg", ".jpeg", ".gif",
                ".heic", ".heif", ".tiff", ".bmp", ".webp", ".jfif"
            ))
        ]
        if image_files:
            load_index(folder_path)
            show_image(folder_path, image_files[index_img], img_label)
        else:
            img_label.config(text="Không có ảnh trong folder")
    except Exception as e:
        img_label.config(text=f"Lỗi: {e}")
def next_image(folder, frame,stats):
    global index_img
    if not image_files:
        return
    index_img = (index_img + 1) % len(image_files)  # quay vòng
    show_image(folder, image_files[index_img], frame)
    from logic import load_data
    load_data(stats,image_files[index_img])
    return

def prev_image(folder, frame,stats):
    global index_img
    if not image_files:
        return
    index_img = (index_img - 1) % len(image_files)  # quay vòng
    show_image(folder, image_files[index_img], frame)
    from logic import load_data
    load_data(stats,image_files[index_img])
    return
    
def on_close(second,frame,folder):
    if mb.askokcancel("Xác nhận", "Bạn có muốn đóng ứng dụng không"):
        insert_database(tmp = True)
        save = {"folder_path" : folder,"last_index" : index_img}
        with open("storesIndex.json","w") as file:
            json.dump(save,file)
        second.destroy()
        frame.deiconify()
        from logic import db
        db.close_connection()
def open_second_window(app,folder):
    variable_name ={"product_name" :"" ,
                    "importer" : {"name_nhap" :"" , "address_nhap" : "", "sdt_nhap" : ""},
                    "manufacturer" : {"name_xuat" : "", "address_xuat" : "","sdt_xuat":""}
                    ,"manufacturing_date" : "", "expiry_date" : "", "type" : ""
                    }
    

    second = tb.Toplevel(app)
    second.title("Assign dataset")
    second.geometry("1500x1100")

    main_pane = tb.Frame(second)
    main_pane.pack(fill="both", expand=True)

    left_frame = tb.Frame(main_pane)
    left_frame.pack(side=LEFT, fill="both", expand=True, padx=10, pady=10)
    
    right_frame = tb.Frame(main_pane)
    right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    img_label = tb.Label(right_frame, text="No image", anchor="center")
    img_label.pack(fill="both", expand=True)
    handle_files(folder,img_label)

    container = tb.Frame(left_frame)
    container.pack(fill="both", expand=True)

    canvas = tb.Canvas(container)
    canvas.pack(side=LEFT, fill="both", expand=True)
    # khai báo thanh cuộn
    scrollbar = tb.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollbar.pack(side=LEFT, fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)

    scroll_frame = tb.Frame(canvas)
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    
    #tạo thanh cuôn
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    scroll_frame.bind("<Configure>", on_frame_configure)
    

    def on_window_resize(event,folder):
        window_width = second.winfo_width()
        img_size = min(1000, int(window_width * 0.4))
        show_image(folder,image_files[index_img], img_label, (img_size, img_size))
                        
    # lăng chuột
    def _on_mouse_wheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    def on_frame_configure(event): # cập nhật vùng cuộn
        canvas.configure(scrollregion=canvas.bbox("all"))
    scroll_frame.bind("<Configure>", on_frame_configure)

    def create_entry_field(parent, label_text, var_path, label_width=20):
        """Tạo entry field responsive với layout pack"""
        frame = tb.Frame(parent)
        frame.pack(fill="x", padx=10, pady=4)
        
        # Label bên trái với width cố định
        label = tb.Label(frame, text=label_text, width=label_width, anchor="w", 
                        font=("Segoe UI", 11))
        label.pack(side=LEFT)
        
        # Entry bên phải - sẽ expand theo width với minimum width
        entry = tb.Entry(frame, font=("Segoe UI", 11), width=40)
        entry.pack(side=LEFT, padx=(10, 5), fill="x", expand=True)
        
        # Lưu entry vào variable_name theo đường dẫn
        keys = var_path.split(".")
        tmp = variable_name
        for k in keys[:-1]:
            tmp = tmp[k]
        tmp[keys[-1]] = entry
        
        return frame

    # Header
    header_frame = tb.Frame(scroll_frame)
    header_frame.pack(fill="x", padx=15, pady=(15, 20))
    tb.Label(header_frame, text="ĐÁNH NHÃN SẢN PHẨM", 
             font=("Segoe UI", 18, "bold")).pack(anchor="w")

    # Tên sản phẩm
    create_entry_field(scroll_frame, "Tên sản phẩm:", "product_name")
    
    # Separator
    tb.Separator(scroll_frame, orient="horizontal").pack(fill="x", padx=15, pady=12)

    # Công ty nhập khẩu
    importer_frame = tb.LabelFrame(scroll_frame, text="Công Ty Nhập Khẩu", 
                                  padding=15, style="info.TLabelframe")
    importer_frame.pack(fill="x", padx=15, pady=8)
    
    create_entry_field(importer_frame, "Tên công ty:", "importer.name_nhap")
    create_entry_field(importer_frame, "Địa chỉ:", "importer.address_nhap")
    create_entry_field(importer_frame, "Số điện thoại:", "importer.sdt_nhap")

    # Công ty sản xuất
    manufacturer_frame = tb.LabelFrame(scroll_frame, text="Công Ty Sản Xuất", 
                                      padding=15, style="warning.TLabelframe")
    manufacturer_frame.pack(fill="x", padx=15, pady=8)
    
    create_entry_field(manufacturer_frame, "Tên công ty:", "manufacturer.name_xuat")
    create_entry_field(manufacturer_frame, "Địa chỉ:", "manufacturer.address_xuat")
    create_entry_field(manufacturer_frame, "Số điện thoại:", "manufacturer.sdt_xuat")

    # Separator
    tb.Separator(scroll_frame, orient="horizontal").pack(fill="x", padx=15, pady=12)

    # Thông tin sản phẩm
    product_info_frame = tb.LabelFrame(scroll_frame, text="Thông Tin Sản Phẩm", padding=15, style="success.TLabelframe")
    product_info_frame.pack(fill="x", padx=15, pady=8)
    
    create_entry_field(product_info_frame, "Ngày sản xuất (dd/mm/yyyy):", "manufacturing_date")
    create_entry_field(product_info_frame, "Hạn sử dụng (dd/mm/yyyy) :", "expiry_date")
    create_entry_field(product_info_frame, "Loại sản phẩm:", "type")
                

    btn_frame = tb.Frame(scroll_frame)
    btn_frame.pack(pady=10)
    tb.Button(btn_frame, text="Prev", bootstyle=WARNING, command=lambda:prev_image(folder,img_label,variable_name)).pack(side=LEFT, padx=5,fill="both",expand=True)
    tb.Button(btn_frame, text="Xác Nhận", bootstyle=SUCCESS, command=lambda:validate_data(variable_name,folder,image_files,index_img,img_label)).pack(side=LEFT, padx=5,expand=True,fill="both")
    tb.Button(btn_frame, text="Next", bootstyle=PRIMARY,command=lambda:validate_data(variable_name,folder,image_files,index_img,img_label)).pack(side=LEFT, padx=5,expand=True,fill="both")
    
    export_frame = tb.Frame(scroll_frame)
    export_frame.pack(pady=10)

    tb.Button(export_frame, text="Xuất CSV", bootstyle=INFO,command=lambda: export_csv("label.csv")).pack(side=LEFT, padx=10)
    tb.Button(export_frame, text="Xuất JSON", bootstyle=INFO,command=lambda: export_json("label.json")).pack(side=LEFT, padx=10)
    second.protocol("WM_DELETE_WINDOW", partial(on_close,second,app,folder))
    
    

    canvas.bind_all("<MouseWheel>", _on_mouse_wheel)
    second.bind("<Configure>", lambda e: on_window_resize(e,folder))
if __name__ == "__main__":
    app = tb.Window(themename="cosmo")
    app.title("Tra Cứu Sản Phẩm")
    app.geometry("450x150")

    labels = ["Nhập folder:"]

    for text in labels:
        frame = tb.Frame(app)
        frame.pack(pady=5, padx=10, fill="x")
        tb.Label(frame, text="Nhập folder:", width=20).pack(side=LEFT)
        folder = tb.Entry(frame, width=50, justify="center")
        folder.pack(side=LEFT, padx=5)

    tb.Button(app, text="Xác Nhận", bootstyle=SUCCESS, command=lambda:check_folder(app,folder)).pack( padx=20, pady=10)
    app.mainloop()