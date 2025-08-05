# ModernEntry.py - 修复版本
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
        self.cursor_id = None
        self._destroyed = False
        
        try:
            self.cursor_id = canvas.create_rectangle(
                x, y, x + width, y + height,
                fill=color, outline="", width=0)
        except tk.TclError:
            self._destroyed = True

    def move(self, x, y):
        if self._destroyed or not self.cursor_id:
            return
            
        was_visible = self.visible
        if self.blink_id:
            try:
                self.canvas.after_cancel(self.blink_id)
            except tk.TclError:
                pass
            self.blink_id = None
            
        self.x = x
        self.y = y
        
        try:
            self.canvas.coords(self.cursor_id, x, y, x + self.width, y + self.height)
            if was_visible:
                self.canvas.itemconfig(self.cursor_id, fill=self.color)
            self.start_blinking()
        except tk.TclError:
            self._destroyed = True

    def blink(self):
        if self._destroyed or not self.cursor_id:
            return
            
        self.visible = not self.visible
        fill = self.color if self.visible else ""
        
        try:
            self.canvas.itemconfig(self.cursor_id, fill=fill)
            self.blink_id = self.canvas.after(self.blink_speed, self.blink)
        except tk.TclError:
            self._destroyed = True

    def start_blinking(self):
        if self._destroyed or not self.cursor_id:
            return
            
        if self.blink_id:
            try:
                self.canvas.after_cancel(self.blink_id)
            except tk.TclError:
                pass
                
        self.visible = True
        try:
            self.canvas.itemconfig(self.cursor_id, fill=self.color)
            self.blink_id = self.canvas.after(self.blink_speed, self.blink)
        except tk.TclError:
            self._destroyed = True

    def stop_blinking(self):
        if self.blink_id:
            try:
                self.canvas.after_cancel(self.blink_id)
            except tk.TclError:
                pass
            self.blink_id = None
            
        self.visible = False
        if not self._destroyed and self.cursor_id:
            try:
                self.canvas.itemconfig(self.cursor_id, fill="")
            except tk.TclError:
                self._destroyed = True

    def set_height(self, height):
        if self._destroyed or not self.cursor_id:
            return
            
        self.height = height
        try:
            self.canvas.coords(self.cursor_id, self.x, self.y, self.x + self.width, self.y + height)
        except tk.TclError:
            self._destroyed = True

    def set_color(self, color):
        self.color = color
        if self.visible and not self._destroyed and self.cursor_id:
            try:
                self.canvas.itemconfig(self.cursor_id, fill=color)
            except tk.TclError:
                self._destroyed = True

    def destroy(self):
        self.stop_blinking()
        self._destroyed = True
        if self.cursor_id:
            try:
                self.canvas.delete(self.cursor_id)
            except tk.TclError:
                pass
            self.cursor_id = None
    
    def hide(self):
        if not self._destroyed and self.cursor_id:
            try:
                self.canvas.itemconfig(self.cursor_id, state='hidden')
            except tk.TclError:
                self._destroyed = True

    def show(self):
        if not self._destroyed and self.cursor_id:
            try:
                self.canvas.itemconfig(self.cursor_id, state='normal')
            except tk.TclError:
                self._destroyed = True

