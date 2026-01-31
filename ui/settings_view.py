import tkinter as tk
from tkinter import messagebox

from core.vault import save_vault
from ui.theme import BG_MAIN, BG_ENTRY, FG_TEXT, ACCENT


class SettingsWindow:
    def __init__(self, parent, session):
        self.session = session

        self.window = tk.Toplevel(parent)
        self.window.title("Settings")
        self.window.geometry("350x360")
        self.window.resizable(False, False)
        self.window.configure(bg=BG_MAIN)

        self.build_ui()

    def build_ui(self):
        pad = {"padx": 12, "pady": 6}

        # ---- Заголовок ----
        tk.Label(
            self.window,
            text="Смена мастер-пароля",
            font=("Segoe UI", 12, "bold"),
            bg=BG_MAIN,
            fg=FG_TEXT
        ).pack(pady=15)

        # ---- Текущий пароль ----
        tk.Label(
            self.window,
            text="Текущий пароль",
            bg=BG_MAIN,
            fg=FG_TEXT
        ).pack(**pad)

        self.old_pass = tk.Entry(
            self.window,
            show="*",
            bg=BG_ENTRY,
            fg=FG_TEXT,
            insertbackground=FG_TEXT,
            relief="flat"
        )
        self.old_pass.pack(fill="x", **pad)

        # ---- Новый пароль ----
        tk.Label(
            self.window,
            text="Новый пароль",
            bg=BG_MAIN,
            fg=FG_TEXT
        ).pack(**pad)

        self.new_pass = tk.Entry(
            self.window,
            show="*",
            bg=BG_ENTRY,
            fg=FG_TEXT,
            insertbackground=FG_TEXT,
            relief="flat"
        )
        self.new_pass.pack(fill="x", **pad)

        # ---- Повтор ----
        tk.Label(
            self.window,
            text="Повторите новый пароль",
            bg=BG_MAIN,
            fg=FG_TEXT
        ).pack(**pad)

        self.new_pass_repeat = tk.Entry(
            self.window,
            show="*",
            bg=BG_ENTRY,
            fg=FG_TEXT,
            insertbackground=FG_TEXT,
            relief="flat"
        )
        self.new_pass_repeat.pack(fill="x", **pad)

        # ---- Кнопка ----
        tk.Button(
            self.window,
            text="Сохранить",
            command=self.change_password
        ).pack(pady=18)

    def change_password(self):
        old = self.old_pass.get()
        new = self.new_pass.get()
        repeat = self.new_pass_repeat.get()

        if old != self.session.master_password:
            messagebox.showerror("Ошибка", "Неверный текущий пароль")
            return

        if not new:
            messagebox.showerror("Ошибка", "Новый пароль пустой")
            return

        if new != repeat:
            messagebox.showerror("Ошибка", "Пароли не совпадают")
            return

        # 🔐 пересохраняем сейф с новым паролем
        save_vault(self.session.vault, new)

        # обновляем сессию
        self.session.master_password = new

        messagebox.showinfo("ZipPass", "Мастер-пароль изменён")
        self.window.destroy()
