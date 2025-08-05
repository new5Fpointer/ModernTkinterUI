# button.py - 修复版本
import tkinter as tk
import math
import tkinter.font as tkfont

class RoundedButton(tk.Canvas):
    """自定义圆角按钮控件"""
    def __init__(self, master, text, command=None, width=60, height=25, radius=4,
                 bg_color="#1e1e1e", button_color="#252525", hover_color="#353535",
                 press_color="#1e1e1e", text_color="#e0e0e0", outline_color="#404040",
                 font_family="default", font_size=9, font_weight="normal"):
        super().__init__(master, width=width, height=height, 
                        highlightthickness=0, bd=0, bg=bg_color)
        self.command = command
        self.radius = radius
        
        # 保存原始尺寸
        self.width = width
        self.height = height

        # 禁用配置
        self.enabled = True           # 当前是否可用
        self.disabled_color = "#353535"   # 禁用时的面板色
        self.disabled_text_color = "#808080"  # 禁用时的文字色
        
        # 颜色配置
        self.button_color = button_color
        self.hover_color = hover_color
        self.press_color = press_color
        self.text_color = text_color
        self.outline_color = outline_color
        self._current_fill = self.button_color
        
        # 字体处理
        if font_family == "default":
            # 使用正确的导入方式获取默认字体
            default_font = tkfont.nametofont("TkDefaultFont")
            font_family = default_font.actual()["family"]
        
        self.font_config = (font_family, font_size, font_weight)
        
        # 绘制圆角按钮
        self.btn_id = self._draw_rounded_rect(
            1, 1, width-1, height-1, 
            fill=self.button_color,
            outline=self.outline_color
        )
        
        # 添加按钮文字 - 保存文字ID
        self.text_id = self.create_text(
            width//2, height//2,
            text=text,
            fill=self.text_color,
            font=self.font_config
        )
        
        # 事件绑定
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
    
    def _on_enter(self, event=None):
        """鼠标悬停效果"""
        if not self.enabled:
            return
        try:
            self.itemconfig(self.btn_id, fill=self.hover_color)
        except tk.TclError:
            pass
    
    def _on_leave(self, event=None):
        """鼠标离开效果"""
        try:
            self._refresh_appearance() 
        except tk.TclError:
            pass
    
    def _on_press(self, event=None):
        """鼠标按下效果"""
        if not self.enabled:
            return
        try:
            self.itemconfig(self.btn_id, fill=self.press_color)
        except tk.TclError:
            pass
    
    def _on_release(self, event=None):
        """鼠标释放并执行命令"""
        if not self.enabled:
            return
        try:
            self.itemconfig(self.btn_id, fill=self.hover_color)
            if self.command:
                self.command()
        except tk.TclError:
            pass
    
    def _draw_rounded_rect(self, x1, y1, x2, y2, **kwargs):
        """绘制圆角矩形"""
        radius = self.radius
        points = []
        top = y1 + radius
        bottom = y2 - radius
        left = x1 + radius
        right = x2 - radius
        
        # 绘制路径
        points.extend([x1, top])
        points.extend(self._get_arc_points(left, top, radius, math.pi, math.pi*1.5))
        points.extend([right, y1])
        points.extend(self._get_arc_points(right, top, radius, math.pi*1.5, math.pi*2))
        points.extend([x2, bottom])
        points.extend(self._get_arc_points(right, bottom, radius, 0, math.pi*0.5))
        points.extend([left, y2])
        points.extend(self._get_arc_points(left, bottom, radius, math.pi*0.5, math.pi))
        points.extend([x1, top])
        
        return self.create_polygon(points, **kwargs, smooth=True)
    
    def _get_arc_points(self, cx, cy, radius, start_angle, end_angle, segments=8):
        """生成圆弧点集"""
        points = []
        for i in range(segments + 1):
            angle = start_angle + (end_angle - start_angle) * i / segments
            points.extend([cx + radius * math.cos(angle), cy + radius * math.sin(angle)])
        return points

    def configure(self, **kwargs):
        """配置按钮属性（含 state / disabled_color）"""
        try:
            # 1. 文本
            if 'text' in kwargs:
                self.itemconfig(self.text_id, text=kwargs['text'])

            # 2. 命令
            if 'command' in kwargs:
                self.command = kwargs['command']

            # 3. 字体
            font_changed = False
            if any(k in kwargs for k in ('font_family', 'font_size', 'font_weight')):
                family, size, weight = self.font_config
                family = kwargs.pop('font_family', family)
                size   = kwargs.pop('font_size',   size)
                weight = kwargs.pop('font_weight', weight)
                self.font_config = (family, size, weight)
                self.itemconfig(self.text_id, font=self.font_config)

            # 4. 禁用色
            if 'disabled_color' in kwargs:
                self.disabled_color = kwargs.pop('disabled_color')
                self._refresh_appearance()
            if 'disabled_text_color' in kwargs:
                self.disabled_text_color = kwargs.pop('disabled_text_color')
                self._refresh_appearance()

            # 5. 状态
            if 'state' in kwargs:
                state = kwargs.pop('state')
                self.set_enabled(state == 'normal')

            # 6. 其余颜色（button_color / hover_color / outline_color / text_color）
            color_changed = False
            color_keys = ['button_color', 'hover_color', 'press_color', 'text_color', 'outline_color']
            for key in color_keys:
                if key in kwargs:
                    setattr(self, key, kwargs[key])
                    color_changed = True

            if color_changed:
                # 如果当前禁用，仍保持 disabled_color；否则用新 button_color
                current_fill = (self.disabled_color if not self.enabled
                                else self.button_color)
                self.delete(self.btn_id)
                self.btn_id = self._draw_rounded_rect(
                    1, 1, self.width-1, self.height-1,
                    fill=current_fill,
                    outline=self.outline_color
                )
                if 'text_color' in kwargs:
                    self.itemconfig(self.text_id, fill=self.text_color)
                self.tag_raise(self.text_id)

        except tk.TclError:
            pass   # 窗口已销毁
    
    def destroy(self):
        """清理资源"""
        try:
            super().destroy()
        except tk.TclError:
            pass
    
    def set_enabled(self, flag=True):
        """True=启用 False=禁用"""
        self.enabled = bool(flag)
        self._refresh_appearance()


    def _refresh_appearance(self):
        """刷新按钮和文字的颜色"""
        if self.enabled:
            fill_color      = self.button_color
            text_fill_color = self.text_color
        else:
            fill_color      = self.disabled_color
            text_fill_color = self.disabled_text_color

        try:
            self.itemconfig(self.btn_id,  fill=fill_color)
            self.itemconfig(self.text_id, fill=text_fill_color)
        except tk.TclError:
            pass