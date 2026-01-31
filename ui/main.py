import tkinter as tk
from tkinter import ttk
import webbrowser
from tkinter import filedialog, messagebox

from ui.entry_view import EntryView
from ui.settings_view import SettingsWindow
from core.vault import save_vault

from utils.csv_tools import export_to_csv, import_from_csv
from utils.icons import load_icon


# 🎨 Цветовая схема
BG_MAIN   = "#1e1e1e"
BG_PANEL  = "#252526"
BG_ENTRY  = "#2d2d30"
FG_TEXT   = "#e6e6e6"
ACCENT    = "#3a96dd"


class MainWindow:
    def __init__(self, session):
        self.session = session
        self.vault = session.vault
        self.icons = {}

        self.root = tk.Tk()
        self.root.title("ZipPass")
        self.root.geometry("900x500")
        self.root.configure(bg=BG_MAIN)

        self.apply_dark_theme()

        self.cat_list = None
        self.tree = None
        self.search_entry = None
        self.search_var = tk.StringVar()

        self.build_ui()
        self.load_categories()
        self.load_entries()

        self.root.bind("<Control-f>", self.focus_search)
        self.root.bind("<Control-F>", self.focus_search)

    # ================= THEME =================

    def apply_dark_theme(self):
        style = ttk.Style(self.root)
        style.theme_use("default")

        style.configure(
            "Treeview",
            background=BG_ENTRY,
            fieldbackground=BG_ENTRY,
            foreground=FG_TEXT,
            rowheight=28
        )
        style.configure(
            "Treeview.Heading",
            background=BG_PANEL,
            foreground=FG_TEXT
        )
        style.map(
            "Treeview",
            background=[("selected", ACCENT)],
            foreground=[("selected", "#ffffff")]
        )

        style.configure(
            "TButton",
            background=BG_PANEL,
            foreground=FG_TEXT,
            padding=6
        )

    # ================= CSV =================

    def export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if not path:
            return
        export_to_csv(self.vault["entries"], path)
        messagebox.showinfo("ZipPass", "Экспорт завершён")

    def import_csv(self):
        path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")]
        )
        if not path:
            return

        new_entries = import_from_csv(path)
        existing_ids = {e["id"] for e in self.vault["entries"]}

        added = 0
        for e in new_entries:
            if e["id"] not in existing_ids:
                self.vault["entries"].append(e)
                added += 1

        save_vault(self.vault, self.session.master_password)
        self.load_entries()

        messagebox.showinfo("ZipPass", f"Импортировано записей: {added}")

    # ================= UI =================

    def build_ui(self):
        # ---- Верх ----
        top = tk.Frame(self.root, bg=BG_MAIN)
        top.pack(fill="x", padx=10, pady=5)

        tk.Label(
            top, text="ZipPass",
            font=("Segoe UI", 14, "bold"),
            bg=BG_MAIN, fg=FG_TEXT
        ).pack(side="left")

        tk.Button(top, text="⚙️ Settings", command=self.open_settings)\
            .pack(side="right", padx=5)
        tk.Button(top, text="🔒 Заблокировать", command=self.lock)\
            .pack(side="right")

        # ---- Тело ----
        body = tk.Frame(self.root, bg=BG_MAIN)
        body.pack(fill="both", expand=True, padx=10, pady=5)

        # ---- Категории ----
        left = tk.Frame(body, width=180, bg=BG_PANEL)
        left.pack(side="left", fill="y")

        tk.Label(
            left, text="Категории",
            font=("Segoe UI", 10, "bold"),
            bg=BG_PANEL, fg=FG_TEXT
        ).pack(pady=5)

        self.cat_list = tk.Listbox(
            left,
            bg=BG_ENTRY,
            fg=FG_TEXT,
            selectbackground=ACCENT,
            highlightthickness=0,
            relief="flat"
        )
        self.cat_list.pack(fill="y", expand=True, padx=5)
        self.cat_list.bind("<<ListboxSelect>>", self.on_category_select)

        # ---- Центр ----
        center = tk.Frame(body, bg=BG_MAIN)
        center.pack(side="left", fill="both", expand=True, padx=(10, 0))

        # ---- Поиск ----
        search_frame = tk.Frame(center, bg=BG_MAIN)
        search_frame.pack(fill="x", pady=(0, 5))

        tk.Label(search_frame, text="🔍", bg=BG_MAIN, fg=FG_TEXT)\
            .pack(side="left")

        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            bg=BG_ENTRY,
            fg=FG_TEXT,
            insertbackground=FG_TEXT,
            relief="flat"
        )
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", lambda _e: self.load_entries())

        # ---- Таблица ----
        self.tree = ttk.Treeview(
            center,
            columns=("login", "url"),
            show="tree headings"
        )
        self.tree.heading("#0", text="")
        self.tree.column("#0", width=36, stretch=False)

        self.tree.heading("login", text="Логин")
        self.tree.heading("url", text="URL")
        self.tree.column("login", width=220)
        self.tree.column("url", width=360)

        self.tree.pack(fill="both", expand=True, side="left")
        self.tree.bind("<Double-1>", self.open_entry)

        scrollbar = ttk.Scrollbar(center, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # ---- Низ ----
        bottom = tk.Frame(self.root, bg=BG_MAIN)
        bottom.pack(fill="x", padx=10, pady=5)

        tk.Button(bottom, text="🌐 Открыть сайт", command=self.open_site)\
            .pack(side="left")
        tk.Button(bottom, text="📤 Экспорт CSV", command=self.export_csv)\
            .pack(side="right", padx=5)
        tk.Button(bottom, text="📥 Импорт CSV", command=self.import_csv)\
            .pack(side="right")

    # ================= Данные =================

    def load_categories(self):
        self.cat_list.delete(0, tk.END)
        for cat in self.vault.get("categories", []):
            self.cat_list.insert(tk.END, cat["name"])
        if self.cat_list.size() > 0:
            self.cat_list.select_set(0)

    def get_selected_category_id(self):
        sel = self.cat_list.curselection()
        if not sel:
            return "all"
        name = self.cat_list.get(sel[0])
        for cat in self.vault["categories"]:
            if cat["name"] == name:
                return cat["id"]
        return "all"

    def on_category_select(self, event=None):
        self.load_entries()

    def load_entries(self):
        self.tree.delete(*self.tree.get_children())

        cat_id = self.get_selected_category_id()
        query = self.search_var.get().lower().strip()

        for entry in self.vault.get("entries", []):
            if cat_id != "all" and entry.get("category_id", "all") != cat_id:
                continue

            if query:
                haystack = " ".join([
                    entry.get("service", ""),
                    entry.get("login", ""),
                    entry.get("url", ""),
                    entry.get("note", ""),
                ]).lower()
                if query not in haystack:
                    continue

            icon = None
            url = entry.get("url", "")
            if url:
                if url not in self.icons:
                    img = load_icon(url)
                    if img:
                        self.icons[url] = img
                icon = self.icons.get(url)

            self.tree.insert(
                "",
                "end",
                iid=entry["id"],
                text=" ",   # 👈 отступ от иконки
                image=icon,
                values=(entry.get("login", ""), entry.get("url", ""))
            )

    # ================= Разное =================

    def get_selected_entry(self):
        selected = self.tree.focus()
        for entry in self.vault["entries"]:
            if entry["id"] == selected:
                return entry
        return None

    def open_entry(self, event=None):
        entry = self.get_selected_entry()
        if not entry:
            return

        def on_save():
            save_vault(self.vault, self.session.master_password)
            self.load_entries()

        EntryView(
            app_root=self.root,
            parent=self.root,
            entry=entry,
            categories=self.vault["categories"],
            on_save=on_save
        )

    def open_site(self):
        entry = self.get_selected_entry()
        if entry and entry.get("url"):
            webbrowser.open(entry["url"])

    def focus_search(self, event=None):
        if self.search_entry:
            self.search_entry.focus_set()
            self.search_entry.select_range(0, tk.END)

    def open_settings(self):
        SettingsWindow(self.root, self.session)

    def lock(self):
        self.root.destroy()

    def run(self):
        self.root.mainloop()
