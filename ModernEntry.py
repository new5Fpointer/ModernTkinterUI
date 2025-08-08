# ModernEntry_fixed.py
import tkinter as tk
import tkinter.font as tkfont

# ====================== 常量定义 ======================
# 尺寸常量
DEFAULT_WIDTH = 240
DEFAULT_HEIGHT = 36
DEFAULT_RADIUS = 8
DEFAULT_CURSOR_HEIGHT = 18
DEFAULT_CURSOR_BLINK_SPEED = 450
TEXT_PADDING_X = 12
MIN_CURSOR_HEIGHT = 14
CURSOR_VERTICAL_OFFSET_REDUCTION = 4
MAX_TEXT_LENGTH = 1000  # 默认最大文本长度

# 颜色常量
BG_COLOR = "#1e1e1e"
ENTRY_BG_COLOR = "#2d2d2d"
BORDER_NORMAL_COLOR = "#444444"
BORDER_FOCUS_COLOR = "#4ec9b0"
TEXT_COLOR = "#e0e0e0"
PLACEHOLDER_COLOR = "#888888"
CURSOR_COLOR = "#6bd8c9"
BUTTON_BG_COLOR = "#4ec9b0"
BUTTON_TEXT_COLOR = "#1e1e1e"
BUTTON_ACTIVE_BG = "#3db09e"
BUTTON_ACTIVE_FG = "#ffffff"
BUTTON_SECONDARY_BG = "#444444"
BUTTON_SECONDARY_FG = "#cccccc"
BUTTON_SECONDARY_ACTIVE_BG = "#555555"
SUCCESS_COLOR = "#4ec9b0"
SELECTION_COLOR = "#3da89b"  # 选择区域颜色（略暗于光标颜色）

# 字体常量
ENTRY_FONT_FAMILY = "Segoe UI"
ENTRY_FONT_SIZE = 12

# 应用常量
APP_TITLE = "Modern Entry Demo"
APP_GEOMETRY = "420x380"
CONTAINER_PAD_X = 20
CONTAINER_PAD_Y = 20
HEADER_PAD_Y = (0, 15)
BUTTON_PAD_Y = (15, 0)
SUCCESS_MESSAGE_DURATION = 2000  # ms
ENTRY_GRID_PAD_X = (0, 10)
ENTRY_GRID_PAD_Y = 8
BUTTON_PAD_X = (10, 0)

# ====================== PureCursor ======================
class PureCursor:
    """自定义光标控件，实现闪烁效果"""
    
    def __init__(self, canvas, x=0, y=0, height=DEFAULT_CURSOR_HEIGHT, width=1,
                 color=CURSOR_COLOR, blink_speed=DEFAULT_CURSOR_BLINK_SPEED):
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
        """移动光标到指定位置"""
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
        """实现光标的闪烁效果"""
        self.visible = not self.visible
        fill = self.color if self.visible else ""
        self.canvas.itemconfig(self.cursor_id, fill=fill)
        self.blink_id = self.canvas.after(self.blink_speed, self.blink)

    def start_blinking(self):
        """开始光标闪烁"""
        if self.blink_id:
            self.canvas.after_cancel(self.blink_id)
        self.visible = True
        self.canvas.itemconfig(self.cursor_id, fill=self.color)
        self.blink_id = self.canvas.after(self.blink_speed, self.blink)

    def stop_blinking(self):
        """停止光标闪烁"""
        if self.blink_id:
            self.canvas.after_cancel(self.blink_id)
            self.blink_id = None
        self.visible = False
        self.canvas.itemconfig(self.cursor_id, fill="")

    def set_height(self, height):
        """设置光标高度"""
        self.height = height
        self.canvas.coords(self.cursor_id, self.x, self.y, self.x + self.width, self.y + height)

    def set_color(self, color):
        """设置光标颜色"""
        self.color = color
        if self.visible:
            self.canvas.itemconfig(self.cursor_id, fill=color)

    def destroy(self):
        """销毁光标"""
        self.stop_blinking()
        try:
            self.canvas.delete(self.cursor_id)
        except tk.TclError:
            pass
    
    def hide(self):
        """隐藏光标"""
        self.canvas.itemconfig(self.cursor_id, state='hidden')

    def show(self):
        """显示光标"""
        self.canvas.itemconfig(self.cursor_id, state='normal')


