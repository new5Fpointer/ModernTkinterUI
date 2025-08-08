import tkinter as tk
from ModernEntry import ModernEntry

root = tk.Tk()
entry = ModernEntry(root, placeholder="请输入内容…")
entry.pack(padx=20, pady=20)
root.mainloop()