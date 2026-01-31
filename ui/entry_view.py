import tkinter as tk
import webbrowser
import time
from ui.theme import BG_MAIN, BG_PANEL, BG_ENTRY, FG_TEXT, ACCENT


class EntryView:
    def __init__(self, app_root, parent, entry: dict, categories: list, on_save):
        self.app_root = app_root
        self.entry = entry
        self.categories = categories
        self.on_save = on_save

        self.window = tk.Toplevel(parent)
        self.window.title(entry.get("service", "Запись"))
        self.window.geometry("420x500")
        self.window.resizable(False, False)
        self.window.configure(bg=BG_MAIN)

        self.password_visible = False

        self.build_ui()

    def build_ui(self):
        pad = {"padx": 10, "pady": 5}

        # ---- Сервис ----
        tk.Label(
            self.window,
            text="Сервис",
            bg=BG_MAIN,
            fg=FG_TEXT
        ).pack(**pad)
        self.service_var = tk.StringVar(value=self.entry.get("service", ""))
        tk.Entry(
            self.window,
            textvariable=self.service_var,
            bg=BG_ENTRY,
            fg=FG_TEXT,
            insertbackground=FG_TEXT,
            relief="flat"
        ).pack(fill="x", **pad)

        # ---- Категория ----
        tk.Label(self.window, text="Категория").pack(**pad)

        self.category_var = tk.StringVar()

        category_names = [c["name"] for c in self.categories]
        self.category_menu = tk.OptionMenu(
            self.window,
            self.category_var,
            *category_names
        )
        self.category_menu.pack(fill="x", **pad)

        # текущая категория
        current_id = self.entry.get("category_id", "all")
        for c in self.categories:
            if c["id"] == current_id:
                self.category_var.set(c["name"])
                break
        else:
            self.category_var.set(category_names[0])

        # ---- URL ----
        tk.Label(self.window, text="URL").pack(**pad)
        self.url_var = tk.StringVar(value=self.entry.get("url", ""))
        tk.Entry(self.window, textvariable=self.url_var).pack(fill="x", **pad)

        tk.Button(
            self.window,
            text="🌐 Открыть сайт",
            command=self.open_site
        ).pack(**pad)

        # ---- Логин ----
        tk.Label(self.window, text="Логин").pack(**pad)
        self.login_var = tk.StringVar(value=self.entry.get("login", ""))
        tk.Entry(self.window, textvariable=self.login_var).pack(fill="x", **pad)

        # ---- Пароль ----
        tk.Label(self.window, text="Пароль").pack(**pad)

        pass_frame = tk.Frame(self.window, bg=BG_MAIN)
        pass_frame.pack(fill="x", **pad)

        self.password_var = tk.StringVar(value=self.entry.get("password", ""))
        self.password_entry = tk.Entry(
            pass_frame, textvariable=self.password_var, show="*"
        )
        self.password_entry.pack(side="left", fill="x", expand=True)

        tk.Button(
            pass_frame, text="👁️", width=3, command=self.toggle_password
        ).pack(side="left", padx=5)

        # ---- Заметка ----
        tk.Label(self.window, text="Заметка").pack(**pad)
        self.note_text = tk.Text(
            self.window,
            height=4,
            bg=BG_ENTRY,
            fg=FG_TEXT,
            insertbackground=FG_TEXT,
            relief="flat"
        )
        self.note_text.pack(fill="x", **pad)
        self.note_text.insert("1.0", self.entry.get("note", ""))

        # ---- Кнопки ----
        bottom = tk.Frame(self.window)
        bottom.pack(pady=10)

        tk.Button(bottom, text="Сохранить", command=self.save).pack(side="left", padx=5)
        tk.Button(bottom, text="Отмена", command=self.window.destroy).pack(side="left")

    def toggle_password(self):
        self.password_visible = not self.password_visible
        self.password_entry.config(show="" if self.password_visible else "*")

    def open_site(self):
        url = self.url_var.get().strip()
        if url:
            webbrowser.open(url)

    def save(self):
        self.entry["service"] = self.service_var.get().strip()
        self.entry["login"] = self.login_var.get().strip()
        self.entry["password"] = self.password_var.get()
        self.entry["url"] = self.url_var.get().strip()
        self.entry["note"] = self.note_text.get("1.0", "end").strip()

        # категория
        selected_name = self.category_var.get()
        for c in self.categories:
            if c["name"] == selected_name:
                self.entry["category_id"] = c["id"]
                break
        else:
            self.entry["category_id"] = "all"

        self.entry["updated_at"] = time.time()

        self.on_save()
        self.window.destroy()
