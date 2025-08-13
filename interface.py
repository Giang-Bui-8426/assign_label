import ttkbootstrap as tb
from ttkbootstrap.constants import *
from logic import validate_data
import tkinter as tk
import re
from datetime import datetime
import os
from PIL import Image, ImageTk
from functools import partial
from ttkbootstrap.dialogs import Messagebox
from logic import check_folder
from logic import insert_database

image_files = []
index_img = 0
def show_image(folder, filename, label_widget, size=(700, 700)):
    image_path = os.path.join(folder, filename)
    if not os.path.exists(image_path):
        label_widget.config(text="Không tìm thấy ảnh", image="")
        return
    img = Image.open(image_path) # mở file đọc ảnh
    img.thumbnail(size, Image.Resampling.LANCZOS) #resize kích thước 
    img_tk = ImageTk.PhotoImage(img) # trung gian tkinter và pillow
    
    label_widget.image = img_tk # lưu img vào biến của tkinter 
    label_widget.config(image=img_tk, text="") # thay đổi tt hiển thị lên ảnh 
    
def handle_files(folder_path,img_label): # xử lí lấy file hình ảnh
    global image_files
    try:
        files = os.listdir(folder_path)
        image_files = [f for f in files if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))] # kiểm tra đuôi hình ảnh
        if image_files:
            index_img = 0
            show_image(folder_path, image_files[index_img], img_label)
    except Exception as e:
        img_label.config(text=f"Lỗi: {e}")
def next_image(folder, frame):
    global index_img
    if not image_files:
        return
    index_img = (index_img + 1) % len(image_files)  # quay vòng
    show_image(folder, image_files[index_img], frame)

def prev_image(folder, frame):
    global index_img
    if not image_files:
        return
    index_img = (index_img - 1) % len(image_files)  # quay vòng
    show_image(folder, image_files[index_img], frame)
def on_close():
    if Messagebox.okcancel("Thoát", "Đóng ứng dụng ?"):
        insert_database(tmp = True)
        second.destroy()

def open_second_window(app,folder):
    variable_name ={"product_name" :"" ,"manufacturer" : {"name_nhap" :"" , "adress_nhap" : "", "sdt_nhap" : ""},
                    "importer" : {"name_xuat" : "", "address_xuat" : "","sdt_xuat":""}
                    ,"manufacturing_date" : "", "expiry_date" : "", "type" : ""}
    

    second = tb.Toplevel(app)
    second.title("Assign dataset")
    second.geometry("1200x1100")

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

    canvas = tk.Canvas(container)
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
    
    # lăng chuột
    def _on_mouse_wheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    def on_frame_configure(event): # cập nhật vùng cuộn
        canvas.configure(scrollregion=canvas.bbox("all"))
    scroll_frame.bind("<Configure>", on_frame_configure)

    def Entry(root, text, var_name, pad_x=30,pad_y=5,size_font=12,width_entry = 60,padx_entry=10): # hàm tạo entry
        global image_files
        frame = tb.Frame(root)
        frame.pack(pady=pad_y,padx=pad_x,fill="x",expand=True)
        tb.Label(frame, text=text, width=20, anchor="w", font=("Segoe UI", size_font)).pack(padx=pad_x,side=LEFT,fill="both",expand=True,pady=pad_y)
        entry_widget = tb.Entry(frame, width=width_entry)
        entry_widget.pack(side=LEFT,pady=pad_y,padx=padx_entry,expand=True,fill="both")
        variable_name[var_name] = entry_widget  # Gán biến toàn cục

    tb.Label(scroll_frame,text="ĐÁNH NHÃN SẢN PHẨM",font=("Segoe UI",20,"bold")).pack(anchor="w",fill = "both",padx=170,expand=True)
    # Các ô nhập
    Entry(scroll_frame, "Tên sản phẩm : ","product_name",pad_y = (70,5),pad_x=5,size_font=15,width_entry=50,padx_entry=10)
    tb.Label(scroll_frame, text="Công Ty Nhập Khẩu:", font=("Segoe UI", 15)).pack(anchor="w", pady=(5, 3),expand=True,fill="both")
    Entry(scroll_frame, "Tên : ", variable_name["manufacturer"]["name_nhap"])
    Entry(scroll_frame, "Địa chỉ : ", variable_name["manufacturer"]["adress_nhap"])
    Entry(scroll_frame, "Số điện thoại : ", variable_name["manufacturer"]["sdt_nhap"])

    tb.Label(scroll_frame, text="Công Ty Sản Xuất:", font=("Segoe UI", 15)).pack(anchor="w", pady=(5, 3),expand=True,fill="both")
    Entry(scroll_frame, "Tên : ", variable_name["importer"]["name_xuat"])
    Entry(scroll_frame, "Địa chỉ : ", variable_name["importer"]["address_xuat"])
    Entry(scroll_frame, "Số điện thoại : ", variable_name["importer"]["sdt_xuat"])

    Entry(scroll_frame, "Ngày Sản Xuất : ", "manufacturing_date",pad_x=5,size_font=15,width_entry=50,padx_entry=10)
    Entry(scroll_frame, "Hạn Sử Dụng : ", "expiry_date",pad_x=5,size_font=15,width_entry=50,padx_entry=10)
    Entry(scroll_frame, "Loại Sản Phẩm : ", "type",pad_x=5,size_font=15,width_entry=50,padx_entry=10)
    canvas.bind_all("<MouseWheel>", _on_mouse_wheel)
                

    btn_frame = tb.Frame(scroll_frame)
    btn_frame.pack(pady=10)
    tb.Button(btn_frame, text="Prev", bootstyle=WARNING, command=partial(next_image,folder,img_label)).pack(side=LEFT, padx=5,fill="both",expand=True)
    tb.Button(btn_frame, text="Xác Nhận", bootstyle=SUCCESS, command=partial(validate_data,variable_name,folder,image_files,index_img,img_label)).pack(side=LEFT, padx=5,expand=True,fill="both")
    tb.Button(btn_frame, text="Next", bootstyle=PRIMARY,command=partial(prev_image,folder,img_label)).pack(side=LEFT, padx=5,expand=True,fill="both")

    second.protocol("WM_DELETE_WINDOW", on_close)

    canvas.bind_all("<MouseWheel>", _on_mouse_wheel)
if __name__ == "__main__":
    app = tb.Window(themename="cosmo")
    app.title("Tra Cứu Sản Phẩm")
    app.geometry("450x150")

    labels = ["Nhập folder:"]

    for text in labels:
        frame = tb.Frame(app)
        frame.pack(pady=5, padx=10, fill="x")
        tb.Label(frame, text=text, width=20).pack(side=LEFT)
        folder = tb.Entry(frame, width=50, justify="center")
        folder.pack(side=LEFT, padx=5)

    tb.Button(app, text="Xác Nhận", bootstyle=SUCCESS, command=partial(check_folder,app,folder)).pack( padx=20, pady=10)
    app.mainloop()