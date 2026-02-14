import base64
import io
import os
import threading
from socket import socket, AF_INET, SOCK_STREAM
from customtkinter import *
from tkinter import filedialog
from PIL import Image
from datetime import datetime


class MainWindow(CTk):
    def __init__(self):
        super().__init__()

        self.geometry("700x600")
        self.title("Chat Client")

        self.username = "User"

#НАЛАШТУВАННЯ
        self.current_theme = "dark"
        self.show_time = False
        self.show_date = False
        self.msg_count = 0

        self.font_size = 14 

        set_appearance_mode("dark")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

#МЕНЮ 
        self.menu_frame = CTkFrame(self, width=0, corner_radius=0)
        self.menu_frame.grid(row=0, column=0, rowspan=2, sticky="nsw")
        self.menu_frame.grid_propagate(False)

        self.is_show_menu = False
        self.speed_animate_menu = -20

#ЛІЧИЛЬНИК 
        self.counter_label = CTkLabel(self, text="Повідомлень: 0")
        self.counter_label.place(x=50, y=8)

#ЧАТ 
        self.chat_field = CTkScrollableFrame(self, corner_radius=0)
        self.chat_field.grid(row=0, column=1, padx=10, pady=(40, 10), sticky="nsew")

#ВВІД 
        self.input_frame = CTkFrame(self)
        self.input_frame.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.message_entry = CTkEntry(self.input_frame, placeholder_text="Введіть повідомлення", height=40)
        self.message_entry.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.open_img_button = CTkButton(self.input_frame, text="📁", width=40, command=self.open_image)
        self.open_img_button.grid(row=0, column=1, padx=5)

        self.send_button = CTkButton(self.input_frame, text="▶️", width=40, command=self.send_message)
        self.send_button.grid(row=0, column=2)

#КНОПКА МЕНЮ 
        self.btn = CTkButton(self, text="☰", width=30, command=self.toggle_show_menu)
        self.btn.place(x=5, y=5)

        threading.Thread(target=self.safe_connect, daemon=True).start()

#ПІДКЛЮЧЕННЯ 

    def safe_connect(self):
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(("localhost", 8080))
            self.recv_message()
        except:
            self.add_message("Система: Офлайн режим")

#МЕНЮ 

    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.speed_animate_menu = -20
        else:
            self.is_show_menu = True
            self.speed_animate_menu = 20
            self.create_menu_content()
        self.show_menu()

    def create_menu_content(self):
        for child in self.menu_frame.winfo_children():
            child.destroy()

        CTkLabel(self.menu_frame, text="Налаштування").pack(pady=(40, 10))

        self.entry = CTkEntry(self.menu_frame, placeholder_text="Ваш нік")
        self.entry.pack(pady=10, padx=10)

        CTkButton(self.menu_frame, text="Зберегти нік", command=self.save_name).pack(pady=5)
        CTkButton(self.menu_frame, text="🌙 Темна тема", command=lambda: self.change_theme("dark")).pack(pady=5)
        CTkButton(self.menu_frame, text="☀️ Світла тема", command=lambda: self.change_theme("light")).pack(pady=5)
        CTkButton(self.menu_frame, text="⏰ Вкл/Викл час", command=self.toggle_time).pack(pady=5)
        CTkButton(self.menu_frame, text="📅 Вкл/Викл дату", command=self.toggle_date).pack(pady=5)
        CTkButton(self.menu_frame, text="🗑 Очистити чат", command=self.clear_chat).pack(pady=5)
        CTkButton(self.menu_frame, text="A+", width=40, command=self.increase_font).pack(pady=5)
        CTkButton(self.menu_frame, text="A-", width=40, command=self.decrease_font).pack(pady=5)
    def show_menu(self):
        curr_w = self.menu_frame.winfo_width()
        new_w = curr_w + self.speed_animate_menu
        if self.is_show_menu and new_w <= 220:
            self.menu_frame.configure(width=new_w)
            self.after(10, self.show_menu)
        elif not self.is_show_menu and new_w >= 0:
            self.menu_frame.configure(width=new_w)
            self.after(10, self.show_menu)

#НАЛАШТУВАННЯ 

    def change_theme(self, mode):
        self.current_theme = mode
        set_appearance_mode(mode)
        self.add_message(f"Система: Тема змінена на {mode}")

    def toggle_time(self):
        self.show_time = not self.show_time
        self.add_message("Система: Перемкнено показ часу")

    def toggle_date(self):
        self.show_date = not self.show_date
        self.add_message("Система: Перемкнено показ дати")

    def save_name(self):
        if self.entry.get():
            self.username = self.entry.get()
            self.add_message(f"Нік змінено на: {self.username}")

    def clear_chat(self):
        for widget in self.chat_field.winfo_children():
            widget.destroy()
        self.msg_count = 0
        self.counter_label.configure(text="Повідомлень: 0")
#ЗМІНА РОЗМІРУ ШРИФТУ 

    def increase_font(self):
        if self.font_size < 30:
            self.font_size += 2
            self.update_fonts()

    def decrease_font(self):
        if self.font_size > 8:
            self.font_size -= 2
            self.update_fonts()

    def update_fonts(self):
        for widget in self.chat_field.winfo_children():
            widget.configure(font=("Arial", self.font_size))

#ЧАТ 

    def add_message(self, message, img=None):
        now = datetime.now()
        time_text = ""
        if self.show_date:
            time_text += now.strftime("%d.%m.%Y ")
        if self.show_time:
            time_text += now.strftime("%H:%M")

        msg_frame = CTkFrame(self.chat_field)
        msg_frame.pack(pady=5, anchor="w", padx=5, fill="x")

        if img:
            lbl = CTkLabel(msg_frame,text=f"{message}\n{time_text}",image=img,compound="top",justify="left",font=("Arial", self.font_size))
        else:
            lbl = CTkLabel(msg_frame,text=f"{message}\n{time_text}",wraplength=500,justify="left",font=("Arial", self.font_size))

        lbl.pack(padx=10, pady=5)

#ЛІЧИЛЬНИК
        self.msg_count += 1
        self.counter_label.configure(text=f"Повідомлень: {self.msg_count}")

    def send_message(self):
        msg = self.message_entry.get()
        if msg:
            self.add_message(f"Ви: {msg}")
            try:
                self.sock.sendall(f"TEXT@{self.username}@{msg}\n".encode())
            except:
                pass
        self.message_entry.delete(0, END)

    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode(errors="ignore")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except:
                break

    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)
        if parts[0] == "TEXT" and len(parts) >= 3:
            self.add_message(f"{parts[1]}: {parts[2]}")
        elif parts[0] == "IMAGE" and len(parts) >= 4:
            img_data = base64.b64decode(parts[3])
            img = CTkImage(Image.open(io.BytesIO(img_data)), size=(200, 200))
            self.add_message(f"{parts[1]} надіслав фото:", img)
    def open_image(self):
        path = filedialog.askopenfilename()
        if path:
            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            try:
                self.sock.sendall(f"IMAGE@{self.username}@{os.path.basename(path)}@{b64}\n".encode())
            except:
                pass
            img = CTkImage(Image.open(path), size=(200, 200))
            self.add_message("Ви надіслали фото:", img)
if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()