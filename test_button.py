# test_button.py
import tkinter as tk
from tkinter import messagebox
from button import RoundedButton

class TestApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RoundedButton 测试")
        self.geometry("360x280")
        self.configure(bg="#1e1e1e")
        self.resizable(False, False)

        # 计数器
        self.counter = 0

        # 1. 基础按钮
        self.btn_hello = RoundedButton(
            self,
            text="点我 +1",
            command=self.on_hello,
            width=100,
            height=30,
            radius=6
        )
        self.btn_hello.pack(pady=15)

        # 2. 计数标签
        self.lbl_count = tk.Label(
            self,
            text="计数：0",
            font=("Consolas", 12),
            fg="#e0e0e0",
            bg="#1e1e1e"
        )
        self.lbl_count.pack()

        # 3. 颜色切换按钮
        self.btn_color = RoundedButton(
            self,
            text="换颜色",
            command=self.toggle_color,
            width=100,
            height=30,
            button_color="#2b5797",
            hover_color="#3e77c9",
            press_color="#1f3a6f"
        )
        self.btn_color.pack(pady=15)

        # 4. 动态文字按钮
        self.btn_dynamic = RoundedButton(
            self,
            text="动态文字",
            command=self.change_text,
            width=100,
            height=30,
            radius=8,
            font_size=10,
            font_weight="bold"
        )
        self.btn_dynamic.pack(pady=15)

        # 5. 退出按钮
        self.btn_exit = RoundedButton(
            self,
            text="退出",
            command=self.on_exit,
            width=60,
            height=25,
            button_color="#a1382e",
            hover_color="#c4453a",
            press_color="#7c281f"
        )
        self.btn_exit.pack(side="bottom", pady=10)

        # 6. 禁用/启用演示
        self.chk_state = tk.BooleanVar(value=True)

        tk.Checkbutton(
            self,
            text="启用按钮",
            variable=self.chk_state,
            command=lambda: self.btn_hello.configure(
                state="normal" if self.chk_state.get() else "disabled"
            ),
            bg="#1e1e1e",
            fg="#e0e0e0",
            selectcolor="#252525"
        ).pack(pady=5)

    # 回调函数
    def on_hello(self):
        self.counter += 1
        self.lbl_count.config(text=f"计数：{self.counter}")

    def toggle_color(self):
        """来回切换 hello 按钮的颜色"""
        if self.btn_hello.button_color == "#252525":
            # 切换到绿色
            self.btn_hello.configure(
                button_color="#4caf50",
                hover_color="#66bb6a",
                press_color="#388e3c",
                outline_color="#81c784"
            )
        else:
            # 切回深灰
            self.btn_hello.configure(
                button_color="#252525",
                hover_color="#353535",
                press_color="#1e1e1e",
                outline_color="#404040"
            )

    def change_text(self):
        """动态修改自己的文字"""
        texts = ["动态文字", "再点一下", "继续加油", "最后一次"]
        current = self.btn_dynamic.itemcget(2, "text")  # 第 2 个 item 是文字
        idx = texts.index(current)
        self.btn_dynamic.configure(text=texts[(idx + 1) % len(texts)])

    def on_exit(self):
        if messagebox.askokcancel("提示", "确定退出测试？"):
            self.destroy()

if __name__ == "__main__":
    TestApp().mainloop()