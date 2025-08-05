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
        
        # 颜色配置
        self.button_color = button_color
        self.hover_color = hover_color
        self.press_color = press_color
        self.text_color = text_color
        self.outline_color = outline_color
        
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
        try:
            self.itemconfig(self.btn_id, fill=self.hover_color)
        except tk.TclError:
            pass
    
    def _on_leave(self, event=None):
        """鼠标离开效果"""
        try:
            self.itemconfig(self.btn_id, fill=self.button_color)
        except tk.TclError:
            pass
    
    def _on_press(self, event=None):
        """鼠标按下效果"""
        try:
            self.itemconfig(self.btn_id, fill=self.press_color)
        except tk.TclError:
            pass
    
    def _on_release(self, event=None):
        """鼠标释放并执行命令"""
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
        """配置按钮属性"""
        try:
            # 处理文本配置
            if 'text' in kwargs:
                self.itemconfig(self.text_id, text=kwargs['text'])
                
            # 处理命令配置
            if 'command' in kwargs:
                self.command = kwargs['command']
            
            # 处理字体配置
            font_changed = False
            if 'font_family' in kwargs or 'font_size' in kwargs or 'font_weight' in kwargs:
                family, size, weight = self.font_config
                if 'font_family' in kwargs:
                    family = kwargs['font_family']
                if 'font_size' in kwargs:
                    size = kwargs['font_size']
                if 'font_weight' in kwargs:
                    weight = kwargs['font_weight']
                self.font_config = (family, size, weight)
                self.itemconfig(self.text_id, font=self.font_config)
                font_changed = True
            
            # 处理颜色配置
            color_changed = False
            color_keys = ['button_color', 'hover_color', 'press_color', 'text_color', 'outline_color']
            for key in color_keys:
                if key in kwargs:
                    setattr(self, key, kwargs[key])
                    color_changed = True
            
            # 如果文本颜色改变，立即更新
            if 'text_color' in kwargs:
                self.itemconfig(self.text_id, fill=self.text_color)
            
            # 如果按钮或边框颜色改变，重绘按钮背景
            if color_changed and ('button_color' in kwargs or 'outline_color' in kwargs):
                self.delete(self.btn_id)
                self.btn_id = self._draw_rounded_rect(
                    1, 1, self.width-1, self.height-1,
                    fill=self.button_color,
                    outline=self.outline_color
                )
                # 确保文字在最上层
                self.tag_raise(self.text_id)
                
        except tk.TclError:
            # 处理窗口已销毁的情况
            pass
    
    def destroy(self):
        """清理资源"""
        try:
            super().destroy()
        except tk.TclError:
            pass