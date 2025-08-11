# ModernEntry_fixed.py
import tkinter as tk
import tkinter.font as tkfont
import math

# ---------- PureCursor ----------
class PureCursor:
    def __init__(self, canvas, x=0, y=0, height=14, width=1,
                 color="#ffffff", blink_speed=450):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.color = color
        self.blink_speed = blink_speed
        self.visible = True
        self.blink_id = None
        self.cursor_id = canvas.create_rectangle(
            x, y, x + width, y + height,
            fill=color, outline="", width=0)

    def move(self, x, y):
        was_visible = self.visible
        if self.blink_id:
            self.canvas.after_cancel(self.blink_id)
            self.blink_id = None
        self.x = x
        self.y = y
        self.canvas.coords(self.cursor_id, x, y, x + self.width, y + self.height)
        if was_visible:
            self.canvas.itemconfig(self.cursor_id, fill=self.color)
        self.start_blinking()

    def blink(self):
        self.visible = not self.visible
        fill = self.color if self.visible else ""
        self.canvas.itemconfig(self.cursor_id, fill=fill)
        self.blink_id = self.canvas.after(self.blink_speed, self.blink)

    def start_blinking(self):
        if self.blink_id:
            self.canvas.after_cancel(self.blink_id)
        self.visible = True
        self.canvas.itemconfig(self.cursor_id, fill=self.color)
        self.blink_id = self.canvas.after(self.blink_speed, self.blink)

    def stop_blinking(self):
        if self.blink_id:
            self.canvas.after_cancel(self.blink_id)
            self.blink_id = None
        self.visible = False
        self.canvas.itemconfig(self.cursor_id, fill="")

    def set_height(self, height):
        self.height = height
        self.canvas.coords(self.cursor_id, self.x, self.y, self.x + self.width, self.y + height)

    def set_color(self, color):
        self.color = color
        if self.visible:
            self.canvas.itemconfig(self.cursor_id, fill=color)

    def destroy(self):
        self.stop_blinking()
        try:
            self.canvas.delete(self.cursor_id)
        except tk.TclError:
            pass
    
    def hide(self):
        self.canvas.itemconfig(self.cursor_id, state='hidden')

    def show(self):
        self.canvas.itemconfig(self.cursor_id, state='normal')