# ====================== ModernEntry ======================
class ModernEntry(tk.Canvas):
    """现代风格的输入框组件"""
    
    _active_cursor = None  # 当前活动的光标
    _first_entry = None    # 第一个创建的输入框实例

    def __init__(self, master, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT, 
                 radius=DEFAULT_RADIUS, bg_color=ENTRY_BG_COLOR, 
                 border_normal=BORDER_NORMAL_COLOR, border_focus=BORDER_FOCUS_COLOR, 
                 text_color=TEXT_COLOR, placeholder="", 
                 placeholder_color=PLACEHOLDER_COLOR, font_family=ENTRY_FONT_FAMILY, 
                 font_size=ENTRY_FONT_SIZE, fixed_size=True, max_length=MAX_TEXT_LENGTH, **kwargs):
        
        # 初始化画布
        super().__init__(master, width=width, height=height,
                         highlightthickness=0, bd=0, bg=bg_color)
        
        # 保存配置参数
        self.bg_color = bg_color
        self.border_normal = border_normal
        self.border_focus = border_focus
        self.text_color = text_color
        self.placeholder = placeholder
        self.placeholder_color = placeholder_color
        self._cursor_pos = 0          # 光标位置（字符索引）
        self._text = ""               # 输入的文本内容
        self._font = tkfont.Font(family=font_family, size=font_size)
        self._cursor_height = DEFAULT_CURSOR_HEIGHT
        self._radius = radius
        self._text_left = 0           # 文本水平偏移量（用于滚动）
        self.fixed_size = fixed_size  # 是否固定尺寸
        self._original_border_focus = border_focus
        self._current_border_focus  = border_focus
        
        # 添加最大长度限制
        if max_length is not None and max_length < 1:
            raise ValueError("max_length must be at least 1 or None for no limit")
        self.max_length = max_length  # 最大输入长度
        
        # 计算文本位置
        font_height = self._font.metrics("linespace")
        self.text_x = TEXT_PADDING_X
        self.text_y = (height - font_height) // 2  # 垂直居中
        self.cursor_y_offset = max(0, (font_height - self._cursor_height) // 2)
        
        # 创建文本显示对象
        self.text_id = self.create_text(
            self.text_x, self.text_y,
            text=placeholder, anchor="nw",
            fill=placeholder_color, font=self._font)
        
        # 绘制背景和边框
        self._redraw_rect(width, height)  
        
        # 初始化光标
        self.cursor = None
        
        # 选择相关变量
        self._select_start = None     # 选择开始位置
        self._dragging_select = False # 是否正在拖动选择
        self._selection_rect = None   # 选择区域矩形ID
        self._selection_rects = []    # 选择区域矩形列表（用于多段选择）
        
        # 绑定事件处理
        self._bind_events()
        
        # 如果是第一个实例，设置全局Tab键处理
        if ModernEntry._first_entry is None:
            ModernEntry._first_entry = self
        self._bind_root_tab()
        
        # 确保文本显示在最上层
        self.tag_raise(self.text_id)

    # ====================== 事件绑定相关方法 ======================
    def _bind_events(self):
        """绑定所有事件处理函数"""
        self.bind("<Button-1>", self._on_click)
        self.bind("<Key>", self._on_key_press)
        self.bind("<BackSpace>", self._on_key_press)
        self.bind("<Delete>", self._on_key_press)
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
        self.bind("<Tab>", self._on_tab)
        self.bind("<B1-Motion>", self._on_drag)  # 鼠标拖动选择
        self.bind("<ButtonRelease-1>", self._on_release)  # 鼠标释放
        
        # 添加粘贴支持
        self.bind("<Control-v>", self._on_paste)
        self.bind("<Control-V>", self._on_paste)  # 处理大写V的情况
        self.bind("<Control-c>", self._on_copy)   # 添加复制支持
        self.bind("<Control-C>", self._on_copy)   # 添加复制支持
        self.bind("<Control-a>", self._select_all) # 添加全选支持
        self.bind("<Control-A>", self._select_all) # 添加全选支持
        
        # 固定尺寸处理
        if self.fixed_size:
            # 阻止调整大小
            self.bind("<Configure>", lambda e: "break")
        else:
            # 允许调整大小
            self.bind("<Configure>", self._on_resize)

    def _bind_root_tab(self):
        """绑定全局Tab键处理"""
        root = self.winfo_toplevel()
        if getattr(root, "_modern_tab_bound", None):
            return
        root._modern_tab_bound = True

        def _global_tab(event):
            """全局Tab键处理函数"""
            focus = event.widget.focus_get()
            if isinstance(focus, ModernEntry):
                return None
            if ModernEntry._first_entry and ModernEntry._first_entry.winfo_exists():
                ModernEntry._first_entry.focus_set()
                return "break"
            return None

        root.bind_all("<Tab>", _global_tab, add="+")

    # ====================== 文本操作相关方法 ======================
    def _fix_index(self, idx):
        """规范化索引位置，确保在有效范围内"""
        if idx in (tk.END, "end"):
            return len(self._text)
        try:
            idx = int(idx)
        except ValueError:
            idx = 0
        if idx < 0:
            idx = max(0, len(self._text) + idx)
        return max(0, min(idx, len(self._text)))
    
    def _normalize_selection(self):
        """确保选择开始和结束位置是有效的"""
        if self._select_start is None:
            return None, None
        
        start = min(self._select_start, self._cursor_pos)
        end = max(self._select_start, self._cursor_pos)
        return start, end

    def insert(self, idx, txt):
        """在指定位置插入文本"""
        # 检查最大长度限制
        if self.max_length is not None:
            # 计算当前文本长度和剩余可用空间
            current_length = len(self._text)
            remaining = self.max_length - current_length
            
            # 如果没有剩余空间，直接返回
            if remaining <= 0:
                return
                
            # 截取文本以适应最大长度
            if len(txt) > remaining:
                txt = txt[:remaining]
        
        idx = self._fix_index(idx)
        self._text = self._text[:idx] + txt + self._text[idx:]
        self._cursor_pos = idx + len(txt)
        self._refresh_text_and_cursor()
        
        # 插入文本后清除选择
        self._select_start = None
        self._clear_selection()

    def delete(self, first, last=None, internal=False):
        """删除指定范围内的文本
        参数:
            first: 删除起始位置
            last: 删除结束位置（可选）
            internal: 是否为内部调用（如清除选择区域），防止递归
        """
        if internal:
            return  # 防止递归调用

        # 如果有选择区域，则删除选择区域
        start, end = self._normalize_selection()
        if start is not None and end is not None:
            self._text = self._text[:start] + self._text[end:]
            self._cursor_pos = start
            self._select_start = None
            self._clear_selection(internal=True)  # 标记为内部调用
            self._refresh_text_and_cursor()
            return

        first = self._fix_index(first)
        last = first + 1 if last is None else self._fix_index(last)
        if first > last:
            first, last = last, first
        self._text = self._text[:first] + self._text[last:]
        self._cursor_pos = first
        self._refresh_text_and_cursor()

        # 删除文本后清除选择
        self._select_start = None
        self._clear_selection(internal=True)

    def set(self, text):
        """设置输入框的文本内容"""
        # 检查最大长度限制
        if self.max_length is not None and len(text) > self.max_length:
            text = text[:self.max_length]
            
        self._text = text
        self._cursor_pos = len(text)
        self._text_left = 0
        self.coords(self.text_id, self.text_x, self.text_y)

        # 更新显示文本
        if text:
            self.itemconfig(self.text_id, text=text, fill=self.text_color)
        else:
            self.itemconfig(self.text_id, text=self.placeholder, fill=self.placeholder_color)

        # 确保光标存在
        if self.cursor is None:
            self._create_cursor()
            self.cursor.hide()

        # 滚动到光标位置
        self._scroll_to_cursor()
        
        # 清除选择
        self._select_start = None
        self._clear_selection()

    def get(self):
        """获取输入框的文本内容"""
        return self._text
    
    def get_selected_text(self):
        """获取选中的文本"""
        start, end = self._normalize_selection()
        if start is None or end is None or start == end:
            return ""
        return self._text[start:end]

    def _refresh_text_and_cursor(self):
        """刷新文本显示和光标位置"""
        # 根据是否有文本决定显示内容
        show_text = self._text if self._text else self.placeholder
        show_color = self.text_color if self._text else self.placeholder_color
        self.itemconfig(self.text_id, text=show_text, fill=show_color)
        
        if self.max_length is not None and len(self._text) >= self.max_length:
            new_color = "#ff4d4d"          # 红色
        else:
            new_color = self._original_border_focus

        if new_color != self._current_border_focus:
            self._current_border_focus = new_color
            # 如果当前正是焦点状态，马上重绘
            if self is self.focus_displayof():
                self._redraw_rect(self.winfo_width(), self.winfo_height(), focus=True)

        # 4. 光标与滚动
        self._update_cursor()
        self._scroll_to_cursor()
        self._update_selection_visual()

    # ====================== 选择区域相关方法 ======================
    def _clear_selection(self, internal=False):
        """清除选择区域"""
        for rect in self._selection_rects:
            self.delete(rect, internal=True)  # 防止递归
        self._selection_rects = []
        self._selection_rect = None
    
    def _update_selection_visual(self):
        """更新选择区域的视觉显示"""
        # 先清除之前的选择区域
        self._clear_selection()
        
        # 如果没有选择开始位置或选择范围无效
        if self._select_start is None or self._select_start == self._cursor_pos:
            return
        
        # 计算选择范围的开始和结束位置
        start = min(self._select_start, self._cursor_pos)
        end = max(self._select_start, self._cursor_pos)
        
        # 计算选择区域的坐标
        start_x = self._font.measure(self._text[:start]) + self.text_x + self._text_left
        end_x = self._font.measure(self._text[:end]) + self.text_x + self._text_left
        
        # 计算文本高度
        font_height = self._font.metrics("linespace")
        y1 = self.text_y
        y2 = y1 + font_height
        
        # 创建选择区域矩形
        self._selection_rect = self.create_rectangle(
            start_x, y1, end_x, y2,
            fill=SELECTION_COLOR, outline="", width=0
        )
        self._selection_rects.append(self._selection_rect)
        
        # 确保选择区域在文本下方但在背景上方
        self.tag_lower(self._selection_rect, self.text_id)
        self.tag_raise(self.text_id)
        if self.cursor:
            self.tag_raise(self.cursor.cursor_id)

    # ====================== 光标操作相关方法 ======================
    def _create_cursor(self):
        """创建光标对象"""
        if self.cursor is None:
            self.cursor = PureCursor(
                self,
                x=self.text_x,
                y=self.text_y + self.cursor_y_offset,
                height=self._cursor_height,
                width=1,
                color=CURSOR_COLOR,
                blink_speed=DEFAULT_CURSOR_BLINK_SPEED
            )
            self.cursor.stop_blinking()
            self.cursor.hide() 

    def _update_cursor(self):
        """更新光标位置"""
        if self.cursor is None:
            self._create_cursor()
            
        # 计算光标位置
        substr = self._text[:self._cursor_pos]
        cursor_x = self.text_x + self._font.measure(substr) + self._text_left
        cursor_y = self.text_y + self.cursor_y_offset
        self.cursor.move(cursor_x, cursor_y)

    # ====================== 事件处理相关方法 ======================
    def _on_click(self, event):
        """鼠标点击事件处理（优化版）"""
        if self.cursor is None:
            self._create_cursor()

        # 使用新方法计算字符索引
        click_pos = self._get_char_index_at_x(event.x)
        
        # 设置光标位置和选择起点
        self._cursor_pos = click_pos
        self._select_start = click_pos
        self._dragging_select = True
        
        # 更新显示
        self._update_cursor()
        self._scroll_to_cursor()
        self.focus_set()
        self._update_selection_visual()
    
    def _on_drag(self, event):
        """鼠标拖动事件处理"""
        if not self._dragging_select:
            return
            
        # 使用新方法计算字符索引
        new_pos = self._get_char_index_at_x(event.x)
        
        # 更新光标位置
        if new_pos != self._cursor_pos:
            self._cursor_pos = new_pos
            self._update_cursor()
            self._scroll_to_cursor()
            self._update_selection_visual()
    
    def _on_release(self, event):
        """鼠标释放事件处理"""
        self._dragging_select = False

    def _on_key_press(self, event):
        """键盘按键事件处理"""
        if self.cursor is None:
            self._create_cursor()

        # 是否是首次按键（用于滚动处理）
        first_key_after_focus_in = (self._cursor_pos == 0 and self._text_left == 0)
        keysym = event.keysym
        shift_pressed = (event.state & 0x0001) != 0  # 检查Shift键是否按下

        def _keep_cursor_fixed():
            """保持光标在窗口中的位置不变（用于滚动调整）"""
            # 计算光标位置变化量
            current_cursor_x = self.text_x + self._font.measure(self._text[:self._cursor_pos]) + self._text_left
            
            # 计算新的光标位置
            new_cursor_x = self.text_x + self._font.measure(self._text[:self._cursor_pos]) + self._text_left
            
            # 调整文本偏移量
            delta = new_cursor_x - current_cursor_x
            self._text_left -= delta

            # 确保滚动位置在有效范围内
            max_left = 0
            min_left = min(0, self.winfo_width() - 2 * self.text_x - self._font.measure(self._text))
            self._text_left = max(min_left, min(max_left, self._text_left))

        # 处理不同按键
        if keysym == "BackSpace":
            # 如果有选择区域，删除选择区域
            if self._select_start is not None and self._select_start != self._cursor_pos:
                self.delete(0, tk.END)  # 这会触发删除选择区域
                return
                
            if self._cursor_pos > 0:
                self._text = self._text[:self._cursor_pos - 1] + self._text[self._cursor_pos:]
                self._cursor_pos -= 1
                if not first_key_after_focus_in:
                    _keep_cursor_fixed()

        elif keysym == "Delete":
            # 如果有选择区域，删除选择区域
            if self._select_start is not None and self._select_start != self._cursor_pos:
                self.delete(0, tk.END)  # 这会触发删除选择区域
                return
                
            if self._cursor_pos < len(self._text):
                self._text = self._text[:self._cursor_pos] + self._text[self._cursor_pos + 1:]
                if not first_key_after_focus_in:
                    _keep_cursor_fixed()

        elif keysym == "Left":
            if shift_pressed:
                # Shift+左键：扩展选择范围
                if self._select_start is None:
                    self._select_start = self._cursor_pos
                self._cursor_pos = max(0, self._cursor_pos - 1)
            else:
                # 普通左键：移动光标并清除选择
                self._select_start = None
                self._clear_selection()
                self._cursor_pos = max(0, self._cursor_pos - 1)
                
        elif keysym == "Right":
            if shift_pressed:
                # Shift+右键：扩展选择范围
                if self._select_start is None:
                    self._select_start = self._cursor_pos
                self._cursor_pos = min(len(self._text), self._cursor_pos + 1)
            else:
                # 普通右键：移动光标并清除选择
                self._select_start = None
                self._clear_selection()
                self._cursor_pos = min(len(self._text), self._cursor_pos + 1)
                
        elif keysym == "Home":
            if shift_pressed:
                # Shift+Home：选择到开头
                if self._select_start is None:
                    self._select_start = self._cursor_pos
                self._cursor_pos = 0
            else:
                # Home：移动到开头并清除选择
                self._select_start = None
                self._clear_selection()
                self._cursor_pos = 0
                
        elif keysym == "End":
            if shift_pressed:
                # Shift+End：选择到结尾
                if self._select_start is None:
                    self._select_start = self._cursor_pos
                self._cursor_pos = len(self._text)
            else:
                # End：移动到结尾并清除选择
                self._select_start = None
                self._clear_selection()
                self._cursor_pos = len(self._text)
                
        elif event.char and event.char.isprintable():
            # 检查最大长度限制
            if self.max_length is not None and len(self._text) >= self.max_length:
                return  # 已达到最大长度，不再接受输入
                
            # 如果有选择区域，先删除选择区域
            if self._select_start is not None and self._select_start != self._cursor_pos:
                self.delete(0, tk.END)  # 这会触发删除选择区域
                
            self._text = self._text[:self._cursor_pos] + event.char + self._text[self._cursor_pos:]
            self._cursor_pos += 1
            if not first_key_after_focus_in:
                _keep_cursor_fixed()
        else:
            return

        # 刷新文本和光标
        self._refresh_text_and_cursor()
        self._scroll_to_cursor()
    
    def _on_copy(self, event):
        """复制选中的文本"""
        selected_text = self.get_selected_text()
        if selected_text:
            self.clipboard_clear()
            self.clipboard_append(selected_text)
        return "break"
    
    def _select_all(self, event):
        """全选文本"""
        self._select_start = 0
        self._cursor_pos = len(self._text)
        self._refresh_text_and_cursor()
        return "break"

    def _on_paste(self, event):
        """处理粘贴事件"""
        try:
            # 从剪贴板获取内容
            clipboard_text = self.clipboard_get()
        except tk.TclError:
            return  # 剪贴板为空或非文本内容
        
        if not clipboard_text:
            return
        
        # 过滤掉换行符（单行输入框）
        clipboard_text = clipboard_text.replace('\n', ' ').replace('\r', '')
        
        # 检查最大长度限制
        if self.max_length is not None:
            # 计算当前文本长度和剩余可用空间
            current_length = len(self._text)
            remaining = self.max_length - current_length
            
            # 如果没有剩余空间，直接返回
            if remaining <= 0:
                return
                
            # 截取文本以适应最大长度
            if len(clipboard_text) > remaining:
                clipboard_text = clipboard_text[:remaining]
        
        # 如果有选择区域，先删除选择区域
        if self._select_start is not None and self._select_start != self._cursor_pos:
            self.delete(0, tk.END)  # 这会触发删除选择区域
        
        # 在光标位置插入文本
        self.insert(self._cursor_pos, clipboard_text)
        return "break"  # 阻止默认处理

    def _on_focus_in(self, event=None):
        """获得焦点事件处理"""
        if self.cursor is None:
            self._create_cursor()
            
        # 处理活动光标
        if ModernEntry._active_cursor and ModernEntry._active_cursor != self:
            ModernEntry._active_cursor.cursor.stop_blinking()
            ModernEntry._active_cursor.cursor.hide()
            
        ModernEntry._active_cursor = self
        
        # 启动光标闪烁
        self.cursor.show()
        self.cursor.start_blinking()
        
        # 重绘边框（焦点状态）
        self._redraw_rect(self.winfo_width(), self.winfo_height(), focus=True)
        
        # 更新选择区域显示
        self._update_selection_visual()

    def _on_focus_out(self, event=None):
        """失去焦点事件处理"""
        if ModernEntry._active_cursor == self:
            if self.cursor:
                self.cursor.stop_blinking()
                self.cursor.hide()
            ModernEntry._active_cursor = None

        # 重置光标位置
        self._cursor_pos = 0
        self._text_left = 0
        self.coords(self.text_id, self.text_x, self.text_y)

        # 更新光标位置
        if self.cursor is None:
            self._create_cursor()
        cursor_x = self.text_x + self._font.measure(self._text[:self._cursor_pos]) + self._text_left
        cursor_y = self.text_y + self.cursor_y_offset
        self.cursor.move(cursor_x, cursor_y)

        # 重绘边框（非焦点状态）
        self._redraw_rect(self.winfo_width(), self.winfo_height(), focus=False)
        
        # 清除选择
        self._select_start = None
        self._clear_selection()

    def _on_tab(self, event):
        """Tab键事件处理（空实现）"""
        pass
    def _get_char_index_at_x(self, x):
        """根据x坐标获取对应的字符索引"""
        click_x_text = x - (self.text_x + self._text_left)
        
        # 处理空文本的情况
        if not self._text:
            return 0
        
        # 使用二分查找优化性能
        left, right = 0, len(self._text)
        while left < right:
            mid = (left + right) // 2
            substr_width = self._font.measure(self._text[:mid])
            if substr_width <= click_x_text:
                left = mid + 1
            else:
                right = mid
        
        # 确定最接近的位置
        if left > 0:
            prev_width = self._font.measure(self._text[:left-1])
            curr_width = self._font.measure(self._text[:left])
            if abs(click_x_text - prev_width) < abs(click_x_text - curr_width):
                return left - 1
        
        return left

    # ====================== 滚动相关方法 ======================
    def _scroll_to_cursor(self):
        """滚动文本使光标可见"""
        if not self._text:
            self._text_left = 0
            self.coords(self.text_id, self.text_x, self.text_y)
            if self.cursor:
                self._update_cursor()
            return

        # 计算光标位置和文本宽度
        cursor_rel_x = self._font.measure(self._text[:self._cursor_pos])
        visible_w = self.winfo_width() - 2 * self.text_x
        text_width = self._font.measure(self._text)

        # 获取光标宽度（如果光标不存在则使用默认值1）
        cursor_width = self.cursor.width if self.cursor else 1

        # 文本宽度小于可视区域时，左对齐
        if text_width <= visible_w:
            self._text_left = 0
        else:
            cursor_left = cursor_rel_x + self._text_left
            cursor_right = cursor_left + cursor_width

            # 根据光标位置调整滚动
            if cursor_left < 0:
                self._text_left = -cursor_rel_x
            elif cursor_right > visible_w:
                self._text_left = -(cursor_rel_x + cursor_width - visible_w)

            # 确保滚动位置在有效范围内
            min_left = min(0, visible_w - text_width)
            max_left = 0
            self._text_left = max(min_left, min(max_left, self._text_left))

        # 更新文本位置
        self.coords(self.text_id, self.text_x + self._text_left, self.text_y)
        self._update_cursor()
        self._update_selection_visual()

    # ====================== 布局和绘制相关方法 ======================
    def _on_resize(self, event):
        """窗口大小变化事件处理"""
        # 仅当允许调整大小时才处理
        if self.fixed_size:
            return
        
        w, h = event.width, event.height
        
        # 重绘背景
        self._redraw_rect(w, h, focus=(self.focus_get() == self))

        # 更新文本垂直位置
        font_height = self._font.metrics("linespace")
        self.text_y = (h - font_height) // 2

        # 更新光标高度
        if self.cursor is None:
            self._create_cursor()
        cursor_h = max(MIN_CURSOR_HEIGHT, font_height - CURSOR_VERTICAL_OFFSET_REDUCTION)
        self.cursor.set_height(cursor_h)

        # 调整文本偏移量
        current_text_width = self._font.measure(self._text)
        visible_w = w - 2 * self.text_x
        
        # 计算当前光标位置
        current_cursor_rel_x = self._font.measure(self._text[:self._cursor_pos])
        current_visible_start = -self._text_left
        current_visible_end = current_visible_start + visible_w
        
        # 调整文本偏移量
        if current_text_width > visible_w:
            # 保持当前可视区域内的文本位置
            if current_cursor_rel_x < current_visible_start:
                self._text_left = -current_cursor_rel_x
            elif current_cursor_rel_x > current_visible_end:
                self._text_left = -(current_cursor_rel_x - visible_w)
            else:
                # 保持当前可视区域的相对位置
                visible_ratio = (current_cursor_rel_x - current_visible_start) / (current_visible_end - current_visible_start)
                new_visible_start = max(0, min(current_text_width - visible_w, current_text_width * visible_ratio - visible_w * visible_ratio))
                self._text_left = -new_visible_start
        else:
            self._text_left = 0

        # 确保滚动位置在有效范围内
        min_left = min(0, visible_w - current_text_width)
        max_left = 0
        self._text_left = max(min_left, min(max_left, self._text_left))

        # 保证光标在可视区域
        self._scroll_to_cursor()

    def _redraw_rect(self, w, h, focus=False):
        """重绘圆角矩形背景和边框（只改颜色，不重建对象）"""
        if hasattr(self, '_rect_outline') and self._rect_outline:
            color = self._current_border_focus if focus else self.border_normal
            self.itemconfig(self._rect_outline, outline=color)
            return

        # 第一次创建
        r = min(h // 2, self._radius)
        x1, y1, x2, y2 = 0, 0, w - 1, h - 1
        pts = self._rounded_rect_pts(x1, y1, x2, y2, r)

        self._rect_bg = self.create_polygon(
            pts, fill=self.bg_color, outline="", smooth=True)
        self._rect_outline = self.create_polygon(
            pts, fill="", outline=self.border_focus if focus else self.border_normal,
            smooth=True, width=1)

        # 保证文本和光标始终在最上层
        self.tag_raise(self.text_id)
        if getattr(self, 'cursor', None) and self.cursor:
            self.tag_raise(self.cursor.cursor_id)

    def _rounded_rect_pts(self, x1, y1, x2, y2, r):
        """生成圆角矩形的多边形点坐标"""
        return [
            x1 + r, y1,  # 起点
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1
        ]


# ====================== DemoApp ======================
class DemoApp:
    """演示应用程序"""
    
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(APP_GEOMETRY)
        self.root.configure(bg=BG_COLOR)

        # 创建主容器
        container = tk.Frame(root, bg=BG_COLOR, padx=CONTAINER_PAD_X, pady=CONTAINER_PAD_Y)
        container.pack(fill="both", expand=True)

        # 创建标题区域
        self._create_header(container)
        
        # 创建表单区域
        form_frame = tk.Frame(container, bg=BG_COLOR)
        form_frame.pack(fill="both", expand=True)
        
        # 创建输入框 - 固定大小
        self.entry_0 = self._create_labeled_entry(form_frame, "Username:", "Enter your username", 0, fixed_size=True, max_length=20)
        # 创建输入框 - 可调整大小
        self.entry_1 = self._create_labeled_entry(form_frame, "Password:", "Enter your password", 1, fixed_size=False, max_length=50)
        self.entry_2 = self._create_labeled_entry(form_frame, "Email:", "your.email@example.com", 2, fixed_size=False, max_length=100)

        # 创建按钮区域
        self._create_buttons(container)
        
        # 配置网格布局权重
        container.columnconfigure(0, weight=1)
        container.rowconfigure(2, weight=1)
        form_frame.columnconfigure(1, weight=1)
        
        # 绑定根窗口点击事件
        self.root.bind("<Button-1>", self._on_root_click)

    def _create_header(self, parent):
        """创建标题区域"""
        header_frame = tk.Frame(parent, bg=BG_COLOR)
        header_frame.pack(fill="x", pady=HEADER_PAD_Y)
        
        tk.Label(
            header_frame, text="Modern Entry", font=("Segoe UI", 16, "bold"),
            fg=SUCCESS_COLOR, bg=BG_COLOR).pack(side="left")
        tk.Label(
            header_frame, text="Smooth cursor animation", font=("Segoe UI", 10),
            fg=PLACEHOLDER_COLOR, bg=BG_COLOR).pack(side="left", padx=(10, 0))
            
        # 添加选择功能提示
        tk.Label(
            header_frame, text="(Now with selection support!)", font=("Segoe UI", 9),
            fg=SELECTION_COLOR, bg=BG_COLOR).pack(side="right", padx=(0, 10))

    def _create_labeled_entry(self, parent, label_text, placeholder, row, fixed_size=True, max_length=MAX_TEXT_LENGTH):
        """创建带标签的输入框"""
        label = tk.Label(
            parent, text=label_text, font=("Segoe UI", 10),
            fg=TEXT_COLOR, bg=BG_COLOR, width=10, anchor="w")
        label.grid(row=row, column=0, pady=ENTRY_GRID_PAD_Y, sticky="w")

        entry = ModernEntry(
            parent, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT, placeholder=placeholder,
            font_family=ENTRY_FONT_FAMILY, font_size=ENTRY_FONT_SIZE, 
            fixed_size=fixed_size, max_length=max_length)
        entry.grid(row=row, column=1, padx=ENTRY_GRID_PAD_X, pady=ENTRY_GRID_PAD_Y, sticky="nw")
        
        parent.columnconfigure(1, weight=1)
        return entry

    def _create_buttons(self, parent):
        """创建按钮区域"""
        button_frame = tk.Frame(parent, bg=BG_COLOR)
        button_frame.pack(fill="x", pady=BUTTON_PAD_Y)

        # 提交按钮
        submit_btn = tk.Button(
            button_frame, text="Submit", font=("Segoe UI", 10, "bold"),
            bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR, activebackground=BUTTON_ACTIVE_BG,
            activeforeground=BUTTON_ACTIVE_FG, relief="flat", padx=20, pady=6,
            command=self.submit_form)
        submit_btn.pack(side="right", padx=BUTTON_PAD_X)

        # 清除按钮
        clear_btn = tk.Button(
            button_frame, text="Clear All", font=("Segoe UI", 10),
            bg=BUTTON_SECONDARY_BG, fg=BUTTON_SECONDARY_FG, activebackground=BUTTON_SECONDARY_ACTIVE_BG,
            activeforeground=BUTTON_ACTIVE_FG, relief="flat", padx=20, pady=6,
            command=self.clear_form)
        clear_btn.pack(side="right")
        
        # 复制按钮
        copy_btn = tk.Button(
            button_frame, text="Copy Selected", font=("Segoe UI", 10),
            bg=BUTTON_SECONDARY_BG, fg=BUTTON_SECONDARY_FG, activebackground=BUTTON_SECONDARY_ACTIVE_BG,
            activeforeground=BUTTON_ACTIVE_FG, relief="flat", padx=20, pady=6,
            command=self.copy_selected)
        copy_btn.pack(side="left")

    def _on_root_click(self, event):
        """根窗口点击事件处理"""
        if isinstance(event.widget, ModernEntry):
            return
        self.root.focus_set()

    def submit_form(self):
        """提交表单"""
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
            self.root, text="✓ Form submitted successfully!",
            font=("Segoe UI", 10), fg=SUCCESS_COLOR, bg=BG_COLOR)
        success.place(relx=0.5, rely=0.92, anchor="center")
        self.root.after(SUCCESS_MESSAGE_DURATION, success.destroy)

    def clear_form(self):
        """清除表单"""
        self.entry_0.set("")
        self.entry_1.set("")
        self.entry_2.set("")
        self.root.focus_set()
        
    def copy_selected(self):
        """复制选中的文本"""
        # 尝试从当前焦点输入框复制
        focus = self.root.focus_get()
        if isinstance(focus, ModernEntry):
            selected_text = focus.get_selected_text()
            if selected_text:
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
                # 显示复制成功消息
                success = tk.Label(
                    self.root, text="✓ Copied to clipboard!",
                    font=("Segoe UI", 9), fg=SUCCESS_COLOR, bg=BG_COLOR)
                success.place(relx=0.5, rely=0.85, anchor="center")
                self.root.after(SUCCESS_MESSAGE_DURATION, success.destroy)

if __name__ == "__main__":
    root = tk.Tk()
    app = DemoApp(root)
    root.mainloop()