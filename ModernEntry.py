import tkinter as tk
import tkinter.font as tkfont
import math

class PureCursor:
    """自定义光标控件，实现平滑移动和闪烁效果"""
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
        
        # 创建光标主体
        self.cursor_id = canvas.create_rectangle(
            x, y, x + width, y + height,
            fill=color, outline="", width=0
        )
    
    def move(self, x, y):
        """平滑移动光标到新位置"""
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
        if self.visible:
            self.canvas.itemconfig(self.cursor_id, fill=self.color)
        else:
            self.canvas.itemconfig(self.cursor_id, fill="")
        self.blink_id = self.canvas.after(self.blink_speed, self.blink)
    
    def start_blinking(self):
        if self.blink_id is not None:
            self.canvas.after_cancel(self.blink_id)
        self.visible = True
        self.canvas.itemconfig(self.cursor_id, fill=self.color)
        self.blink_id = self.canvas.after(self.blink_speed, self.blink)
    
    def stop_blinking(self):
        if self.blink_id is not None:
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
        self.canvas.delete(self.cursor_id)


class ModernEntry(tk.Canvas):
    """现代风格输入框组件"""
    _active_cursor = None

    def __init__(self, master, width=240, height=36, radius=6,
                 bg_color="#2d2d2d", border_normal="#444444",
                 border_focus="#4ec9b0", text_color="#e0e0e0",
                 placeholder="", placeholder_color="#888888",
                 font_family="Segoe UI", font_size=12, **kwargs):
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
        # 修复了rect_id的绘制范围
        self.rect_id = self._draw_rounded_rect(
            0, 0, width, height,
            fill=bg_color,
            outline=border_normal,
            radius=radius
        )

        font_height = self._font.metrics("linespace")
        self.text_x = 12
        self.text_y = (height - font_height) // 2
        self.cursor_y_offset = max(0, (font_height - self._cursor_height) // 2)
            
        self.text_id = self.create_text(
            self.text_x, self.text_y,
            text=self.placeholder,
            anchor="nw",
            fill=self.placeholder_color,
            font=self._font
        )
        
        self.cursor = None
        self.bind("<Button-1>", self._on_click)
        self.bind("<Key>", self._on_key_press)
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
        self.bind("<Tab>", self._on_tab)
        self._parent = master
        self._parent.bind("<Configure>", self._on_resize, add="+")

    def _on_tab(self, event):
        event.widget.tk_focusNext().focus()
        return "break"

    def _on_focus_in(self, event=None):
        if self.cursor is None:
            self._create_cursor()
        if ModernEntry._active_cursor:
            ModernEntry._active_cursor.cursor.stop_blinking()
        ModernEntry._active_cursor = self
        self.itemconfig(self.rect_id, outline=self.border_focus)
        if self._text == "" and self.itemcget(self.text_id, "text") == self.placeholder:
            self.itemconfig(self.text_id, text="", fill=self.text_color)
        if self.cursor:
            self.cursor.start_blinking()
    
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
    
    def _on_focus_out(self, event=None):
        if ModernEntry._active_cursor == self:
            if self.cursor:
                self.cursor.stop_blinking()
            ModernEntry._active_cursor = None
        self.itemconfig(self.rect_id, outline=self.border_normal)
        if self._text == "":
            self.itemconfig(self.text_id, text=self.placeholder, fill=self.placeholder_color)

    def _on_click(self, event):
        if self.cursor is None:
            self._create_cursor()
        click_x = event.x
        text_width = self._font.measure(self._text)
        if click_x > self.text_x + text_width:
            self._cursor_pos = len(self._text)
        else:
            self._cursor_pos = 0
            min_distance = float('inf')
            for i in range(len(self._text) + 1):
                substr = self._text[:i]
                substr_width = self._font.measure(substr)
                cursor_x = self.text_x + substr_width
                distance = abs(click_x - cursor_x)
                if distance < min_distance:
                    min_distance = distance
                    self._cursor_pos = i
        self._update_cursor()
        self.focus_set()

    def _on_key_press(self, event):
        if self.cursor is None:
            self._create_cursor()
        
        if event.keysym == "BackSpace":
            if self._cursor_pos > 0:
                self._text = self._text[:self._cursor_pos-1] + self._text[self._cursor_pos:]
                self._cursor_pos -= 1
        elif event.keysym == "Delete":
            if self._cursor_pos < len(self._text):
                self._text = self._text[:self._cursor_pos] + self._text[self._cursor_pos+1:]
        elif event.keysym == "Left":
            if self._cursor_pos > 0:
                self._cursor_pos -= 1
        elif event.keysym == "Right":
            if self._cursor_pos < len(self._text):
                self._cursor_pos += 1
        elif event.keysym == "Home":
            self._cursor_pos = 0
        elif event.keysym == "End":
            self._cursor_pos = len(self._text)
        elif len(event.char) > 0 and event.char.isprintable():
            self._text = self._text[:self._cursor_pos] + event.char + self._text[self._cursor_pos:]
            self._cursor_pos += 1
        
        self.itemconfig(self.text_id, text=self._text, fill=self.text_color)
        self._update_cursor()

    def _update_cursor(self):
        substr = self._text[:self._cursor_pos]
        cursor_x = self.text_x + self._font.measure(substr)
        cursor_y = self.text_y + self.cursor_y_offset
        if self.cursor:
            self.cursor.move(cursor_x, cursor_y)

    def get(self):
        return self._text

    def set(self, text):
        self._text = text
        self._cursor_pos = len(text)
        self.itemconfig(self.text_id, text=text, fill=self.text_color)
        self._update_cursor()

    def insert(self, idx, txt):
        self._text = self._text[:idx] + txt + self._text[idx:]
        self._cursor_pos = idx + len(txt)
        self.itemconfig(self.text_id, text=self._text, fill=self.text_color)
        self._update_cursor()

    def delete(self, first, last=None):
        if first == "end" or first == tk.END:
            first = len(self._text)
        if last is None:
            last = first + 1
        elif last == "end" or last == tk.END:
            last = len(self._text)
        first = max(0, min(first, len(self._text)))
        last = max(0, min(last, len(self._text)))
        if first > last:
            first, last = last, first
        self._text = self._text[:first] + self._text[last:]
        self._cursor_pos = first
        self.itemconfig(self.text_id, text=self._text, fill=self.text_color)
        self._update_cursor()

    def _draw_rounded_rect(self, x1, y1, x2, y2, **kwargs):
        radius = kwargs.pop('radius', 6)
        if radius == 0:
            return self.create_rectangle(x1, y1, x2, y2, **kwargs)
        points = []
        top = y1 + radius
        bottom = y2 - radius
        left = x1 + radius
        right = x2 - radius
        points.extend([x1, top])
        points.extend(self._get_arc_points(left, top, radius, math.pi, math.pi * 1.5))
        points.extend([right, y1])
        points.extend(self._get_arc_points(right, top, radius, math.pi * 1.5, math.pi * 2))
        points.extend([x2, bottom])
        points.extend(self._get_arc_points(right, bottom, radius, 0, math.pi * 0.5))
        points.extend([left, y2])
        points.extend(self._get_arc_points(left, bottom, radius, math.pi * 0.5, math.pi))
        points.extend([x1, top])
        return self.create_polygon(points, **kwargs, smooth=True, width=1)
    
    def _get_arc_points(self, cx, cy, radius, start_angle, end_angle, segments=8):
        points = []
        for i in range(segments + 1):
            angle = start_angle + (end_angle - start_angle) * i / segments
            points.extend([cx + radius * math.cos(angle), cy + radius * math.sin(angle)])
        return points

    def _on_resize(self, event):
        """父容器大小变化时，强制更新 Canvas 宽度"""
        new_width = event.width - 100  # 减去 padding
        self.config(width=new_width)
        self.height = self.winfo_height()

        # 重绘边框
        self.delete(self.rect_id)
        self.rect_id = self._draw_rounded_rect(
            1, 1, new_width - 1, self.height - 1,
            fill=self.bg_color,
            outline=self.border_focus if ModernEntry._active_cursor == self else self.border_normal,
            radius=2
        )

        # 更新文本和光标
        font_height = self._font.metrics("linespace")
        self.text_y = (self.height - font_height) // 2
        self.coords(self.text_id, self.text_x, self.text_y)
        self._update_cursor()

class DemoApp:
    """紧凑布局的演示应用程序"""
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Entry Demo")
        self.root.geometry("420x380")
        self.root.configure(bg="#1e1e1e")
        
        # 主容器
        container = tk.Frame(root, bg="#1e1e1e", padx=20, pady=20)
        container.pack(fill="both", expand=True)
        
        # 标题区
        header_frame = tk.Frame(container, bg="#1e1e1e")
        header_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(
            header_frame, 
            text="Modern Entry", 
            font=("Segoe UI", 16, "bold"), 
            fg="#4ec9b0", 
            bg="#1e1e1e"
        ).pack(side="left")
        
        tk.Label(
            header_frame, 
            text="Smooth cursor animation", 
            font=("Segoe UI", 10), 
            fg="#888888", 
            bg="#1e1e1e"
        ).pack(side="left", padx=(10, 0))
        
        # 输入框区域
        form_frame = tk.Frame(container, bg="#1e1e1e")
        form_frame.pack(fill="both", expand=True)
        
        # 用户名输入框
        self._create_labeled_entry(form_frame, "Username:", "Enter your username", 0)
        
        # 密码输入框
        self._create_labeled_entry(form_frame, "Password:", "Enter your password", 1)
        
        # 邮箱输入框
        self._create_labeled_entry(form_frame, "Email:", "your.email@example.com", 2)
        
        # 按钮区域
        button_frame = tk.Frame(container, bg="#1e1e1e")
        button_frame.pack(fill="x", pady=(15, 0))
        
        # 提交按钮
        submit_btn = tk.Button(
            button_frame,
            text="Submit",
            font=("Segoe UI", 10, "bold"),
            bg="#4ec9b0",
            fg="#1e1e1e",
            activebackground="#3db09e",
            activeforeground="#ffffff",
            relief="flat",
            padx=20,
            pady=6,
            command=self.submit_form
        )
        submit_btn.pack(side="right", padx=(10, 0))
        
        # 清除按钮
        clear_btn = tk.Button(
            button_frame,
            text="Clear All",
            font=("Segoe UI", 10),
            bg="#444444",
            fg="#cccccc",
            activebackground="#555555",
            activeforeground="#ffffff",
            relief="flat",
            padx=20,
            pady=6,
            command=self.clear_form
        )
        clear_btn.pack(side="right")
        
    def _create_labeled_entry(self, parent, label_text, placeholder, row):
        """创建带标签的输入框"""
        label = tk.Label(
            parent, 
            text=label_text, 
            font=("Segoe UI", 10), 
            fg="#cccccc", 
            bg="#1e1e1e",
            width=10,
            anchor="w"
        )
        label.grid(row=row, column=0, pady=8, sticky="w")
        
        entry = ModernEntry(
            parent, 
            width=260, 
            height=36, 
            placeholder=placeholder,
            font_family="Segoe UI",
            font_size=12
        )
        entry.grid(row=row, column=1, padx=(0, 10), pady=8, sticky="w")
        
        # 保存引用
        setattr(self, f"entry_{row}", entry)
        
        # 配置列权重
        parent.columnconfigure(1, weight=1)
        
    def submit_form(self):
        """提交表单数据"""
        username = self.entry_0.get()
        password = self.entry_1.get()
        email = self.entry_2.get()
        
        print("\n--- Form Submission ---")
        print(f"Username: {username}")
        print(f"Password: {password}")
        print(f"Email: {email}")
        print("----------------------\n")
        
        # 显示成功消息
        success = tk.Label(
            self.root, 
            text="✓ Form submitted successfully!", 
            font=("Segoe UI", 10), 
            fg="#4ec9b0", 
            bg="#1e1e1e"
        )
        success.place(relx=0.5, rely=0.92, anchor="center")
        self.root.after(2000, success.destroy)
    
    def clear_form(self):
        """清除所有输入框内容"""
        self.entry_0.set("")
        self.entry_1.set("")
        self.entry_2.set("")
        self.root.focus()

class MyWindow(tk.Tk):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.title('我是无辜的窗口')
        self.geometry('400x300')

        # 绑定动作 <Configure>
        self.bind('<Configure>', self.myCall)

    # 定义触发的事件
    def myCall(self, event=None):
        print('调用 myCall 函数')
        print('此时窗口尺寸为：{}x{}'.format(self.winfo_width(),self.winfo_height()))

if __name__ == '__main__':
    myWindow = MyWindow()
    myWindow.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = DemoApp(root)
    root.mainloop()