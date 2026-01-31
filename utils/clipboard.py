def copy_to_clipboard(root, text: str):
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()