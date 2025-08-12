import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
import re
from tkinter import messagebox
from datetime import datetime
import os

def _on_mouse_wheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mouse_wheel)

    #  CỘT PHẢI
    right_frame = tb.Frame(main_pane, bootstyle="secondary")
    right_frame.pack(side=RIGHT, fill="both", expand=True)

    tb.Label(right_frame, text="Hiển Thị Sản Phẩm", font=("Segoe UI", 12, "bold")).pack(pady=10)



# Màn hình 1
app = tb.Window(themename="cosmo")
app.title("Tra Cứu Sản Phẩm")
app.geometry("450x150")

labels = ["Mời Nhập folder:"]

for text in labels:
    frame = tb.Frame(app)
    frame.pack(pady=5, padx=10, fill="x")
    tb.Label(frame, text=text, width=20).pack(side=LEFT)
    tb.Entry(frame, width=50, justify="center").pack(side=LEFT, padx=5)

tb.Button(app, text="Xác Nhận", bootstyle=SUCCESS, command=open_second_window).pack( padx=20, pady=10)

# Hàm chuẩn hóa và kiểm tra ký tự đặc biệt
def chuan_hoa_chuoi(text):
    text = text.strip().lower()
    # Chỉ cho phép chữ, số, khoảng trắng, dấu gạch ngang, gạch dưới
    if re.search(r"[^a-z0-9\s\-_]", text):
        return None
    return text

# Hàm kiểm tra ngày hợp lệ
def check_date_format(date_str):
    try:
        datetime.strptime(date_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False

def click():
    errors = []

    # Lấy dữ liệu và chuẩn hóa
    ten_sp = chuan_hoa_chuoi(entry1.get())
    cty_nhap = chuan_hoa_chuoi(entry2.get())
    cty_xuat = chuan_hoa_chuoi(entry3.get())
    nsx = entry4.get().strip()
    hsd = entry5.get().strip()
    loai_sp = chuan_hoa_chuoi(entry6.get())
    folder = entry7.get().strip()

    # 1. Kiểm tra nếu tất cả trường đều trống
    if not any([ten_sp, cty_nhap, cty_xuat, nsx, hsd, loai_sp]):
        errors.append("Cần nhập ít nhất một thông tin sản phẩm.")

    # 2. Kiểm tra chuỗi bị None (do có ký tự đặc biệt)
    if entry1.get().strip() and ten_sp is None:
        errors.append("Tên sản phẩm chứa ký tự đặc biệt.")
    if entry2.get().strip() and cty_nhap is None:
        errors.append("Công ty nhập khẩu chứa ký tự đặc biệt.")
    if entry3.get().strip() and cty_xuat is None:
        errors.append("Công ty xuất khẩu chứa ký tự đặc biệt.")
    if entry6.get().strip() and loai_sp is None:
        errors.append("Loại sản phẩm chứa ký tự đặc biệt.")

    # 3. Kiểm tra định dạng ngày nếu có nhập
    if nsx:
        if not check_date_format(nsx):
            errors.append("Ngày sản xuất không đúng định dạng dd/mm/yyyy.")
    if hsd:
        if not check_date_format(hsd):
            errors.append("Hạn sử dụng không đúng định dạng dd/mm/yyyy.")

    # 4. Kiểm tra HSD >= NSX
    if nsx and hsd and check_date_format(nsx) and check_date_format(hsd):
        nsx_date = datetime.strptime(nsx, "%d/%m/%Y")
        hsd_date = datetime.strptime(hsd, "%d/%m/%Y")
        if hsd_date < nsx_date:
            errors.append("Hạn sử dụng phải lớn hơn hoặc bằng ngày sản xuất.")

    # 5. Kiểm tra folder (nếu là bắt buộc)
    if folder and not os.path.exists(folder):
        errors.append("Thư mục không tồn tại.")

    # 6. Báo lỗi hoặc thành công
    if errors:
        messagebox.showerror("Lỗi", "\n".join(errors))
    else:
        messagebox.showinfo("Thành công", "Dữ liệu hợp lệ!")

app.mainloop()