# ---------- ModernEntry ----------
class ModernEntry(tk.Canvas):
    _active_cursor = None
    _first_entry = None
    _tab_bound = False

    def __init__(self, master, width=240, height=36, radius=4,
                 bg_color="#2d2d2d", border_normal="#444444",
                 border_focus="#4ec9b0", text_color="#e0e0e0",
                 placeholder="", placeholder_color="#888888",
                 font_family="Segoe UI", font_size=12,
                 fixed_size=True, **kwargs):

        super().__init__(master, width=width, height=height,
                         highlightthickness=0, bd=0, bg=bg_color)
        
        # 基础配置
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
        self._text_left = 0
        self._max_text_width = None
        self._destroyed = False

        # 布局计算
        font_height = self._font.metrics("linespace")
        self.text_x = 12
        self.text_y = (height - font_height) // 2
        self.cursor_y_offset = max(0, (font_height - self._cursor_height) // 2)

        # 光标初始化 - 必须在_redraw_rect之前
        self.cursor = None
        
        # 创建文本和背景
        self.text_id = self.create_text(
            self.text_x, self.text_y,
            text=placeholder, anchor="nw",
            fill=placeholder_color, font=self._font)
        self._redraw_rect(width, height)
        
        # 事件绑定
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

        # 设置第一个Entry和全局Tab绑定
        if ModernEntry._first_entry is None:
            ModernEntry._first_entry = self
        self._bind_root_tab()
        self.tag_raise(self.text_id)
        
    def _bind_root_tab(self):
        """绑定全局Tab键处理 - 只绑定一次"""
        if ModernEntry._tab_bound:
            return
            
        root = self._root()
        if root is None:
            return
            
        ModernEntry._tab_bound = True

        def _global_tab(event):
            focus = event.widget.focus_get()
            # 如果焦点已经是 ModernEntry，让其自己处理
            if isinstance(focus, ModernEntry):
                return None
            # 否则把焦点给第一个存在的 ModernEntry
            if (ModernEntry._first_entry and 
                not ModernEntry._first_entry._destroyed and
                ModernEntry._first_entry.winfo_exists()):
                ModernEntry._first_entry.focus_set()
                return "break"
            return None

        try:
            root.bind_all("<Tab>", _global_tab, add="+")
        except tk.TclError:
            pass

    def _fix_index(self, idx):
        """修正索引值"""
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
        """插入文本"""
        if self._destroyed:
            return
        idx = self._fix_index(idx)
        self._text = self._text[:idx] + txt + self._text[idx:]
        self._cursor_pos = idx + len(txt)
        self._refresh_text_and_cursor()

    def delete(self, first, last=None):
        """删除文本"""
        if self._destroyed:
            return
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
        """设置文本内容"""
        if self._destroyed:
            return
            
        self._text = text
        self._cursor_pos = len(text)
        self._text_left = 0
        
        try:
            self.coords(self.text_id, self.text_x, self.text_y)

            # 显示文本或占位符
            if text:
                self.itemconfig(self.text_id, text=text, fill=self.text_color)
            else:
                self.itemconfig(self.text_id, text=self.placeholder, fill=self.placeholder_color)

            # 确保光标存在但隐藏
            self._ensure_cursor_exists()
            if self.cursor:
                self.cursor.hide()

            # 滚动归零
            self._scroll_to_cursor()
        except tk.TclError:
            self._destroyed = True

    def get(self):
        """获取文本内容"""
        return self._text

    def _ensure_cursor_exists(self):
        """确保光标存在"""
        if self.cursor is None and not self._destroyed:
            try:
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
            except tk.TclError:
                self._destroyed = True

    def _refresh_text_and_cursor(self):
        """刷新文本显示和光标位置"""
        if self._destroyed:
            return
            
        try:
            # 根据当前 _text 决定显示什么
            show_text = self._text if self._text else self.placeholder
            show_color = self.text_color if self._text else self.placeholder_color
            self.itemconfig(self.text_id, text=show_text, fill=show_color)
            
            self._update_cursor()
            self._scroll_to_cursor()
        except tk.TclError:
            self._destroyed = True

    def _on_click(self, event):
        """处理鼠标点击"""
        if self._destroyed:
            return
            
        self._ensure_cursor_exists()
        if not self.cursor:
            return
            
        # 将鼠标坐标转换为文本坐标
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
        self._scroll_to_cursor()
        self.focus_set()

    def _on_key_press(self, event):
        """处理按键事件"""
        if self._destroyed:
            return
            
        self._ensure_cursor_exists()
        if not self.cursor:
            return
            
        keysym = event.keysym

        if keysym == "BackSpace":
            if self._cursor_pos > 0:
                self._text = self._text[:self._cursor_pos-1] + self._text[self._cursor_pos:]
                self._cursor_pos -= 1 
        elif keysym == "Delete":
            if self._cursor_pos < len(self._text):
                self._text = self._text[:self._cursor_pos] + self._text[self._cursor_pos + 1:]
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

        self._cursor_pos = max(0, min(self._cursor_pos, len(self._text)))
        self._refresh_text_and_cursor()
        self._scroll_to_cursor()

    def _on_focus_in(self, event=None):
        """获得焦点时的处理"""
        if self._destroyed:
            return
            
        self._ensure_cursor_exists()
        
        # 处理之前的活动光标
        if ModernEntry._active_cursor and ModernEntry._active_cursor != self:
            if (ModernEntry._active_cursor.cursor and 
                not ModernEntry._active_cursor._destroyed):
                ModernEntry._active_cursor.cursor.stop_blinking()
                ModernEntry._active_cursor.cursor.hide()
        
        # 设置当前为活动光标
        ModernEntry._active_cursor = self
        
        try:
            self._redraw_rect(self.winfo_width(), self.winfo_height(), focus=True)
            if self.cursor:
                self.cursor.show()
                self.cursor.start_blinking()
        except tk.TclError:
            self._destroyed = True

    def _on_focus_out(self, event=None):
        """失去焦点时的处理"""
        if self._destroyed:
            return
            
        if ModernEntry._active_cursor == self:
            if self.cursor:
                self.cursor.stop_blinking()
                self.cursor.hide()
            ModernEntry._active_cursor = None
            
        try:
            self._redraw_rect(self.winfo_width(), self.winfo_height(), focus=False)
        except tk.TclError:
            self._destroyed = True

    def _on_tab(self, event):
        """Tab键处理 - 跳转到下一个可聚焦控件"""
        try:
            next_widget = event.widget.tk_focusNext()
            if next_widget:
                next_widget.focus()
            return "break"
        except tk.TclError:
            pass

    def _update_cursor(self):
        """更新光标位置"""
        if self._destroyed or not self.cursor:
            return
            
        substr = self._text[:self._cursor_pos]
        cursor_x = self.text_x + self._font.measure(substr) + self._text_left
        cursor_y = self.text_y + self.cursor_y_offset
        self.cursor.move(cursor_x, cursor_y)

    def _scroll_to_cursor(self):
        """滚动以保证光标可见"""
        if self._destroyed:
            return
            
        # 无文本时归零
        if not self._text:
            self._text_left = 0
            try:
                self.coords(self.text_id, self.text_x, self.text_y)
                self._update_cursor()
            except tk.TclError:
                self._destroyed = True
            return

        # 光标宽度
        cursor_w = 1 if not self.cursor else self.cursor.width

        # 光标左/右边界（相对于文本起始点）
        cursor_left = self._font.measure(self._text[:self._cursor_pos])
        cursor_right = cursor_left + cursor_w

        # 可视窗口宽度
        try:
            visible_w = self.winfo_width() - 2 * self.text_x
        except tk.TclError:
            self._destroyed = True
            return

        # 计算滚动偏移
        if cursor_left < -self._text_left:
            self._text_left = -cursor_left
        elif cursor_right > -self._text_left + visible_w:
            self._text_left = -(cursor_right - visible_w)

        # 应用滚动
        try:
            self.coords(self.text_id, self.text_x + self._text_left, self.text_y)
            self._update_cursor()
        except tk.TclError:
            self._destroyed = True

    def _on_resize(self, event):
        """处理尺寸变化"""
        if self._destroyed:
            return
            
        w, h = event.width, event.height
        
        try:
            self._redraw_rect(w, h, focus=(self.focus_get() == self))

            font_height = self._font.metrics("linespace")
            self.text_y = (h - font_height) // 2
            self.coords(self.text_id, self.text_x + self._text_left, self.text_y)

            if self.cursor is not None:
                cursor_h = max(14, font_height - 4)
                self.cursor.set_height(cursor_h)
                self._update_cursor()
                self._scroll_to_cursor()
        except tk.TclError:
            self._destroyed = True
        
    def _redraw_rect(self, w, h, focus=False):
        """重绘背景矩形"""
        if self._destroyed:
            return
            
        try:
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
            if self.cursor and self.cursor.cursor_id:
                self.tag_raise(self.cursor.cursor_id)
        except tk.TclError:
            self._destroyed = True

    def _rounded_rect_pts(self, x1, y1, x2, y2, r):
        """生成圆角矩形坐标点"""
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
    
    def destroy(self):
        """清理资源"""
        self._destroyed = True
        
        # 清理光标
        if self.cursor:
            self.cursor.destroy()
            self.cursor = None
            
        # 清理类变量引用
        if ModernEntry._active_cursor == self:
            ModernEntry._active_cursor = None
        if ModernEntry._first_entry == self:
            ModernEntry._first_entry = None
            
        try:
            super().destroy()
        except tk.TclError:
            pass
    
# ---------- DemoApp ----------
class DemoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Entry Demo - Fixed Version")
        self.root.geometry("420x380")
        self.root.configure(bg="#1e1e1e")

        container = tk.Frame(root, bg="#1e1e1e", padx=20, pady=20)
        container.pack(fill="both", expand=True)

        header_frame = tk.Frame(container, bg="#1e1e1e")
        header_frame.pack(fill="x", pady=(0, 15))

        tk.Label(
            header_frame, text="Modern Entry - Fixed", font=("Segoe UI", 16, "bold"),
            fg="#4ec9b0", bg="#1e1e1e").pack(side="left")
        tk.Label(
            header_frame, text="All bugs fixed!", font=("Segoe UI", 10),
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
        
        container.columnconfigure(0, weight=1)
        container.rowconfigure(2, weight=1)
        form_frame.columnconfigure(1, weight=1)

    def _create_labeled_entry(self, parent, label_text, placeholder, row):
        label = tk.Label(
            parent, text=label_text, font=("Segoe UI", 10),
            fg="#cccccc", bg="#1e1e1e", width=10, anchor="w")
        label.grid(row=row, column=0, pady=8, sticky="w")

        entry = ModernEntry(
            parent, width=260, height=36, placeholder=placeholder,
            font_family="Segoe UI", font_size=12, fixed_size=False)
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