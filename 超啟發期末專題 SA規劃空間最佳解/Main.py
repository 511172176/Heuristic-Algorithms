import tkinter as tk
from tkinter import ttk
import random
import matplotlib.pyplot as plt
from matplotlib import rcParams
import matplotlib.font_manager as fm
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
from Experiment import Experiment
from RoomLayoutOptimizer import RoomLayoutOptimizer
from ExactSolver import ExactSolver

# 動態選擇可用的支持中文的字體
def select_font(preferred_fonts):
    available_fonts = set(fm.FontProperties(fname=font).get_name() for font in fm.findSystemFonts(fontpaths=None, fontext='ttf'))
    for font in preferred_fonts:
        if font in available_fonts:
            return font
    return 'sans-serif'

preferred_fonts = ['Microsoft YaHei', 'SimHei', 'PingFang SC', 'Noto Sans CJK', 'WenQuanYi Micro Hei']
selected_font = select_font(preferred_fonts)

# 設置 Matplotlib 的字體
rcParams['font.sans-serif'] = [selected_font]
rcParams['axes.unicode_minus'] = False

# 設定隨機種子（可選）
random.seed(42)

# 家具類別
class Furniture:
    def __init__(self, name, length, width, quantity):
        self.name = name
        self.length = length
        self.width = width
        self.quantity = quantity

# 主函數
def main():
    # 創建實驗對象
    experiment = Experiment()

    # 定義測試案例
    # 測試案例1：小房間，預期有精確解
    furniture_list1 = [
        Furniture('床', 1.5, 1, 1),
        Furniture('書桌', 1, 0.5, 1),
        Furniture('椅子', 0.5, 0.5, 1)
    ]
    experiment.add_test_case(room_length=3, room_width=3, furniture_list=furniture_list1, exact_solution_expected=True)

    # 測試案例2：中等房間，無精確解（設置為 False 以避免 MemoryError）
    furniture_list2 = [
        Furniture('床', 2, 1.5, 1),
        Furniture('衣櫃', 1.5, 0.6, 1),
        Furniture('書桌', 1.2, 0.6, 1),
        Furniture('椅子', 0.5, 0.5, 2),
        Furniture('沙發', 2, 1, 1),
        Furniture('茶几', 1, 0.5, 1)
    ]
    experiment.add_test_case(room_length=5, room_width=4, furniture_list=furniture_list2, exact_solution_expected=True)

    # 測試案例3：更小的房間，預期有精確解
    furniture_list3 = [
        Furniture('床', 1, 1, 1),
        Furniture('書桌', 1, 0.5, 1),
        Furniture('椅子', 0.5, 0.5, 1)
    ]
    experiment.add_test_case(room_length=2.5, room_width=2, furniture_list=furniture_list3, exact_solution_expected=True)

    # 測試案例4：更大房間，更多家具，無精確解（設置為 False 以避免 MemoryError）
    furniture_list4 = [
        Furniture('床', 2.5, 1.5, 1),
        Furniture('衣櫃', 2, 0.8, 2),
        Furniture('書桌', 1.5, 0.7, 2),
        Furniture('椅子', 0.6, 0.6, 4),
        Furniture('沙發', 3, 1.2, 1),
        Furniture('茶几', 1.2, 0.6, 2)
    ]
    experiment.add_test_case(room_length=6, room_width=5, furniture_list=furniture_list4, exact_solution_expected=False)

    # 運行實驗
    experiment.run(sa_runs=20)  # 增加 SA 運行次數以提高找到最佳解的概率

    # 創建主視窗
    root = tk.Tk()
    root.title("房間佈置優化實驗工具")
    root.geometry("300x150")  # 設置主視窗大小

    # 改進按鈕外觀
    style = ttk.Style()
    style.theme_use('clam')  # 使用 'clam' 主題
    style.configure('TButton',
                    font=('Arial', 10, 'bold'),
                    foreground='white',
                    background='#4CAF50',
                    padding=(6, 6),
                    width=20)  # 設定固定寬度以統一按鈕大小
    style.map('TButton',
              foreground=[('active', 'white')],
              background=[('active', '#45a049')])

    # 使用 ttk.Button 以統一外觀
    display_button = ttk.Button(root, text="顯示實驗結果", command=experiment.display_results)
    display_button.pack(pady=10, ipadx=10, ipady=5)

    exit_button = ttk.Button(root, text="退出", command=root.destroy)
    exit_button.pack(pady=10, ipadx=10, ipady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
