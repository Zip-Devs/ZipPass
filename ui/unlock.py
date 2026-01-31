import tkinter as tk
from tkinter import messagebox

from core.vault import load_vault
from ui.main import MainWindow
from core.session import Session


class UnlockWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("ZipPass")
        self.root.resizable(False, False)

        tk.Label(
            root,
            text="ZipPass 🔐",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=15)

        tk.Label(root, text="Введите мастер-пароль").pack()

        self.password_entry = tk.Entry(root, show="*", width=30)
        self.password_entry.pack(pady=8)
        self.password_entry.focus()

        tk.Button(
            root,
            text="Разблокировать",
            width=20,
            command=self.unlock
        ).pack(pady=10)

        self.password_entry.bind("<Return>", lambda _: self.unlock())

    def unlock(self):
        password = self.password_entry.get().strip()
        if not password:
            return

        try:
            vault = load_vault(password)


            session = Session(
                vault=vault,
                master_password=password
            )

            self.root.destroy()

            main = MainWindow(session)
            main.run()

        except Exception:
            messagebox.showerror("Ошибка", "Неверный мастер-пароль")


def run_unlock():
    root = tk.Tk()
    UnlockWindow(root)
    root.mainloop()