# ---------- ModernEntry ----------
class ModernEntry(tk.Canvas):
    _active_cursor = None
    _first_entry = None

    def __init__(self, master, width=240, height=36, radius=4,
                 bg_color="#2d2d2d", border_normal="#444444",
                 border_focus="#4ec9b0", text_color="#e0e0e0",
                 placeholder="", placeholder_color="#888888",
                 font_family="Segoe UI", font_size=12,
                 fixed_size=True, **kwargs):

        super().__init__(master, width=width, height=height,
                         highlightthickness=0, bd=0, bg=bg_color)
        self.bg_color = bg_color
        self.border_normal = border_normal
        self.border_focus = border_focus
        self.text_color = text_color
        self.placeholder = placeholder
        self.placeholder_color = placeholder_color
        self._cursor_pos = 0
        self._text = ""
        self._font = tkfont.Font(family=font_family, size=font_size)
        self._cursor_height = 18
        self._radius = radius
        self._text_left = 0           # 当前文本在画布中的 x 偏移（负值表示向左滚）
        self._max_text_width = None   # 缓存文本最大可显示宽度

        

        font_height = self._font.metrics("linespace")
        self.text_x = 12
        self.text_y = (height - font_height) // 2
        self.cursor_y_offset = max(0, (font_height - self._cursor_height) // 2)

        self.text_id = self.create_text(
            self.text_x, self.text_y,
            text=placeholder, anchor="nw",
            fill=placeholder_color, font=self._font)
        self._redraw_rect(width, height)  

        self.cursor = None
        self.bind("<Button-1>", self._on_click)
        self.bind("<Key>", self._on_key_press)
        self.bind("<BackSpace>", self._on_key_press)
        self.bind("<Delete>", self._on_key_press)
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
        self.bind("<Tab>", self._on_tab)
        if fixed_size:
            self.bind("<Configure>", lambda e: "break")
        else:
            self.bind("<Configure>", self._on_resize)

        if ModernEntry._first_entry is None:
            ModernEntry._first_entry = self
        self._bind_root_tab()
        self.tag_raise(self.text_id)
        
    def _bind_root_tab(self):
        root = self._root()
        if getattr(root, "_modern_tab_bound", None):
            return
        root._modern_tab_bound = True

        def _global_tab(event):
            focus = event.widget.focus_get()
            # 如果焦点已经是 ModernEntry，让系统自己处理
            if isinstance(focus, ModernEntry):
                return None
            # 否则把焦点给第一个 ModernEntry
            if ModernEntry._first_entry and ModernEntry._first_entry.winfo_exists():
                ModernEntry._first_entry.focus_set()
                return "break"
            return None

        root.bind_all("<Tab>", _global_tab, add="+")

    def _fix_index(self, idx):
        if idx in (tk.END, "end"):
            return len(self._text)
        try:
            idx = int(idx)
        except ValueError:
            idx = 0
        if idx < 0:
            idx = max(0, len(self._text) + idx)
        return max(0, min(idx, len(self._text)))

    def insert(self, idx, txt):
        idx = self._fix_index(idx)
        self._text = self._text[:idx] + txt + self._text[idx:]
        self._cursor_pos = idx + len(txt)
        self._refresh_text_and_cursor()

    def delete(self, first, last=None):
        first = self._fix_index(first)
        if last is None:
            last = first + 1
        else:
            last = self._fix_index(last)
        if first > last:
            first, last = last, first
        self._text = self._text[:first] + self._text[last:]
        self._cursor_pos = first
        self._refresh_text_and_cursor()

    def set(self, text):
        self._text = text
        self._cursor_pos = len(text)
        self._text_left = 0
        self.coords(self.text_id, self.text_x, self.text_y)

        # 1. 立即显示占位符或文本
        if text:
            self.itemconfig(self.text_id, text=text, fill=self.text_color)
        else:
            self.itemconfig(self.text_id, text=self.placeholder, fill=self.placeholder_color)

        # 2. 光标：不存在就创建并隐藏
        if self.cursor is None:
            self._create_cursor()
            self.cursor.hide()

        # 3. 滚动归零
        self._scroll_to_cursor()

    def get(self):
        return self._text

    def _refresh_text_and_cursor(self):
    # 根据当前 _text 实时决定显示什么
        show_text   = self._text if self._text else self.placeholder
        show_color  = self.text_color if self._text else self.placeholder_color
        self.itemconfig(self.text_id, text=show_text, fill=show_color)
        self._update_cursor()
        self._scroll_to_cursor()

    def _on_click(self, event):
        if self.cursor is None:
            self._create_cursor()
        # 把鼠标坐标转换成“文本坐标”
        click_x_text = event.x - (self.text_x + self._text_left)

        # 二分查找最近的光标插入点
        self._cursor_pos = 0
        min_distance = float('inf')
        for i in range(len(self._text) + 1):
            substr_width = self._font.measure(self._text[:i])
            distance = abs(click_x_text - substr_width)
            if distance < min_distance:
                min_distance = distance
                self._cursor_pos = i
        self._cursor_pos = max(0, min(self._cursor_pos, len(self._text)))

        self._update_cursor()
        self._scroll_to_cursor()   # 让光标可见
        self.focus_set()

    def _on_key_press(self, event):
        if self.cursor is None:
            self._create_cursor()
        keysym = event.keysym

        def _keep_cursor_fixed():
            """保持光标在窗口中的像素位置不变"""
            old_cursor_x = self.text_x + self._font.measure(self._text[:self._cursor_pos]) + self._text_left
            new_cursor_x = self.text_x + self._font.measure(self._text[:self._cursor_pos]) + self._text_left
            delta = new_cursor_x - old_cursor_x
            self._text_left -= delta

            max_left = 0
            min_left = min(0, self.winfo_width() - 2 * self.text_x - self._font.measure(self._text))
            self._text_left = max(min_left, min(max_left, self._text_left))

        if keysym == "BackSpace":
            if self._cursor_pos > 0:
                self._text = self._text[:self._cursor_pos-1] + self._text[self._cursor_pos:]
                self._cursor_pos -= 1
                _keep_cursor_fixed()

        elif keysym == "Delete":
            if self._cursor_pos < len(self._text):
                self._text = self._text[:self._cursor_pos] + self._text[self._cursor_pos + 1:]
                _keep_cursor_fixed()

        elif keysym == "Left":
            self._cursor_pos = max(0, self._cursor_pos - 1)
        elif keysym == "Right":
            self._cursor_pos = min(len(self._text), self._cursor_pos + 1)
        elif keysym == "Home":
            self._cursor_pos = 0
        elif keysym == "End":
            self._cursor_pos = len(self._text)
        elif event.char and event.char.isprintable():
            self._text = self._text[:self._cursor_pos] + event.char + self._text[self._cursor_pos:]
            self._cursor_pos += 1
        else:
            return

        self._refresh_text_and_cursor()
        self._scroll_to_cursor()

    def _on_focus_in(self, event=None):
        if self.cursor is None:
            self._create_cursor()
        if ModernEntry._active_cursor:
            self.cursor.show() 
            ModernEntry._active_cursor.cursor.stop_blinking()
        ModernEntry._active_cursor = self
        self._redraw_rect(self.winfo_width(), self.winfo_height(), focus=True)
        if self.cursor:
            self.cursor.start_blinking()
        if self.cursor is None:
            self._create_cursor()
        self.cursor.show()
        self.cursor.start_blinking()

    def _on_focus_out(self, event=None):
        if ModernEntry._active_cursor == self:
            if self.cursor:
                self.cursor.stop_blinking()
                self.cursor.hide()
            ModernEntry._active_cursor = None

        # ✅ 新增：失去焦点时重置光标位置到开头
        self._cursor_pos = 0
        self._text_left = 0
        self.coords(self.text_id, self.text_x, self.text_y)
        self._update_cursor()

        self._redraw_rect(self.winfo_width(), self.winfo_height(), focus=False)

    def _on_tab(self, event):
        """event.widget.tk_focusNext().focus()
        return "break"""
        pass

    def _create_cursor(self):
        if self.cursor is None:
            self.cursor = PureCursor(
                self,
                x=self.text_x,
                y=self.text_y + self.cursor_y_offset,
                height=self._cursor_height,
                width=1,
                color="#6bd8c9",
                blink_speed=450
            )
            self.cursor.stop_blinking()
            self.cursor.hide() 

    def _update_cursor(self):
        substr = self._text[:self._cursor_pos]
        cursor_x = self.text_x + self._font.measure(substr) + self._text_left
        cursor_y = self.text_y + self.cursor_y_offset
        if self.cursor:
            self.cursor.move(cursor_x, cursor_y)

    def _scroll_to_cursor(self):
        """保证光标始终可见，且精确落在两字符之间"""
        # 无文本时归零
        if not self._text:
            self._text_left = 0
            self.coords(self.text_id, self.text_x, self.text_y)
            self._update_cursor()
            return

        # 光标宽度（像素）
        cursor_w = self.cursor.width

        # 光标左/右边界（相对于文本起始点）
        cursor_left = self._font.measure(self._text[:self._cursor_pos])
        cursor_right = cursor_left + cursor_w

        # 可视窗口
        visible_w = self.winfo_width() - 2 * self.text_x

        # 需要向左滚
        if cursor_left < -self._text_left:
            self._text_left = -cursor_left
        # 需要向右滚
        elif cursor_right > -self._text_left + visible_w:
            self._text_left = -(cursor_right - visible_w)

        # 应用
        self.coords(self.text_id, self.text_x + self._text_left, self.text_y)
        self._update_cursor()

    def _on_resize(self, event):
        w, h = event.width, event.height
        self._redraw_rect(w, h, focus=(self.focus_get() == self))

        font_height = self._font.metrics("linespace")
        self.text_y = (h - font_height) // 2

        # 1. 重新计算最大可显示宽度
        visible_w = w - 2 * self.text_x
        text_width = self._font.measure(self._text)

        # 2. 重新计算 _text_left，使光标仍可见且文本尽量靠左
        if self._text:
            cursor_x_in_text = self._font.measure(self._text[:self._cursor_pos])
            # 让光标位于可视区域
            self._text_left = max(-cursor_x_in_text,
                                min(0, visible_w - text_width))
        else:
            self._text_left = 0

        # 3. 更新文本和光标位置
        self.coords(self.text_id, self.text_x + self._text_left, self.text_y)

        if self.cursor is not None:
            cursor_h = max(14, font_height - 4)
            self.cursor.set_height(cursor_h)
            self._update_cursor()
        
    # -------------------------------------------------
    #  统一画圆角矩形（背景 + 边框），并保证不越界
    # -------------------------------------------------
    def _redraw_rect(self, w, h, focus=False):
        if hasattr(self, '_rect_bg'):
            self.delete(self._rect_bg)
        if hasattr(self, '_rect_outline'):
            self.delete(self._rect_outline)

        r = min(h // 2, self._radius)
        x1, y1, x2, y2 = 0, 0, w - 1, h - 1
        pts = self._rounded_rect_pts(x1, y1, x2, y2, r)

        self._rect_bg = self.create_polygon(
            pts, fill=self.bg_color, outline="", smooth=True)
        self._rect_outline = self.create_polygon(
            pts, fill="", outline=self.border_focus if focus else self.border_normal,
            smooth=True, width=1)

        self.tag_raise(self.text_id)
        if getattr(self, 'cursor', None):  # ✅ 安全判断
            self.tag_raise(self.cursor.cursor_id)

    # -------------------------------------------------
    #  圆角矩形坐标（顺时针，12 个点）
    # -------------------------------------------------
    def _rounded_rect_pts(self, x1, y1, x2, y2, r):
        return [
            x1+r, y1,              # 起点
            x2-r, y1,
            x2,   y1,
            x2,   y1+r,
            x2,   y2-r,
            x2,   y2,
            x2-r, y2,
            x1+r, y2,
            x1,   y2,
            x1,   y2-r,
            x1,   y1+r,
            x1,   y1
        ]
    
# ---------- DemoApp ----------
class DemoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Entry Demo")
        self.root.geometry("420x380")
        self.root.configure(bg="#1e1e1e")

        container = tk.Frame(root, bg="#1e1e1e", padx=20, pady=20)
        container.pack(fill="both", expand=True)

        header_frame = tk.Frame(container, bg="#1e1e1e")
        header_frame.pack(fill="x", pady=(0, 15))

        tk.Label(
            header_frame, text="Modern Entry", font=("Segoe UI", 16, "bold"),
            fg="#4ec9b0", bg="#1e1e1e").pack(side="left")
        tk.Label(
            header_frame, text="Smooth cursor animation", font=("Segoe UI", 10),
            fg="#888888", bg="#1e1e1e").pack(side="left", padx=(10, 0))

        form_frame = tk.Frame(container, bg="#1e1e1e")
        form_frame.pack(fill="both", expand=True)

        self._create_labeled_entry(form_frame, "Username:", "Enter your username", 0)
        self._create_labeled_entry(form_frame, "Password:", "Enter your password", 1)
        self._create_labeled_entry(form_frame, "Email:", "your.email@example.com", 2)

        button_frame = tk.Frame(container, bg="#1e1e1e")
        button_frame.pack(fill="x", pady=(15, 0))

        submit_btn = tk.Button(
            button_frame, text="Submit", font=("Segoe UI", 10, "bold"),
            bg="#4ec9b0", fg="#1e1e1e", activebackground="#3db09e",
            activeforeground="#ffffff", relief="flat", padx=20, pady=6,
            command=self.submit_form)
        submit_btn.pack(side="right", padx=(10, 0))

        clear_btn = tk.Button(
            button_frame, text="Clear All", font=("Segoe UI", 10),
            bg="#444444", fg="#cccccc", activebackground="#555555",
            activeforeground="#ffffff", relief="flat", padx=20, pady=6,
            command=self.clear_form)
        clear_btn.pack(side="right")
        container.columnconfigure(0, weight=1)   # 如果有多列
        container.rowconfigure(2, weight=1)      # form_frame 所在行
        form_frame.columnconfigure(1, weight=1)

    def _create_labeled_entry(self, parent, label_text, placeholder, row):
        label = tk.Label(
            parent, text=label_text, font=("Segoe UI", 10),
            fg="#cccccc", bg="#1e1e1e", width=10, anchor="w")
        label.grid(row=row, column=0, pady=8, sticky="w")

        entry = ModernEntry(
            parent, width=260, height=36, placeholder=placeholder,
            font_family="Segoe UI", font_size=12,fixed_size=False)
        entry.grid(row=row, column=1, padx=(0, 10), pady=8, sticky="nsew")
        setattr(self, f"entry_{row}", entry)
        parent.columnconfigure(1, weight=1)

    def submit_form(self):
        username = self.entry_0.get()
        password = self.entry_1.get()
        email = self.entry_2.get()
        print("\n--- Form Submission ---")
        print(f"Username: {username}")
        print(f"Password: {password}")
        print(f"Email: {email}")
        print("----------------------\n")
        success = tk.Label(
            self.root, text="✓ Form submitted successfully!",
            font=("Segoe UI", 10), fg="#4ec9b0", bg="#1e1e1e")
        success.place(relx=0.5, rely=0.92, anchor="center")
        self.root.after(2000, success.destroy)

    def clear_form(self):
        self.entry_0.set("")
        self.entry_1.set("")
        self.entry_2.set("")
        self.root.focus()

if __name__ == "__main__":
    root = tk.Tk()
    DemoApp(root)
    root.mainloop()