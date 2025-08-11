from tkinter import *
from tkinter import messagebox
import os
import re
import datetime
# Giao diện
window = Tk()
window.title("Tra Cứu Sản Phẩm")
window.geometry("400x400")
window.resizable(False, False)
lb2=Label(window,text="Tên Sản Phẩm",font='10')
lb2.grid(row= 1,column=1)
entry1 = Entry(window,font='10',bg='white',fg='black',bd=4,width=20)
entry1.grid(row=1,column =2)
lb3=Label(window,text="Tên Công Ty Nhập Khẩu",font='10')
lb3.grid( row= 2,column=1)
entry2 = Entry(window,font='10',bg='white',fg='black',bd=4,width=20)
entry2.grid(row=2,column =2)
lb4=Label(window,text="Công Ty Xuất Khẩu",font='10')
lb4.grid(row= 3,column=1)
entry3 = Entry(window,font='10',bg='white',fg='black',bd=4,width=20)
entry3.grid(row=3,column =2)
lb5=Label(window,text="Ngày Sản Xuất",font='10')
lb5.grid(row= 4,column=1)
entry4 = Entry(window,font='10',bg='white',fg='black',bd=4,width=20)
entry4.grid(row=4,column =2)
lb6=Label(window,text="Hạn Sử Dụng",font='10')
lb6.grid(row= 5,column=1)
entry5 = Entry(window,font='10',bg='white',fg='black',bd=4,width=20)
entry5.grid(row=5,column =2)
lb7=Label(window,text="Loại Sản Phẩm",font='10')
lb7.grid(row =6,column=1)
entry6 = Entry(window,font='10',bg='white',fg='black',bd=4,width=20)
entry6.grid(row=6,column =2)
lb8=Label(window,text="Nhập folder",font='10')
lb8.grid(row =7,column=1)
entry7 = Entry(window,font='10',bg='white',fg='black',bd=4,width=20)
entry7.grid(row=7,column =2)
# Logic
# Hàm kiểm tra định dạng ngày
def check_date_format(date_str):
    try:
        return datetime.datetime.strptime(date_str, "%d/%m/%Y")
    except ValueError:
        return None

# Hàm xác nhận dữ liệu
def click():
    ten_sp = entry1.get().strip()
    cty_nhap = entry2.get().strip()
    cty_xuat = entry3.get().strip()
    nsx = entry4.get().strip()
    hsd = entry5.get().strip()
    loai_sp = entry6.get().strip()
    folder = entry7.get().strip()
    #1.Kiểm tra không để trống
    if not all([ten_sp, cty_nhap, cty_xuat, nsx, hsd, loai_sp, folder]):
        messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
        return
    #2.Kiểm tra ngày tháng
    nsx_date = check_date_format(nsx)
    hsd_date = check_date_format(hsd)
    if not nsx_date or not hsd_date:
        messagebox.showerror("Lỗi", "Ngày phải đúng định dạng dd/mm/yyyy!")
        return
    if hsd_date <= nsx_date:
        messagebox.showerror("Lỗi", "Hạn sử dụng phải sau ngày sản xuất!")
        return
def kiem_tra_folder(path):
    if not path.strip():
        return False
    #Các ký tự đặc biệt
    invalid_chars = r'[<>:"/\\|?*]'
    if re.search(invalid_chars, path):
        return False
    # Kiểm tra xem có phải là một đường dẫn hợp lệ
    if not os.path.isdir(path):
        return False
    return True

#Test
def get():
    messagebox.showinfo("Thông báo", "Bạn đã nhấn Next!")
btn1=Button(window,text="Xác nhận",bg='white',fg='black',command=click)
btn1.place(x=200,y=220)
btn2=Button(window,text="Next",bg='white',fg='black',command=get)
btn2.place(x=350,y=220)
window.mainloop()
