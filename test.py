import tkinter as tk
from tkinter import ttk
from button import RoundedButton
from ModernEntry import ModernEntry

class CustomWidgetsTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("自定义控件测试")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e1e")

        # 提前定义状态变量和方法
        self.status_var = tk.StringVar(value="就绪")
        self.update_status = lambda message: (
            self.status_var.set(message),
            self.root.after(3000, lambda: self.status_var.set("就绪"))
        )

        # 创建样式
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#1e1e1e")
        self.style.configure("Header.TLabel", background="#1e1e1e", foreground="#e0e0e0", font=("Arial", 12, "bold"))
        self.style.configure("Status.TLabel", background="#1e1e1e", foreground="#888888", font=("Arial", 9))

        # 创建主框架
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 创建标签页
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 创建按钮测试标签页
        self.create_button_tab()

        # 创建输入框测试标签页
        self.create_entry_tab()

        # 创建组合测试标签页
        self.create_combination_tab()

        # 状态栏
        status_bar = ttk.Label(root, textvariable=self.status_var, style="Status.TLabel")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    def create_button_tab(self):
        """创建按钮测试标签页"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="圆角按钮测试")
        
        # 创建按钮测试区域
        button_frame = ttk.Frame(tab)
        button_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # 标题
        header = ttk.Label(button_frame, text="RoundedButton 控件测试", style="Header.TLabel")
        header.pack(pady=(0, 15))
        
        # 普通按钮
        self.create_button_section(button_frame, "基本按钮")
        
        # 不同样式的按钮
        self.create_button_section(button_frame, "不同样式的按钮", 
                                   button_color="#3a7ca5", hover_color="#5fa8d3", 
                                   press_color="#2a5a7a", text_color="#ffffff", 
                                   outline_color="#1c4b6e")
        
        # 不同尺寸的按钮
        self.create_button_section(button_frame, "不同尺寸的按钮", 
                                   width=100, height=40, radius=10, 
                                   font_size=12)
        
        # 禁用状态按钮
        self.create_disabled_button_section(button_frame)
    
    def create_button_section(self, parent, title, **kwargs):
        """创建按钮测试部分"""
        section_frame = ttk.Frame(parent)
        section_frame.pack(fill=tk.X, pady=10)
        
        # 部分标题
        section_label = ttk.Label(section_frame, text=title, style="Status.TLabel")
        section_label.pack(anchor=tk.W, padx=5)
        
        # 按钮容器
        button_container = ttk.Frame(section_frame)
        button_container.pack(fill=tk.X, pady=5)
        
        # 创建按钮
        btn1 = RoundedButton(
            button_container, text="按钮1", 
            command=lambda: self.update_status(f"点击了 {title} 的按钮1"),
            **kwargs
        )
        btn1.pack(side=tk.LEFT, padx=5)
        
        btn2 = RoundedButton(
            button_container, text="按钮2", 
            command=lambda: self.update_status(f"点击了 {title} 的按钮2"),
            **kwargs
        )
        btn2.pack(side=tk.LEFT, padx=5)
        
        btn3 = RoundedButton(
            button_container, text="按钮3", 
            command=lambda: self.update_status(f"点击了 {title} 的按钮3"),
            **kwargs
        )
        btn3.pack(side=tk.LEFT, padx=5)
        
        # 动态修改按钮
        change_btn = RoundedButton(
            button_container, text="修改按钮", 
            command=lambda: self.change_button_properties(btn1, btn2, btn3),
            width=80, height=25,
            button_color="#5d5d5d", hover_color="#6d6d6d", press_color="#4d4d4d"
        )
        change_btn.pack(side=tk.RIGHT, padx=5)
    
    def create_disabled_button_section(self, parent):
        """创建禁用按钮测试部分"""
        section_frame = ttk.Frame(parent)
        section_frame.pack(fill=tk.X, pady=10)
        
        # 部分标题
        section_label = ttk.Label(section_frame, text="禁用状态按钮", style="Status.TLabel")
        section_label.pack(anchor=tk.W, padx=5)
        
        # 按钮容器
        button_container = ttk.Frame(section_frame)
        button_container.pack(fill=tk.X, pady=5)
        
        # 创建按钮
        self.disabled_btn1 = RoundedButton(
            button_container, text="禁用按钮1", 
            command=lambda: self.update_status("点击了禁用按钮1"),
            button_color="#ff6b6b", hover_color="#ff8e8e", press_color="#e05a5a"
        )
        self.disabled_btn1.pack(side=tk.LEFT, padx=5)
        
        self.disabled_btn2 = RoundedButton(
            button_container, text="禁用按钮2", 
            command=lambda: self.update_status("点击了禁用按钮2"),
            button_color="#4ec9b0", hover_color="#6bd8c9", press_color="#3aa897"
        )
        self.disabled_btn2.pack(side=tk.LEFT, padx=5)
        
        # 禁用/启用切换按钮
        toggle_btn = RoundedButton(
            button_container, text="切换禁用状态", 
            command=self.toggle_disabled_buttons,
            width=100, height=25,
            button_color="#5d5d5d", hover_color="#6d6d6d", press_color="#4d4d4d"
        )
        toggle_btn.pack(side=tk.RIGHT, padx=5)
        
        # 初始状态
        self.disable_buttons()
    
    def change_button_properties(self, *buttons):
        """动态修改按钮属性"""
        for i, btn in enumerate(buttons):
            colors = [
                ("#ff6b6b", "#ff8e8e", "#e05a5a", "#ffffff"),  # 红色
                ("#4ec9b0", "#6bd8c9", "#3aa897", "#ffffff"),  # 青色
                ("#d7ba7d", "#e8d4a8", "#c0a566", "#ffffff")   # 黄色
            ]
            color_set = colors[i % len(colors)]
            
            btn.configure(
                button_color=color_set[0],
                hover_color=color_set[1],
                press_color=color_set[2],
                text_color=color_set[3],
                text=f"修改{i+1}"
            )
        
        self.update_status("按钮属性已修改")
    
    def disable_buttons(self):
        """禁用按钮"""
        self.disabled_btn1.set_enabled(False)
        self.disabled_btn2.set_enabled(False)
        self.update_status("按钮已禁用")
    
    def enable_buttons(self):
        """启用按钮"""
        self.disabled_btn1.set_enabled(True)
        self.disabled_btn2.set_enabled(True)
        self.update_status("按钮已启用")
    
    def toggle_disabled_buttons(self):
        """切换按钮禁用状态"""
        if self.disabled_btn1.enabled:
            self.disable_buttons()
        else:
            self.enable_buttons()
    
    def create_entry_tab(self):
        """创建输入框测试标签页"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="现代输入框测试")
        
        # 创建输入框测试区域
        entry_frame = ttk.Frame(tab)
        entry_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # 标题
        header = ttk.Label(entry_frame, text="ModernEntry 控件测试", style="Header.TLabel")
        header.pack(pady=(0, 15))
        
        # 基本输入框
        self.create_entry_section(entry_frame, "基本输入框", placeholder="在此输入...")
        
        # 带最大长度的输入框
        self.create_entry_section(entry_frame, "带最大长度的输入框 (10字符)", 
                                 placeholder="最多输入10字符...", max_length=10)
        
        # 不同样式的输入框
        self.create_entry_section(entry_frame, "不同样式的输入框", 
                                 bg_color="#3a3a3a", border_normal="#ff6b6b", 
                                 border_focus="#ff8e8e", text_color="#ffffff",
                                 placeholder="红色边框...")
        
        # 不同尺寸的输入框
        self.create_entry_section(entry_frame, "不同尺寸的输入框", 
                                 width=300, height=40, radius=12,
                                 placeholder="宽300高40...")
    
    def create_entry_section(self, parent, title, **kwargs):
        """创建输入框测试部分"""
        section_frame = ttk.Frame(parent)
        section_frame.pack(fill=tk.X, pady=10)
        
        # 部分标题
        section_label = ttk.Label(section_frame, text=title, style="Status.TLabel")
        section_label.pack(anchor=tk.W, padx=5)
        
        # 输入框容器
        entry_container = ttk.Frame(section_frame)
        entry_container.pack(fill=tk.X, pady=5)
        
        # 创建输入框
        entry = ModernEntry(entry_container, **kwargs)
        entry.pack(fill=tk.X, padx=5, pady=5)
        
        # 功能按钮
        btn_frame = ttk.Frame(entry_container)
        btn_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        get_btn = RoundedButton(
            btn_frame, text="获取内容", 
            command=lambda: self.show_entry_content(entry),
            width=80, height=25
        )
        get_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = RoundedButton(
            btn_frame, text="清空内容", 
            command=lambda: self.clear_entry(entry),
            width=80, height=25
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        disable_btn = RoundedButton(
            btn_frame, text="禁用/启用", 
            command=lambda: self.toggle_entry_state(entry),
            width=80, height=25
        )
        disable_btn.pack(side=tk.LEFT, padx=5)
    
    def show_entry_content(self, entry):
        """显示输入框内容"""
        content = entry.get()
        self.update_status(f"输入框内容: '{content}'")
    
    def clear_entry(self, entry):
        """清空输入框内容"""
        entry.set("")
        self.update_status("输入框已清空")
    
    def toggle_entry_state(self, entry):
        """切换输入框禁用状态"""
        if entry.cursor and entry.cursor.visible:
            # 当前是启用状态，禁用它
            entry.focus_set()  # 确保先获取焦点再失去焦点
            entry.event_generate("<FocusOut>")
            self.update_status("输入框已禁用")
        else:
            # 当前是禁用状态，启用它
            entry.focus_set()
            entry.event_generate("<FocusIn>")
            self.update_status("输入框已启用")
    
    def create_combination_tab(self):
        """创建组合测试标签页"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="组合测试")
        
        # 创建组合测试区域
        combo_frame = ttk.Frame(tab)
        combo_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # 标题
        header = ttk.Label(combo_frame, text="控件组合测试", style="Header.TLabel")
        header.pack(pady=(0, 15))
        
        # 登录表单
        self.create_login_form(combo_frame)
        
        # 数据展示
        self.create_data_display(combo_frame)
    
    def create_login_form(self, parent):
        """创建登录表单"""
        form_frame = ttk.LabelFrame(parent, text="登录表单")
        form_frame.pack(fill=tk.X, pady=10)
        
        # 用户名
        ttk.Label(form_frame, text="用户名:", style="Status.TLabel").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.username_entry = ModernEntry(form_frame, width=300, placeholder="输入用户名...")
        self.username_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 密码
        ttk.Label(form_frame, text="密码:", style="Status.TLabel").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.password_entry = ModernEntry(form_frame, width=300, placeholder="输入密码...")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 按钮区域
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        login_btn = RoundedButton(
            btn_frame, text="登录", 
            command=self.login_action,
            width=100, height=35,
            button_color="#4ec9b0", hover_color="#6bd8c9", press_color="#3aa897"
        )
        login_btn.pack(side=tk.LEFT, padx=10)
        
        reset_btn = RoundedButton(
            btn_frame, text="重置", 
            command=self.reset_form,
            width=100, height=35,
            button_color="#d7ba7d", hover_color="#e8d4a8", press_color="#c0a566"
        )
        reset_btn.pack(side=tk.LEFT, padx=10)
        
        # 配置列权重
        form_frame.columnconfigure(1, weight=1)
    
    def login_action(self):
        """登录按钮动作"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            self.update_status("用户名和密码不能为空")
            return
        
        self.update_status(f"登录尝试: 用户名='{username}', 密码='{password}'")
    
    def reset_form(self):
        """重置表单"""
        self.username_entry.set("")
        self.password_entry.set("")
        self.update_status("表单已重置")
    
    def create_data_display(self, parent):
        """创建数据展示区域"""
        display_frame = ttk.LabelFrame(parent, text="数据展示")
        display_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 输入区域
        input_frame = ttk.Frame(display_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(input_frame, text="输入数据:", style="Status.TLabel").pack(side=tk.LEFT, padx=5)
        self.data_entry = ModernEntry(input_frame, width=200, placeholder="输入要添加的数据...")
        self.data_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        add_btn = RoundedButton(
            input_frame, text="添加", 
            command=self.add_data_item,
            width=60, height=25
        )
        add_btn.pack(side=tk.LEFT, padx=5)
        
        # 数据显示区域
        self.data_listbox = tk.Listbox(
            display_frame, 
            bg="#2d2d2d", fg="#e0e0e0",
            selectbackground="#4ec9b0", selectforeground="#ffffff",
            bd=0, highlightthickness=0
        )
        self.data_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 操作按钮
        btn_frame = ttk.Frame(display_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        remove_btn = RoundedButton(
            btn_frame, text="删除选中项", 
            command=self.remove_selected_item,
            width=100, height=25,
            button_color="#ff6b6b", hover_color="#ff8e8e", press_color="#e05a5a"
        )
        remove_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = RoundedButton(
            btn_frame, text="清空列表", 
            command=self.clear_data_list,
            width=80, height=25
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
    
    def add_data_item(self):
        """添加数据项"""
        data = self.data_entry.get()
        if not data:
            self.update_status("请输入要添加的数据")
            return
        
        self.data_listbox.insert(tk.END, data)
        self.data_entry.set("")
        self.update_status(f"已添加: {data}")
    
    def remove_selected_item(self):
        """删除选中项"""
        selection = self.data_listbox.curselection()
        if not selection:
            self.update_status("请选择要删除的项")
            return
        
        item = self.data_listbox.get(selection[0])
        self.data_listbox.delete(selection[0])
        self.update_status(f"已删除: {item}")
    
    def clear_data_list(self):
        """清空数据列表"""
        self.data_listbox.delete(0, tk.END)
        self.update_status("数据列表已清空")

if __name__ == "__main__":
    root = tk.Tk()
    app = CustomWidgetsTestApp(root)
    root.mainloop()