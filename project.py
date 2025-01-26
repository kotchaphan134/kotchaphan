import tkinter as tk
from tkinter import ttk, messagebox, filedialog, PhotoImage
import sqlite3
from datetime import datetime
from PIL import Image, ImageTk
import io
import shutil
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class CoffeeApp:       
    def __init__(self, root):
        # สร้างหน้า window
        self.root = root
        self.root.title("MN Coffee")
        self.root.attributes('-fullscreen', True)
        self.root.config(bg="#E9E7DC")

        # หน้าต่าง , แถบเลื่อน 
        self.main_canvas = tk.Canvas(self.root, bg="#E9E7DC")
        self.main_canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.main_canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.scrollable_frame = tk.Frame(self.main_canvas, bg="#E9E7DC")
        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollable_frame.bind("<Configure>", lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))

        # เพื่อเลื่อนเมาส์
        self.root.bind_all("<MouseWheel>", self.on_mouse_wheel)

        # ฟอนต์
        self.font10 = ("FC Subject [Non-commercial] Reg", 10) 
        self.font16 = ("FC Subject [Non-commercial] Reg", 16)
        self.font20 = ("FC Subject [Non-commercial] Reg", 20)           
        self.font40 = ("FC Subject Rounded [Non-cml.] B", 40)

        self.customer_name = ""
        self.table_number = "0"
        self.order_list = []  # ใช้เก็บรายการคำสั่งซื้อทั้งหมด

        # ตั้งค่า UI และ db
        self.init_db()
        self.setup_ui()

    def on_mouse_wheel(self, event):
        # mouse wheel
        self.main_canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")
    
    def init_db(self):
        self.conn = sqlite3.connect(r"C:\Users\user\Desktop\project\coffee.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (         
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                โต๊ะที่ TEXT,
                ชื่อลูกค้า TEXT,
                รายการ TEXT,
                ราคา REAL,
                สลิป TEXT,
                วันที่ DATE
            )''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ชื่อ TEXT ,
                ราคา REAL,
                path TEXT
            )''')

    def setup_ui(self):
        self.bar()
        self.head()
        self.input()
        self.display_menu()


    def bar(self):
        top_bar = tk.Frame(self.root, bg="#656863", height=60, width=1520)
        top_bar.place(x=0, y=0)
        top_bar.pack_propagate(False)

        sigh = tk.Label(
            top_bar, text=" MN Coffee",bg="#656863",fg="white", font=self.font16 ,height=2
        )
        sigh.pack(side="left", padx=5, pady=10)

        exit_button = tk.Button(
            top_bar, text=" ออกจากระบบ", command=root.destroy, bg="black",fg="white", font=self.font10 ,height=2
        )
        exit_button.pack(side="right", padx=5, pady=10)
        # ปุ่ม About Me
        about_button = tk.Button(
            top_bar, text=" 😀\nAbout Us", command=self.about, bg="#A7A79C", font=self.font10 ,height=2,width=10
        )
        about_button.pack(side="right", padx=5, pady=10)

        # ปุ่ม Admin
        admin_button = tk.Button(
            top_bar, text=" Admin", command=self.admin, bg="#A7A79C", font=self.font10 ,height=2,width=10
        )
        admin_button.pack(side="right", padx=5, pady=10)   


    def head(self):
        self.png = PhotoImage(file="C:/head.png")
        imageh = tk.Label(self.scrollable_frame, image=self.png, bg="#E9E7DC",height=220)
        imageh.image = self.png  # เก็บ reference ของภาพ
        imageh.pack(side="top", anchor="nw", padx=0, pady=45)

    def buttons(self):
        frame = tk.Frame(self.scrollable_frame, bg="#E9E7DC")
        frame.pack(pady=10)

        delete = tk.Button(frame, text="ลบรายการ", command=self.delete, bg="#CF8C8C", font=self.font16)
        delete.pack(side="left", padx=10)

        pay = tk.Button(frame, text="จ่ายเงิน", command=self.pay, bg="#909270", font=self.font16)
        pay.pack(side="left", padx=10)

    def input(self):
        input_frame = tk.Frame(self.scrollable_frame, bg="#E9E7DC")
        input_frame.pack(pady=10)

        # ชื่อลูกค้า
        tk.Label(input_frame, text="ชื่อลูกค้า:", font=self.font16, bg="#E9E7DC").grid(row=0, column=0, padx=5, pady=0, sticky="e")
        self.user = tk.Entry(input_frame, font=self.font16, width=35)
        self.user.insert(0, self.customer_name)  # เพิ่มข้อมูล
        self.user.grid(row=0, column=1, padx=5, pady=0, sticky="w")

        # โต๊ะที่
        tk.Label(input_frame, text="โต๊ะที่:", font=self.font16, bg="#E9E7DC").grid(row=0, column=2, padx=5, sticky="e")
        self.tb_num = tk.StringVar(value=self.table_number)  # เพิ่มข้อมูล
        self.tb_menu = ttk.Combobox(input_frame, textvariable=self.tb_num, values=[str(i) for i in range(0, 13)], font=self.font16, width=10, state="readonly")
        self.tb_menu.grid(row=0, column=3, padx=5, pady=0, sticky="w")
        

    def display_menu(self):
        self.menu = {}
        self.images = {}
        self.selected_menu = None

        # ดึงเมนูจาก db
        self.cursor.execute("SELECT ชื่อ, ราคา, path FROM menu")
        for row in self.cursor.fetchall():
            name, price, img_path = row
            self.menu[name] = int(price)
            self.images[name] = tk.PhotoImage(file=img_path)

        self.menu_per_page = 8  # จำนวนเมนูต่อหน้า
        self.current_page = 0  
        self.total_pages = (len(self.menu) + self.menu_per_page - 1) // self.menu_per_page

        self.update_menu_display()

    def update_menu_display(self):
        # ล้าง Frame เก่าของเมนู
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # เรียกใช้ head และ input
        self.head()
        self.input()

        # คำนวณเมนูที่จะแสดง
        start_index = self.current_page * self.menu_per_page
        end_index = start_index + self.menu_per_page
        items = list(self.menu.items())[start_index:end_index]

        frame = tk.Frame(self.scrollable_frame, bg="#E9E7DC")
        frame.pack(pady=10)

        for i, (name, price) in enumerate(items):
            button = tk.Button(frame, text=f"{name} - {price} บาท", compound="top", image=self.images[name], width=220, height=150,
                               font=self.font16, command=lambda n=name: self.select_menu(n), bg="#D3D3CA")
            button.grid(row=i // 4, column=i % 4, padx=5, pady=5)

        # ปุ่มถัดไป ,ย้อนกลับ
        nav_frame = tk.Frame(self.scrollable_frame, bg="#E9E7DC")
        nav_frame.pack(pady=10)

        if self.current_page > 0:
            prev_button = tk.Button(nav_frame, text="ย้อนกลับ", command=self.prev_page, font=self.font16, bg="#d7c596",width=10)
            prev_button.pack(side="left", padx=10)

        if self.current_page < self.total_pages - 1:
            next_button = tk.Button(nav_frame, text="ถัดไป", command=self.next_page, font=self.font16, bg="#d7c596",width=10)
            next_button.pack(side="left", padx=10)

        # ใช้ setup_option_var, list, buttons เพื่อแสดงตัวเลือก, ตาราง, และปุ่ม
        self.setup_option_var()
        self.list()
        self.buttons()

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.save_user_input()
            self.save_table_data() 
            self.current_page += 1
            self.update_menu_display()

    def prev_page(self):
        if self.current_page > 0:
            self.save_user_input()
            self.save_table_data()  
            self.current_page -= 1
            self.update_menu_display()

    def save_user_input(self):
        self.customer_name = self.user.get()
        self.table_number = self.tb_num.get()

    def setup_option_var(self):
        frame = tk.Frame(self.scrollable_frame, bg="#E9E7DC")
        frame.pack(pady=10)

        self.option_var = tk.StringVar(value="")
        for option, price in [("Hot", 5), ("Iced", 10), ("Mix", 15)]:
            tk.Radiobutton(frame, text=f"{option} (+{price} บาท)", variable=self.option_var, value=option, font=self.font16, bg="#E9E7DC").pack(side="left", padx=10)

        #จำนวนแก้ว
        tk.Label(frame, text="จำนวนแก้ว:", font=self.font16, bg="#E9E7DC").pack(side="left", padx=5)
        self.quantity_var = tk.IntVar(value=1)
        self.quantity_spinbox = tk.Spinbox(frame, from_=1, to=99, textvariable=self.quantity_var, font=self.font16, width=5)
        self.quantity_spinbox.pack(side="left", padx=10)

        # ปุ่มเพิ่มรายการ
        add = tk.Button(frame, text="เพิ่มรายการ", command=self.add, bg="#8FC0CB", font=self.font16)
        add.pack(side="right", padx=10)

    def list(self):
        self.style = ttk.Style()
        self.style.configure("Treeview.Heading", font=self.font16)
        self.style.configure("Treeview", rowheight=30, font=self.font16)

        list_frame = tk.Frame(self.scrollable_frame, bg="#E9E7DC")
        list_frame.pack(pady=10)

        self.tree = ttk.Treeview(list_frame, columns=("รายการ", "ราคา"), show='headings', height=7)
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.column("รายการ", width=500, anchor="center")
        self.tree.column("ราคา", width=300, anchor="center")
        self.tree.heading("รายการ", text="รายการ")
        self.tree.heading("ราคา", text="ราคา")

        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # เติมข้อมูลกลับเข้าตาราง
        for order in self.order_list:
            self.tree.insert("", "end", values=order)

    def save_table_data(self):
        self.order_list = []
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            self.order_list.append(values)  # เก็บข้อมูลในรูปแบบ tuple

    def buttons(self):

        frame = tk.Frame(self.scrollable_frame, bg="#E9E7DC")
        frame.pack(pady=10)

        delete = tk.Button(frame, text="ลบรายการ", command=self.delete, bg="#CF8C8C", font=self.font16)
        delete.pack(side="left", padx=10)

        pay = tk.Button(frame, text="จ่ายเงิน", command=self.pay, bg="#909270", font=self.font16)
        pay.pack(side="left", padx=10)

    def select_menu(self, name):
        self.selected_menu = name
        messagebox.showinfo("เลือกเมนู", f"คุณเลือก {name}")

    def add(self):
        # เพิ่มรายการไปยังตารางสั่งซื้อและ db
        table, customer,quantity = self.tb_num.get(), self.user.get(),self.quantity_var.get() 
        if table == "0" or not customer or not self.selected_menu or not self.option_var.get():
            messagebox.showwarning("ข้อผิดพลาด", "กรุณากรอกข้อมูลให้ครบถ้วน")

            return
        
        if quantity <=0 or quantity >=11:
            messagebox.showwarning("ข้อผิดพลาด", "กรุณากรอกข้อมูลให้ครบถูกต้อง")

            return
        
        #ทำราคา
        option = self.option_var.get()
        base_price = self.menu[self.selected_menu]
        extra_price = {"Hot": 5, "Iced": 10, "Mix": 15}[option]
        quantity = self.quantity_var.get()  #ดึงค่าจำนวนแก้ว
        total_price = (base_price + extra_price) * quantity  #คำนวณราคา

        self.order_list.append((f"{self.selected_menu} ({option}) x{quantity}", f"{total_price}"))

        # แสดงรายการในตาราง
        self.tree.insert("", "end", values=(f"{self.selected_menu} ({option}) x{quantity}", f"{total_price}"))
        self.cursor.execute('''
            INSERT INTO orders (โต๊ะที่, ชื่อลูกค้า, รายการ, ราคา, สลิป, วันที่)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (table, customer, f"{self.selected_menu} ({option}) x{quantity}", total_price, None, datetime.now().date()))
        self.conn.commit()

        # reset การเลือก
        self.selected_menu = None
        self.option_var.set("")
        self.quantity_var.set(1)  # รีเซ็ตจำนวนแก้วกลับเป็น 1

    def delete(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("ข้อผิดพลาด", "กรุณาเลือกรายการที่ต้องการลบ")
            return

        confirm = messagebox.askyesno("ยืนยันการลบ", "คุณต้องการลบรายการที่เลือกนี้หรือไม่?")
        if confirm:
            # ลบรายการที่เลือกจาก TreeView
            item = self.tree.item(selected_item)
            values = item['values']
            item_name = values[0]

            # ลบรายการจากฐานข้อมูล
            self.cursor.execute('''DELETE FROM orders WHERE รายการ = ?''', (item_name,))
            self.conn.commit()

            self.tree.delete(selected_item)

            messagebox.showinfo("สำเร็จ", "รายการได้รับการลบเรียบร้อยแล้ว")

            
    def pay(self):
        total = sum(int(self.tree.item(item, 'values')[1]) for item in self.tree.get_children())
        if total == 0:
            messagebox.showwarning("ข้อผิดพลาด", "ไม่มีรายการในตาราง")
            return
        
        self.show_payment_window(total)

    def show_payment_window(self, total):   #หน้าต่างชำระเงิน
        payment_window = tk.Toplevel(self.root)
        payment_window.title("ชำระเงิน")
        payment_window.attributes('-fullscreen', True)
        payment_window.config(bg="#E9E7DC")

        #ยอดรวม, คิวอาร์โค้ด
        tk.Label(payment_window, text=f"ยอดรวม {total:,.2f} บาท", font=self.font40, fg="white", bg="#585650", width=50, height=2).pack(pady=0)
        image = PhotoImage(file="C:/qr1.png")  
        self.png = PhotoImage(file="C:/qr1.png")
        imageqr = tk.Label(payment_window, image=self.png, bg="#E9E7DC")
        imageqr.pack(pady=20)
        
        #อัปโหลดสลิป
        upload = tk.Button(payment_window, text="ยืนยันการชำระเงิน (กรุณาอัพโหลดรูปสลิป)", command=self.slip, bg="#B2DFF7", font=self.font16)
        upload.pack(pady=10)

        close = tk.Button(payment_window, text="กลับ", command=lambda: [payment_window.destroy(), self.root.deiconify()], bg="#CF8C8C", font=self.font16)
        close.pack(pady=10)

    def slip(self):
        #กำหนดไฟล์สลิป
        path = filedialog.askopenfilename(title="เลือกไฟล์สลิป", filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if path:
            with open(path, 'rb') as file:
                data = file.read()  #อ่านข้อมูลใน binary mode

            # อัพเดต DB
            self.cursor.execute('''
                UPDATE orders SET สลิป = ? WHERE id = (SELECT MAX(id) FROM orders)
            ''', (data,))
            self.conn.commit()
            messagebox.showinfo("ชำระเงินเรียบร้อยแล้ว", "สลิปได้ถูกอัพโหลดแล้ว!")
            self.table_number = self.tb_num.get()
            self.create_receipt_pdf(r"C:\Users\user\Desktop\project\receipt.pdf")  # ทำ pdf
            self.show_receipt(r"C:\Users\user\Desktop\project\receipt.pdf")  # ขึ้น pdf

            # ล้างตาราง
            self.tree.delete(*self.tree.get_children())
            self.order_list = []  # Clear

    def create_receipt_pdf(self, filename):
        c = canvas.Canvas(filename, pagesize=(400, 1000))
        width, height = 400, 1000

        c.setFont("Helvetica", 32)
        c.drawCentredString(width / 2, height - 70, f"{self.table_number}")

        c.setFont("Helvetica", 22)
        c.drawCentredString(width / 2, height - 100, "MN Coffee")

        c.setFont("Helvetica", 12)
        c.drawCentredString(width / 2, height - 120, "Address: 123 Khonkaen, Thailand")
        c.drawCentredString(width / 2, height - 140, "Tel: 061-923-9991")
        c.drawCentredString(width / 2, height - 160, "---------------------------------------------------------------------")
        c.drawCentredString(width / 2, height - 180, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawCentredString(width / 2, height - 200, "---------------------------------------------------------------------")

        y = height - 220

        for order in self.order_list:
            item_name, price = order
            c.drawString(50, y, item_name)
            c.drawString(320, y, str(price))
            y -= 20

        total_price = sum(int(order[1]) for order in self.order_list)
        c.drawCentredString(width / 2, y - 20, f"Total: {total_price:,.2f} THB")
        c.drawCentredString(width / 2, y - 40, "**************************************************************")
        c.drawCentredString(width / 2, y - 60, "THANK YOU")
        c.save()

    def show_receipt(self, filename):
        import webbrowser
        webbrowser.open_new(filename)

    def show_slip(self, order_id):
        #แสดงรูปสลิป
        self.cursor.execute("SELECT slip_path FROM orders WHERE id = ?", (order_id,))
        data = self.cursor.fetchone()[0]
        if data:
            image = Image.open(io.BytesIO(data))  
            image = ImageTk.PhotoImage(image)
            label = tk.Label(self.root, image=image)
            label.image = image 
            label.pack()
            self.conn.commit()

    def closing(self):
        self.conn.close()
        self.root.destroy()

    def about(self):
        self.root.withdraw()
        about_window = tk.Toplevel(self.root)
        about_window.title("About Us")
        about_window.attributes('-fullscreen', True)
        about_window.config(bg="#F4EEED")
        
        # ปุ่มกลับ
        close = tk.Button(
            about_window, text="กลับ", command=lambda: [about_window.destroy(), self.root.deiconify()], bg="#D595A0", font=self.font16 ,width=10
        )
        close.pack(side="bottom", padx=20, pady=10)

        image = PhotoImage(file="C:/Abo.png")  
        self.png = PhotoImage(file="C:/Abo.png")
        imageab = tk.Label(about_window, image=self.png, bg="#F4EEED")
        imageab.pack(pady=0)

    def admin(self):
        self.root.withdraw()
        admin_window = tk.Toplevel(self.root)
        admin_window.title("Admin")
        admin_window.attributes('-fullscreen', True)
        admin_window.config(bg="#F4EEED")

        frame = tk.Frame(admin_window, bg="#F4EEED", height=150)
        frame.pack(pady=10)

        tk.Label(admin_window, text="กรุณากรอกรหัสผ่าน", font=self.font40).pack(anchor="center", pady=15)
        
        self.passw = tk.Entry(admin_window, font=self.font40, show="*", width=20)
        self.passw.pack(pady=10, anchor="center")

        def validate_password():
            pw = self.passw.get()
            if pw == "123456": 
                self.show_admin_dashboard(admin_window)
            else:
                messagebox.showwarning("ข้อผิดพลาด", "รหัสผ่านไม่ถูกต้อง กรุณาลองอีกครั้ง")
        
        frameb = tk.Frame(admin_window, bg="#F4EEED")
        frameb.pack(pady=10)

        exit_button = tk.Button(
            frameb, text=" กลับ", command=lambda: [admin_window.destroy(), self.root.deiconify()], bg="#D595A0", font=self.font16, height=1, width=10
        )
        exit_button.pack(side="left", padx=20, pady=10)

        tk.Button(
            frameb,
            text="ยืนยัน",
            command=validate_password,
            bg="#A7A79C",
            font=self.font16,
            width=10
        ).pack(side="left", padx=20, pady=10)

    def show_admin_dashboard(self, admin_window):
        admin_window.destroy()

        admin1_window = tk.Toplevel(self.root)
        admin1_window.title("Admin")
        admin1_window.attributes('-fullscreen', True)
        admin1_window.config(bg="#F4EEED")

        frame = tk.Frame(admin1_window, bg="#F4EEED", height=150)
        frame.pack(pady=10)
        tk.Label(admin1_window, text="Admin", font=self.font40, bg="#F4EEED").pack(pady=10)
        
        tk.Button(
            admin1_window,
            text="ตั้งค่าเมนู",
            command=self.setting,
            bg="#8FC0CB",
            font=self.font20
        ).pack(pady=10)

        tk.Button(
            admin1_window,
            text="ดูคำสั่งซื้อ",
            command=self.view_orders,
            bg="#8FC0CB",
            font=self.font20
        ).pack(pady=10)

        exit_button = tk.Button(
            admin1_window, text=" ย้อนกลับ", command=lambda: [admin1_window.destroy(), self.root.deiconify()], bg="#ff8d8d", font=self.font20, height=1, width=8
        )
        exit_button.pack(padx=20, pady=10)

    def show_menu_page(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()  
        self.setup_ui()  #สร้าง widgets ใหม่

    def setting(self):
        setting_window = tk.Toplevel(self.root)
        setting_window.title("ตั้งค่าเมนู")
        setting_window.attributes('-fullscreen', True)
        setting_window.config(bg="#E9E7DC")
        tk.Label(setting_window, text="แก้ไขเมนู", font=self.font40, bg="#E9E7DC").pack(side="top", pady=20)

        # Frame แสดงเมนู
        frame = tk.Frame(setting_window, bg="#E9E7DC")
        frame.pack(pady=5)

        # แสดงเมนูในตาราง
        menu_tree = ttk.Treeview(frame, columns=("ชื่อเมนู", "ราคา", "รูปภาพ"), show="headings", height=10)
        menu_tree.pack(side="left", fill="both", expand=True)

        menu_tree.column("ชื่อเมนู", width=300, anchor="center")
        menu_tree.column("ราคา", width=200, anchor="center")
        menu_tree.column("รูปภาพ", width=200, anchor="center")
        menu_tree.heading("ชื่อเมนู", text="----------------- ชื่อเมนู -----------------")
        menu_tree.heading("ราคา", text="------------ ราคา ------------")
        menu_tree.heading("รูปภาพ", text="------------ รูปภาพ ------------")

        # ดึงข้อมูลจาก db
        self.cursor.execute("SELECT ชื่อ, ราคา, path FROM menu")
        for row in self.cursor.fetchall():
            menu_tree.insert('', 'end', values=row)

        # แถบเลื่อน
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=menu_tree.yview)
        scrollbar.pack(side="right", fill="y")
        menu_tree.configure(yscrollcommand=scrollbar.set)

        # ฟอร์มเพิ่มและแก้ไขเมนู
        form_frame = tk.Frame(setting_window, bg="#E9E7DC")
        form_frame.pack(pady=5)

        tk.Label(form_frame, text="ชื่อเมนู:", font=self.font16, bg="#F4EEED").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        menu_name_entry = tk.Entry(form_frame, font=self.font16, width=30)
        menu_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        #ให้กรอกเป็น eng เท่านั้น
        def validate_english_input(char):
            if not char.isascii():
                messagebox.showwarning("ข้อผิดพลาด", "กรุณากรอกเป็นภาษาอังกฤษ")
                return False
            return True

        validate_command = (self.root.register(validate_english_input), '%S')
        menu_name_entry.config(validate="key", validatecommand=validate_command)

        tk.Label(form_frame, text="ราคา:", font=self.font16, bg="#F4EEED").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        menu_price_entry = tk.Entry(form_frame, font=self.font16, width=30)
        menu_price_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # ปุ่มเลือกภาพ
        image_path = tk.StringVar()
        tk.Label(form_frame, text="รูปภาพ:", font=self.font16, bg="#F4EEED").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(form_frame, textvariable=image_path, font=self.font16, width=30, state="readonly").grid(row=2, column=1, padx=5, pady=5, sticky="w")

        def select_image():
            path = filedialog.askopenfilename(title="เลือกไฟล์รูปภาพ", filetypes=[("Image files", ".png;.jpg;*.jpeg")])
            if path:
                image_path.set(path)

        tk.Button(form_frame, text="เลือกไฟล์", command=select_image, bg="#D3D3CA", font=self.font16).grid(row=2, column=3, padx=5, pady=5)

        # เพิ่มเมนูใหม่
        def add_menu():
            self.menu_items = list(self.menu.items())  # แปลง dictionary ให้เป็นลิสต์
            name = menu_name_entry.get().strip()
            try:
                price = int(menu_price_entry.get().strip())
                img_path = image_path.get()
                if name and price > 0 and img_path:
                    self.cursor.execute("INSERT INTO menu (ชื่อ, ราคา, path) VALUES (?, ?, ?)", (name, price, img_path))
                    self.conn.commit()
                    menu_tree.insert('', 'end', values=(name, price, img_path))
                    menu_name_entry.delete(0, 'end')
                    menu_price_entry.delete(0, 'end')
                    image_path.set("")
                    # เรียกฟังก์ชันเพื่อรีเฟรชเมนูในหน้าหลัก
                    self.menu_items = list(self.menu.items())
                    self.show_menu_page()
                else:
                    messagebox.showwarning("ข้อผิดพลาด", "กรุณากรอกข้อมูลให้ครบถ้วน")
            except ValueError:
                messagebox.showwarning("ข้อผิดพลาด", "ราคาต้องเป็นตัวเลข")

        # ลบเมนู
        def delete_menu():
            selected = menu_tree.selection()
            if not selected:
                messagebox.showwarning("ข้อผิดพลาด", "กรุณาเลือกเมนูที่ต้องการลบ")
                return

            for item in selected:
                name = menu_tree.item(item, "values")[0]
                if name in self.menu:
                    del self.menu[name]
                    del self.images[name]
                self.cursor.execute("DELETE FROM menu WHERE ชื่อ = ?", (name,))
                self.conn.commit()
                menu_tree.delete(item)
            self.show_menu_page()

        # แก้ไขเมนู
        def edit_menu():
            selected = menu_tree.selection()
            if not selected or len(selected) > 1:
                messagebox.showwarning("ข้อผิดพลาด", "กรุณาเลือกเมนูเพียงรายการเดียวเพื่อแก้ไข")
                return

            item = selected[0]
            old_name = menu_tree.item(item, "values")[0]
            new_name = menu_name_entry.get().strip() or old_name
            try:
                new_price = menu_price_entry.get().strip()
                new_price = int(new_price) if new_price else menu_tree.item(item, "values")[1]
                new_img_path = image_path.get() or menu_tree.item(item, "values")[2]
                self.cursor.execute("UPDATE menu SET ชื่อ = ?, ราคา = ?, path = ? WHERE ชื่อ = ?", (new_name, new_price, new_img_path, old_name))
                self.conn.commit()
                menu_tree.item(item, values=(new_name, new_price, new_img_path))
                if old_name in self.menu:
                    del self.menu[old_name]
                    del self.images[old_name]
                self.menu[new_name] = new_price
                self.images[new_name] = tk.PhotoImage(file=new_img_path)
                menu_name_entry.delete(0, 'end')
                menu_price_entry.delete(0, 'end')
                image_path.set("")
                self.menu_items = list(self.menu.items())
                self.show_menu_page()
            except ValueError:
                messagebox.showwarning("ข้อผิดพลาด")

        # ปุ่ม
        tk.Button(form_frame, text="เพิ่มเมนู", command=add_menu, bg="#8FC0CB", font=self.font16).grid(row=3, column=0, padx=5, pady=10)
        tk.Button(form_frame, text="ลบเมนู", command=delete_menu, bg="#CF8C8C", font=self.font16).grid(row=3, column=1, padx=5, pady=10)
        tk.Button(form_frame, text="แก้ไขเมนู", command=edit_menu, bg="#ffe38d", font=self.font16).grid(row=3, column=2, padx=5, pady=10)

        frame1 = tk.Label(setting_window,text=".",fg="#E9E7DC", bg="#E9E7DC",height=50,width=1520)
        frame1.pack(pady=0,side="bottom")
        frame1.pack_propagate(False)
        tk.Button(frame1, text="ย้อนกลับ", command=setting_window.destroy, bg="#ffb68d", font=self.font16,width=10).pack(side="left", pady=0,padx=10)
        tk.Button(frame1, text="กลับสู่หน้าหลัก", command=lambda: [setting_window.destroy(), self.root.deiconify()], bg="#ff8d8d", font=self.font16 ,height=1,width=10).pack(side="right", pady=0,padx=10)
    
    def view_orders(self):
        orders_window = tk.Toplevel(self.root)
        self.conn = sqlite3.connect(r"C:\Users\user\Desktop\project\coffee.db")
        orders_window.title("ดูคำสั่งซื้อ")
        orders_window.attributes('-fullscreen', True)
        orders_window.config(bg="#E9E7DC")

        tk.Label(orders_window, text="คำสั่งซื้อทั้งหมด", font=self.font16, bg="#E9E7DC").pack(pady=10)

        # ตัวเลือกการกรอง
        filter_frame = tk.Frame(orders_window, bg="#E9E7DC")
        filter_frame.pack(pady=10)

        # ตัวเลือกวัน
        tk.Label(filter_frame, text="วัน:", font=self.font16, bg="#E9E7DC").grid(row=0, column=0, padx=5)
        day_combo = ttk.Combobox(filter_frame, values=["All"] + [str(i) for i in range(1, 32)], state="readonly", font=("Arial", 14))
        day_combo.current(0)
        day_combo.grid(row=0, column=1, padx=5)

        # ตัวเลือกเดือน
        tk.Label(filter_frame, text="เดือน:", font=self.font16, bg="#E9E7DC").grid(row=0, column=2, padx=5)
        month_combo = ttk.Combobox(filter_frame, values=["All"] + [str(i) for i in range(1, 13)], state="readonly", font=("Arial", 14))
        month_combo.current(0)
        month_combo.grid(row=0, column=3, padx=5)

        # ตัวเลือกปี
        current_year = datetime.now().year
        years = ["All"] + [str(year) for year in range(current_year - 10, current_year + 1)]
        tk.Label(filter_frame, text="ปี:", font=self.font16, bg="#E9E7DC").grid(row=0, column=4, padx=5)
        year_combo = ttk.Combobox(filter_frame, values=years, state="readonly", font=("Arial", 14))
        year_combo.current(0)
        year_combo.grid(row=0, column=5, padx=5)

        # ปุ่มกรอง
        def apply_filter():
            selected_day = day_combo.get()
            selected_month = month_combo.get()
            selected_year = year_combo.get()

            query = "SELECT * FROM orders WHERE 1=1"
            params = []

            if selected_day != "All":
                query += " AND strftime('%d', วันที่) = ?"
                params.append(selected_day.zfill(2))
            if selected_month != "All":
                query += " AND strftime('%m', วันที่) = ?"
                params.append(selected_month.zfill(2))
            if selected_year != "All":
                query += " AND strftime('%Y', วันที่) = ?"
                params.append(selected_year)

            self.cursor.execute(query, params)
            orders = self.cursor.fetchall()

            # ล้างข้อมูลเดิมในตาราง
            for item in order_tree.get_children():
                order_tree.delete(item)

            # แสดงข้อมูลที่กรองแล้ว
            total_price = 0
            for order in orders:
                order_tree.insert('', 'end', values=(order[6], order[3], order[4]))
                total_price += order[4]

            total_label.config(text=f"ยอดรวมทั้งหมด: {total_price:,.2f} บาท")

        filter_button = tk.Button(filter_frame, text="ยืนยัน", command=apply_filter, bg="#A8D5BA", font=self.font16)
        filter_button.grid(row=0, column=6, padx=10)

        # แสดงคำสั่งซื้อ
        order_tree = ttk.Treeview(orders_window, columns=("วันที่", "รายการ", "ราคา"), show="headings", height=15)
        order_tree.pack(anchor="center", fill="both", padx=10, pady=10)

        # ขนาดคอลัมน์
        order_tree.column("วันที่", width=150, anchor="center") 
        order_tree.column("รายการ", width=300, anchor="center")
        order_tree.column("ราคา", width=150, anchor="center")

        order_tree.heading("วันที่", text="******** ปี-เดือน-วัน ********")
        order_tree.heading("รายการ", text="******** รายการ ********")
        order_tree.heading("ราคา", text="******** ราคา ********")

        # ดึงข้อมูลทั้งหมดจากฐานข้อมูล
        self.cursor.execute("SELECT * FROM orders")
        orders = self.cursor.fetchall()

        total_price = 0
        for order in orders:
            order_tree.insert('', 'end', values=(order[6], order[3], order[4]))
            total_price += order[4]

        scrollbar = ttk.Scrollbar(orders_window, orient="vertical", command=order_tree.yview)
        scrollbar.pack(side="right", fill="y")
        order_tree.configure(yscrollcommand=scrollbar.set)

        # ยอดรวมทั้งหมด
        total_label = tk.Label(orders_window, text=f"ยอดรวมทั้งหมด: {total_price:,.2f} บาท", font=self.font16, bg="#E9E7DC")
        total_label.pack(pady=10)
        
        # ปุ่ม
        tk.Button(orders_window, text="สรุปการขาย", command=self.fetch, bg="#909270", font=self.font16).pack(pady=10)
        tk.Button(orders_window, text="ปิด", command=orders_window.destroy, bg="#D595A0", font=self.font16,width=9).pack(pady=10)

        # ปิดการเชื่อมต่อฐานข้อมูลเมื่อปิดหน้าต่าง
        def on_close():
            self.conn.close()
            orders_window.destroy()

        orders_window.protocol("WM_DELETE_WINDOW", on_close)

    def fetch(self):
        or_window = tk.Toplevel(self.root)
        or_window.title("สรุปการขาย")
        self.conn = sqlite3.connect(r"C:\Users\user\Desktop\project\coffee.db")
        or_window.attributes('-fullscreen', True)
        or_window.config(bg="#E9E7DC")

        tk.Label(or_window, text="สรุปคำสั่งซื้อ", font=self.font16, bg="#E9E7DC").pack(pady=10)

        filter_frame = tk.Frame(or_window, bg="#E9E7DC")
        filter_frame.pack(pady=10)
        
        # ตัวเลือกวัน
        tk.Label(filter_frame, text="วัน:", font=self.font16, bg="#E9E7DC").grid(row=0, column=0, padx=5)
        day_combo = ttk.Combobox(filter_frame, values=["All"] + [str(i) for i in range(1, 32)], state="readonly", font=("Arial", 14))
        day_combo.current(0)
        day_combo.grid(row=0, column=1, padx=5)

        # ตัวเลือกเดือน
        tk.Label(filter_frame, text="เดือน:", font=self.font16, bg="#E9E7DC").grid(row=0, column=2, padx=5)
        month_combo = ttk.Combobox(filter_frame, values=["All"] + [str(i) for i in range(1, 13)], state="readonly", font=("Arial", 14))
        month_combo.current(0)
        month_combo.grid(row=0, column=3, padx=5)

        # ตัวเลือกปี
        current_year = datetime.now().year
        years = ["All"] + [str(year) for year in range(current_year - 10, current_year + 1)]
        tk.Label(filter_frame, text="ปี:", font=self.font16, bg="#E9E7DC").grid(row=0, column=4, padx=5)
        year_combo = ttk.Combobox(filter_frame, values=years, state="readonly", font=("Arial", 14))
        year_combo.current(0)
        year_combo.grid(row=0, column=5, padx=5)

        # ปุ่มกรอง
        def apply_filter():
            selected_day = day_combo.get()
            selected_month = month_combo.get()
            selected_year = year_combo.get()

            query = "SELECT * FROM orders WHERE 1=1"
            params = []

            if selected_day != "All":
                query += " AND strftime('%d', วันที่) = ?"
                params.append(selected_day.zfill(2))
            if selected_month != "All":
                query += " AND strftime('%m', วันที่) = ?"
                params.append(selected_month.zfill(2))
            if selected_year != "All":
                query += " AND strftime('%Y', วันที่) = ?"
                params.append(selected_year)

            self.cursor.execute(query, params)
            orders = self.cursor.fetchall()

            if not orders:
                tk.messagebox.showinfo("ไม่มีข้อมูล", "ไม่มีคำสั่งซื้อในระบบสำหรับวันที่เลือก")
            else:
                summarized_orders = {}
                for order in orders:
                    item_name = order[3].rsplit("x", 1)[0].strip()
                    quantity = self.get_quantity(order[3])
                    price = order[4]
                    if item_name in summarized_orders:
                        summarized_orders[item_name]['quantity'] += quantity
                        summarized_orders[item_name]['price'] += price
                    else:
                        summarized_orders[item_name] = {'quantity': quantity, 'price': price}

                self.populate_treeview(summarized_orders, or_tree)

            total_price = sum(order[4] for order in orders)
            total_label.config(text=f"ยอดรวมทั้งหมด: {total_price:,.2f} บาท")

        filter_button = tk.Button(filter_frame, text="ยืนยัน", command=apply_filter, bg="#A8D5BA", font=self.font16)
        filter_button.grid(row=0, column=6, padx=10)

        # ตารางแสดงคำสั่งซื้อ
        or_tree = ttk.Treeview(or_window, columns=("ลำดับที่", "รายการ", "จำนวนแก้ว", "ราคา"), show="headings", height=15)
        or_tree.pack(anchor="center", fill="both", padx=10, pady=10)
        or_tree.column("ลำดับที่", width=50, anchor="center")
        or_tree.column("รายการ", width=300, anchor="center")
        or_tree.column("จำนวนแก้ว", width=150, anchor="center")
        or_tree.column("ราคา", width=150, anchor="center")
        or_tree.heading("ลำดับที่", text="ลำดับที่")
        or_tree.heading("รายการ", text="รายการ")
        or_tree.heading("จำนวนแก้ว", text="จำนวนแก้ว")
        or_tree.heading("ราคา", text="ราคา")

        scrollbar = ttk.Scrollbar(or_window, orient="vertical", command=or_tree.yview)
        scrollbar.pack(side="right", fill="y")
        or_tree.configure(yscrollcommand=scrollbar.set)

        self.cursor.execute("SELECT * FROM orders")
        orders = self.cursor.fetchall()
        orders_sorted = sorted(
            orders, 
            key=lambda order: self.get_quantity(order[3]),  
            reverse=True
        )

        # ถ้ามันชื่อเดียวกันให้เพิ่มแก้ว
        summarized_orders = {}
        for order in orders_sorted:
            item_name = order[3].rsplit("x", 1)[0].strip()
            quantity = self.get_quantity(order[3])
            price = order[4]
            if item_name in summarized_orders:
                summarized_orders[item_name]['quantity'] += quantity
                summarized_orders[item_name]['price'] += price
            else:
                summarized_orders[item_name] = {'quantity': quantity, 'price': price}

        self.populate_treeview(summarized_orders, or_tree)

        total_price = sum(order[4] for order in orders)
        total_label = tk.Label(or_window, text=f"ยอดรวมทั้งหมด: {total_price:,.2f} บาท", font=self.font16, bg="#E9E7DC")
        total_label.pack(pady=10)

        tk.Button(or_window, text="กลับ", command=or_window.destroy, bg="#D595A0", font=self.font16, width=9).pack(pady=10)

        def on_close():
            self.conn.close()
            or_window.destroy()

        or_window.protocol("WM_DELETE_WINDOW", on_close)

    def get_quantity(self, order_string):
        try:
            return int(order_string.split("x")[-1].strip())
        except (IndexError, ValueError):
            return 0

    def populate_treeview(self, summarized_orders, or_tree):
        for item in or_tree.get_children():
            or_tree.delete(item)

        for idx, (item_name, details) in enumerate(summarized_orders.items()):
            formatted_price = "{:,.2f}".format(details['price'])
            or_tree.insert('', 'end', values=(idx + 1, item_name, details['quantity'], formatted_price))


if __name__ == "__main__":
    root = tk.Tk()
    app = CoffeeApp(root)
    root.protocol("WM_DELETE_WINDOW", app.closing)
    root.mainloop()
