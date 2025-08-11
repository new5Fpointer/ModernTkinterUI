# ModernEntry.py
import tkinter as tk
import tkinter.font as tkfont

# ====================== 常量定义 ======================
DEFAULT_WIDTH = 240
DEFAULT_HEIGHT = 36
DEFAULT_RADIUS = 8
DEFAULT_CURSOR_HEIGHT = 18
DEFAULT_CURSOR_BLINK_SPEED = 450
SELECTION_HEIGHT_OFFSET = -3
ENTRY_FONT_SIZE = 12
TEXT_PADDING_X = 12
MIN_CURSOR_HEIGHT = 14
CURSOR_VERTICAL_OFFSET_REDUCTION = 4
MAX_TEXT_LENGTH = 1000

BG_COLOR = "#1e1e1e"
ENTRY_BG_COLOR = "#2d2d2d"
BORDER_NORMAL_COLOR = "#444444"
BORDER_FOCUS_COLOR = "#4ec9b0"
TEXT_COLOR = "#e0e0e0"
PLACEHOLDER_COLOR = "#888888"
CURSOR_COLOR = "#6bd8c9"
SELECTION_COLOR = "#348b81"
ENTRY_FONT_FAMILY = "dengxian"

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

# ====================== ModernEntry ======================
class ModernEntry(tk.Canvas):
    """现代风格的输入框组件"""
    _active_cursor = None
    _first_entry = None

    def _rounded_rect_pts(self, x1, y1, x2, y2, r):
        return [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
            x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1
        ]

    def _redraw_rect(self, w, h, focus=False):
        """无条件重绘：背景和边框都重新画"""
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
            pts, fill="", outline=self.border_focus if self.focus_get() == self else self.border_normal,
            smooth=True, width=1)

        self.tag_raise(self.text_id)
        if hasattr(self, 'cursor') and self.cursor:
            self.tag_raise(self.cursor.cursor_id)

    def __init__(self, master, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT,
                 radius=DEFAULT_RADIUS, bg_color=ENTRY_BG_COLOR,
                 border_normal=BORDER_NORMAL_COLOR, border_focus=BORDER_FOCUS_COLOR,
                 text_color=TEXT_COLOR, placeholder="", placeholder_color=PLACEHOLDER_COLOR,
                 font_family=ENTRY_FONT_FAMILY, font_size=ENTRY_FONT_SIZE,
                 fixed_size=True, max_length=MAX_TEXT_LENGTH, **kwargs):
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
        self._cursor_height = DEFAULT_CURSOR_HEIGHT
        self._radius = radius
        self._text_left = 0
        self.fixed_size = fixed_size
        self._original_border_focus = border_focus
        self._current_border_focus = border_focus
        if max_length is not None and max_length < 1:
            raise ValueError("max_length must be at least 1 or None for no limit")
        self.max_length = max_length
        font_height = self._font.metrics("linespace")
        self.text_x = TEXT_PADDING_X
        self.text_y = (height - font_height) // 2
        self.cursor_y_offset = max(0, (font_height - self._cursor_height) // 2)
        self.text_id = self.create_text(
            self.text_x, self.text_y,
            text=placeholder, anchor="nw", fill=placeholder_color, font=self._font)
        self._redraw_rect(width, height)
        self.cursor = None
        self._select_start = None
        self._dragging_select = False
        self._selection_rect = None
        self._selection_rects = []
        self._bind_events()
        if ModernEntry._first_entry is None:
            ModernEntry._first_entry = self
        self._bind_root_tab()
        self.tag_raise(self.text_id)

    def _bind_events(self):
        self.bind("<Button-1>", self._on_click)
        self.bind("<Key>", self._on_key_press)
        self.bind("<BackSpace>", self._on_key_press)
        self.bind("<Delete>", self._on_key_press)
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
        self.bind("<Tab>", self._on_tab)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Control-v>", self._on_paste)
        self.bind("<Control-V>", self._on_paste)
        self.bind("<Control-c>", self._on_copy)
        self.bind("<Control-C>", self._on_copy)
        self.bind("<Control-a>", self._select_all)
        self.bind("<Control-A>", self._select_all)
        if self.fixed_size:
            self.bind("<Configure>", lambda e: "break")
        else:
            self.bind("<Configure>", self._on_resize)

    def _bind_root_tab(self):
        root = self.winfo_toplevel()
        if getattr(root, "_modern_tab_bound", None):
            return
        root._modern_tab_bound = True
        def _global_tab(event):
            focus = event.widget.focus_get()
            if isinstance(focus, ModernEntry):
                return None
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

    def _normalize_selection(self):
        if self._select_start is None:
            return None, None
        start = min(self._select_start, self._cursor_pos)
        end = max(self._select_start, self._cursor_pos)
        return start, end

    def insert(self, idx, txt):
        if self.max_length is not None:
            current_length = len(self._text)
            remaining = self.max_length - current_length
            if remaining <= 0:
                return
            if len(txt) > remaining:
                txt = txt[:remaining]
        idx = self._fix_index(idx)
        self._text = self._text[:idx] + txt + self._text[idx:]
        self._cursor_pos = idx + len(txt)
        self._refresh_text_and_cursor()
        self._select_start = None
        self._clear_selection()

    def delete(self, first, last=None):
        start, end = self._normalize_selection()
        if start is not None and end is not None:
            self._text = self._text[:start] + self._text[end:]
            self._cursor_pos = start
            self._select_start = None
            for rect in self._selection_rects:
                super().delete(rect)
            self._selection_rects = []
            self._refresh_text_and_cursor()
            return
        first = self._fix_index(first)
        last = first + 1 if last is None else self._fix_index(last)
        if first > last:
            first, last = last, first
        self._text = self._text[:first] + self._text[last:]
        self._cursor_pos = first
        self._refresh_text_and_cursor()
        self._select_start = None
        self._clear_selection()

    def set(self, text):
        if self.max_length is not None and len(text) > self.max_length:
            text = text[:self.max_length]
        self._text = text
        self._cursor_pos = len(text)
        self._text_left = 0
        self.coords(self.text_id, self.text_x, self.text_y)
        self.itemconfig(self.text_id, text=text or self.placeholder,
                        fill=self.text_color if text else self.placeholder_color)
        if self.cursor is None:
            self._create_cursor()
            self.cursor.hide()
        self._scroll_to_cursor()
        self._select_start = None
        self._clear_selection()

    def get(self):
        return self._text

    def get_selected_text(self):
        start, end = self._normalize_selection()
        if start is None or end is None or start == end:
            return ""
        return self._text[start:end]

    def _refresh_text_and_cursor(self):
        show_text = self._text if self._text else self.placeholder
        show_color = self.text_color if self._text else self.placeholder_color
        self.itemconfig(self.text_id, text=show_text, fill=show_color)
        if self.max_length is not None and len(self._text) >= self.max_length:
            new_color = "#ff4d4d"
        else:
            new_color = self._original_border_focus
        if new_color != self._current_border_focus:
            self._current_border_focus = new_color
            if self is self.focus_displayof():
                self._redraw_rect(self.winfo_width(), self.winfo_height(), focus=True)
        self._update_cursor()
        self._scroll_to_cursor()
        self._update_selection_visual()

    def _clear_selection(self):
        for rect in self._selection_rects:
            super().delete(rect)
        self._selection_rects = []
        self._selection_rect = None

    def _update_selection_visual(self):
        for rect in self._selection_rects:
            super().delete(rect)
        self._selection_rects = []
        if self._select_start is None or self._select_start == self._cursor_pos:
            return
        start, end = self._normalize_selection()
        start_x = self._font.measure(self._text[:start]) + self.text_x + self._text_left
        end_x = self._font.measure(self._text[:end]) + self.text_x + self._text_left
        font_height = self._font.metrics("linespace")
        sel_height = font_height + SELECTION_HEIGHT_OFFSET
        offset_y = (font_height - sel_height) // 2
        y1 = self.text_y + offset_y
        y2 = y1 + sel_height
        rect = self.create_rectangle(start_x, y1, end_x, y2,
                                     fill=SELECTION_COLOR, outline="", width=0)
        self._selection_rects.append(rect)
        self.tag_lower(rect, self.text_id)
        self.tag_raise(self.text_id)
        if self.cursor:
            self.tag_raise(self.cursor.cursor_id)

    def _create_cursor(self):
        if self.cursor is None:
            self.cursor = PureCursor(
                self, x=self.text_x, y=self.text_y + self.cursor_y_offset,
                height=self._cursor_height, width=2, color=CURSOR_COLOR,
                blink_speed=DEFAULT_CURSOR_BLINK_SPEED)
            self.cursor.stop_blinking()
            self.cursor.hide()

    def _update_cursor(self):
        if self.cursor is None:
            self._create_cursor()
        substr = self._text[:self._cursor_pos]
        cursor_x = self.text_x + self._font.measure(substr) + self._text_left
        cursor_y = self.text_y + self.cursor_y_offset
        print("光标坐标 -> x:", cursor_x, "y:", cursor_y)
        self.cursor.move(cursor_x, cursor_y)

    def _on_click(self, event):
        if self.cursor is None:
            self._create_cursor()
        new_pos = self._get_char_index_at_x(event.x)
        new_pos = max(0, min(new_pos, len(self._text)))
        if new_pos != self._cursor_pos:
            self._cursor_pos = new_pos
            self._update_cursor()
            self._scroll_to_cursor()
        if not self._dragging_select:
            self._select_start = None
            self._clear_selection()
        self._select_start = self._cursor_pos
        self._dragging_select = True
        self.focus_set()

    def _on_drag(self, event):
        if not self._dragging_select:
            return
        new_pos = self._get_char_index_at_x(event.x)
        if new_pos != self._cursor_pos:
            self._cursor_pos = new_pos
            self._update_cursor()
            self._scroll_to_cursor()
            self._update_selection_visual()

    def _on_release(self, event):
        self._dragging_select = False
        if self._select_start == self._cursor_pos:
            self._select_start = None
            self._clear_selection()

    def _on_key_press(self, event):
        if self.cursor is None:
            self._create_cursor()
        first_key_after_focus_in = (self._cursor_pos == 0 and self._text_left == 0)
        keysym = event.keysym
        shift_pressed = (event.state & 0x0001) != 0

        def _keep_cursor_fixed():
            current_cursor_x = self.text_x + self._font.measure(self._text[:self._cursor_pos]) + self._text_left
            new_cursor_x = self.text_x + self._font.measure(self._text[:self._cursor_pos]) + self._text_left
            delta = new_cursor_x - current_cursor_x
            self._text_left -= delta
            max_left = 0
            min_left = min(0, self.winfo_width() - 2 * self.text_x - self._font.measure(self._text))
            self._text_left = max(min_left, min(max_left, self._text_left))

        if keysym == "BackSpace":
            start, end = self._normalize_selection()
            if start is not None and end is not None:
                self._text = self._text[:start] + self._text[end:]
                self._cursor_pos = start
                self._select_start = None
                self._clear_selection()
                self._refresh_text_and_cursor()
                return
            if self._cursor_pos > 0:
                self._text = self._text[:self._cursor_pos - 1] + self._text[self._cursor_pos:]
                self._cursor_pos -= 1
                if not first_key_after_focus_in:
                    _keep_cursor_fixed()
        elif keysym == "Delete":
            start, end = self._normalize_selection()
            if start is not None and end is not None:
                self._text = self._text[:start] + self._text[end:]
                self._cursor_pos = start
                self._select_start = None
                self._clear_selection()
                self._refresh_text_and_cursor()
                return
            if self._cursor_pos < len(self._text):
                self._text = self._text[:self._cursor_pos] + self._text[self._cursor_pos + 1:]
                if not first_key_after_focus_in:
                    _keep_cursor_fixed()
        elif keysym == "Left":
            if shift_pressed:
                if self._select_start is None:
                    self._select_start = self._cursor_pos
                self._cursor_pos = max(0, self._cursor_pos - 1)
            else:
                self._select_start = None
                self._clear_selection()
                self._cursor_pos = max(0, self._cursor_pos - 1)
        elif keysym == "Right":
            if shift_pressed:
                if self._select_start is None:
                    self._select_start = self._cursor_pos
                self._cursor_pos = min(len(self._text), self._cursor_pos + 1)
            else:
                self._select_start = None
                self._clear_selection()
                self._cursor_pos = min(len(self._text), self._cursor_pos + 1)
        elif keysym == "Home":
            if shift_pressed:
                if self._select_start is None:
                    self._select_start = self._cursor_pos
                self._cursor_pos = 0
            else:
                self._select_start = None
                self._clear_selection()
                self._cursor_pos = 0
        elif keysym == "End":
            if shift_pressed:
                if self._select_start is None:
                    self._select_start = self._cursor_pos
                self._cursor_pos = len(self._text)
            else:
                self._select_start = None
                self._clear_selection()
                self._cursor_pos = len(self._text)
        elif event.char and event.char.isprintable():
            if self.max_length is not None and len(self._text) >= self.max_length:
                return
            if self._select_start is not None and self._select_start != self._cursor_pos:
                start, end = self._normalize_selection()
                self._text = self._text[:start] + self._text[end:]
                self._cursor_pos = start
                self._select_start = None
                self._clear_selection()
            self._text = self._text[:self._cursor_pos] + event.char + self._text[self._cursor_pos:]
            self._cursor_pos += 1
            if not first_key_after_focus_in:
                _keep_cursor_fixed()
        else:
            return
        self._refresh_text_and_cursor()
        self._scroll_to_cursor()

    def _on_copy(self, event):
        selected_text = self.get_selected_text()
        if selected_text:
            self.clipboard_clear()
            self.clipboard_append(selected_text)
        return "break"

    def _select_all(self, event):
        self._select_start = 0
        self._cursor_pos = len(self._text)
        self._refresh_text_and_cursor()
        return "break"

    def _on_paste(self, event):
        try:
            clipboard_text = self.clipboard_get()
        except tk.TclError:
            return
        if not clipboard_text:
            return
        clipboard_text = clipboard_text.replace('\n', ' ').replace('\r', '')
        if self.max_length is not None:
            current_length = len(self._text)
            remaining = self.max_length - current_length
            if remaining <= 0:
                return
            if len(clipboard_text) > remaining:
                clipboard_text = clipboard_text[:remaining]
        if self._select_start is not None and self._select_start != self._cursor_pos:
            start, end = self._normalize_selection()
            self._text = self._text[:start] + self._text[end:]
            self._cursor_pos = start
            self._select_start = None
            self._clear_selection()
        self.insert(self._cursor_pos, clipboard_text)
        return "break"

    def _on_focus_in(self, event=None):
        if self.cursor is None:
            self._create_cursor()
        if ModernEntry._active_cursor and ModernEntry._active_cursor != self:
            ModernEntry._active_cursor.cursor.stop_blinking()
            ModernEntry._active_cursor.cursor.hide()
            ModernEntry._active_cursor._select_start = None
            ModernEntry._active_cursor._clear_selection()
        ModernEntry._active_cursor = self
        self.cursor.show()
        self.cursor.start_blinking()
        self._redraw_rect(self.winfo_width(), self.winfo_height(), focus=True)
        self._update_selection_visual()

    def _on_focus_out(self, event=None):
        if ModernEntry._active_cursor == self:
            if self.cursor:
                self.cursor.stop_blinking()
                self.cursor.hide()
            ModernEntry._active_cursor = None
        self._cursor_pos = 0
        self._text_left = 0
        self.coords(self.text_id, self.text_x, self.text_y)
        if self.cursor is None:
            self._create_cursor()
        cursor_x = self.text_x + self._font.measure(self._text[:self._cursor_pos]) + self._text_left
        cursor_y = self.text_y + self.cursor_y_offset
        self.cursor.move(cursor_x, cursor_y)
        self._redraw_rect(self.winfo_width(), self.winfo_height(), focus=False)
        self._select_start = None
        self._clear_selection()

    def _on_tab(self, event):
        pass

    def _get_char_index_at_x(self, x):
        click_x_text = x - (self.text_x + self._text_left)
        if not self._text:
            return 0
        left, right = 0, len(self._text)
        while left < right:
            mid = (left + right) // 2
            substr_width = self._font.measure(self._text[:mid])
            if substr_width <= click_x_text:
                left = mid + 1
            else:
                right = mid
        if left > 0:
            prev_width = self._font.measure(self._text[:left-1])
            curr_width = self._font.measure(self._text[:left])
            if abs(click_x_text - prev_width) < abs(click_x_text - curr_width):
                return left - 1
        return left

    def _scroll_to_cursor(self):
        if not self._text:
            self._text_left = 0
            self.coords(self.text_id, self.text_x, self.text_y)
            if self.cursor:
                self._update_cursor()
            return
        cursor_rel_x = self._font.measure(self._text[:self._cursor_pos])
        visible_w = self.winfo_width() - 2 * self.text_x
        text_width = self._font.measure(self._text)
        cursor_width = self.cursor.width if self.cursor else 1
        if text_width <= visible_w:
            self._text_left = 0
        else:
            cursor_left = cursor_rel_x + self._text_left
            cursor_right = cursor_left + cursor_width
            if cursor_left < 0:
                self._text_left = -cursor_rel_x
            elif cursor_right > visible_w:
                self._text_left = -(cursor_rel_x + cursor_width - visible_w)
            min_left = min(0, visible_w - text_width)
            max_left = 0
            self._text_left = max(min_left, min(max_left, self._text_left))
        self.coords(self.text_id, self.text_x + self._text_left, self.text_y)
        self._update_cursor()
        self._update_selection_visual()
        
    def _on_resize(self, event):
        if self.fixed_size:
            return

        w, h = event.width, event.height

        self._redraw_rect(w, h, focus=(self.focus_get() == self))
        font_height = self._font.metrics("linespace")
        self.text_y = (h - font_height) // 2
        cursor_h = max(MIN_CURSOR_HEIGHT, font_height - CURSOR_VERTICAL_OFFSET_REDUCTION)
        if self.cursor:
            self.cursor.set_height(cursor_h)

        text_width = self._font.measure(self._text)
        visible_w = w - 2 * self.text_x
        self._text_left = visible_w - text_width if text_width > visible_w else 0

        self._cursor_pos = len(self._text)
        self.coords(self.text_id, self.text_x + self._text_left, self.text_y)
        self._update_cursor()