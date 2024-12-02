import copy
import csv
import json
import os
import time
from tkinter import ttk
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt

from ExactSolver import ExactSolver
from RoomLayoutOptimizer import RoomLayoutOptimizer
from plot_utils import plot_layout


# 實驗類別
class Experiment:
    def __init__(self):
        self.test_cases = []
        self.results = []

    def add_test_case(self, room_length, room_width, furniture_list, exact_solution_expected=False):
        self.test_cases.append({
            'room_length': room_length,
            'room_width': room_width,
            'furniture_list': furniture_list,
            'exact_solution_expected': exact_solution_expected
        })

    def run(self, sa_runs=10):
        for idx, test_case in enumerate(self.test_cases):
            print(f"\nRunning Test Case {idx+1}: Room {test_case['room_length']}x{test_case['room_width']}m")
            furniture_list = test_case['furniture_list']
            # 模擬退火
            optimizer = RoomLayoutOptimizer(test_case['room_length'], test_case['room_width'], furniture_list)
            start_time = time.perf_counter()
            sa_energy = optimizer.optimize_layout(runs=sa_runs)
            sa_time = time.perf_counter() - start_time

            # 精確解法（僅適用於小規模測試案例）
            if test_case['exact_solution_expected']:
                exact_solver = ExactSolver(test_case['room_length'], test_case['room_width'], furniture_list)
                try:
                    start_time = time.perf_counter()
                    exact_layout, exact_energy = exact_solver.solve()
                    exact_time = time.perf_counter() - start_time
                    layout_image_path = f"exact_layout_test_case_{idx+1}.png"
                    if exact_layout:
                        exact_solver.display_layout(exact_layout, f"Exact Solution Test Case {idx+1} Layout", save_path=layout_image_path)
                    else:
                        print(f"  Test Case {idx+1} has no valid layout.")
                except MemoryError:
                    exact_layout, exact_energy = None, None
                    exact_time = None
                    print(f"  Exact Solver failed due to MemoryError for Test Case {idx+1}")
            else:
                exact_layout = None
                exact_energy = None
                exact_time = None

            # 儲存結果
            self.results.append({
                'test_case': idx+1,
                'room_size': f"{test_case['room_length']}x{test_case['room_width']}m",
                'sa_energy': sa_energy,
                'sa_time': sa_time,
                'exact_energy': exact_energy,
                'exact_time': exact_time,
                'sa_layout': copy.deepcopy(optimizer.best_layout),  # 儲存最佳佈局
                'exact_layout': copy.deepcopy(exact_layout)
            })

            # 生成並保存每個測試案例的佈局圖片
            sa_layout_image_path = f"sa_layout_test_case_{idx+1}.png"
            if optimizer.best_layout:
                optimizer.display_layout(optimizer.best_layout, f"Simulated Annealing Test Case {idx+1} Layout", save_path=sa_layout_image_path)
            else:
                print(f"  Test Case {idx+1} has no valid SA layout.")

            # 打印結果，增加時間精度
            print(f"  Simulated Annealing: Energy = {sa_energy:.2f}, Time = {sa_time:.4f}s")
            if test_case['exact_solution_expected']:
                if exact_energy is not None:
                    print(f"  Exact Solver:        Energy = {exact_energy:.2f}, Time = {exact_time:.4f}s")
                    if exact_energy == 0:
                        print("  Result: Successfully found a valid layout without overlaps.")
                    else:
                        print("  Result: Found a layout with overlaps.")
                else:
                    print("  Exact Solver: Failed to find a valid layout due to MemoryError.")
            else:
                print("  Exact Solver: Not applicable.")

        # 在運行完成後自動保存結果
        self.save_results_to_csv("experiment_results.csv")
        self.save_results_to_json("experiment_results.json")

    def save_results_to_csv(self, filename):
        # 定義CSV文件的欄位
        fieldnames = ['Test Case', 'Room Size', 'SA Energy', 'SA Time(s)', 'Exact Energy', 'Exact Time(s)']
        with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for result in self.results:
                writer.writerow({
                    'Test Case': result['test_case'],
                    'Room Size': result['room_size'],
                    'SA Energy': f"{result['sa_energy']:.2f}",
                    'SA Time(s)': f"{result['sa_time']:.4f}",
                    'Exact Energy': f"{result['exact_energy']:.2f}" if result['exact_energy'] is not None else "N/A",
                    'Exact Time(s)': f"{result['exact_time']:.4f}s" if result['exact_time'] is not None else "N/A"
                })
        print(f"\nResults have been saved to {os.path.abspath(filename)}")

    def save_results_to_json(self, filename):
        # 將結果轉換為JSON格式
        with open(filename, mode='w', encoding='utf-8') as jsonfile:
            json.dump(self.results, jsonfile, indent=4, ensure_ascii=False)
        print(f"Results have been saved to {os.path.abspath(filename)}")

    def display_results(self):
        # 創建結果視窗
        window = tk.Toplevel()
        window.title("實驗結果")
        window.geometry("1600x1200")  # 擴大視窗尺寸以容納更多內容

        # 創建一個滾動條容器
        canvas = tk.Canvas(window, bg='white')
        scrollbar = tk.Scrollbar(window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 定義顏色列表
        colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange', 'cyan', 'magenta']

        # 用於綜合圖表的數據
        test_cases_numbers = []
        sa_energies = []
        sa_times = []
        exact_energies = []
        exact_times = []

        # 顯示每個測試案例的結果和佈局
        for result in self.results:
            frame = tk.Frame(scrollable_frame, bd=2, relief='groove', padx=10, pady=10)
            frame.pack(padx=10, pady=10, fill='x')

            # 顯示數據
            data_frame = tk.Frame(frame)
            data_frame.pack(side='left', padx=10)

            tk.Label(data_frame, text=f"Test Case: {result['test_case']}", font=('Arial', 12, 'bold')).pack(anchor='w')
            tk.Label(data_frame, text=f"Room Size: {result['room_size']}", font=('Arial', 12)).pack(anchor='w')
            tk.Label(data_frame, text=f"SA Energy: {result['sa_energy']:.2f}", font=('Arial', 12)).pack(anchor='w')
            tk.Label(data_frame, text=f"SA Time: {result['sa_time']:.4f}s", font=('Arial', 12)).pack(anchor='w')
            if result['exact_energy'] is not None:
                tk.Label(data_frame, text=f"Exact Energy: {result['exact_energy']:.2f}", font=('Arial', 12)).pack(anchor='w')
                tk.Label(data_frame, text=f"Exact Time: {result['exact_time']:.4f}s", font=('Arial', 12)).pack(anchor='w')
            else:
                tk.Label(data_frame, text="Exact Energy: N/A", font=('Arial', 12)).pack(anchor='w')
                tk.Label(data_frame, text="Exact Time: N/A", font=('Arial', 12)).pack(anchor='w')

            # 更新綜合圖表的數據
            test_cases_numbers.append(result['test_case'])
            sa_energies.append(result['sa_energy'])
            sa_times.append(result['sa_time'])
            # 如果有精確解法，則添加到列表中，否則添加 None
            if result['exact_energy'] is not None:
                exact_energies.append(result['exact_energy'])
                exact_times.append(result['exact_time'])
            else:
                exact_energies.append(None)  # 使用 None 來表示沒有數據
                exact_times.append(None)

            # 顯示SA佈局圖表
            if result['sa_layout']:
                layout_frame = tk.Frame(frame)
                layout_frame.pack(side='left', padx=10)

                # 使用 matplotlib 繪製佈局並嵌入到Tkinter
                fig, ax = plot_layout(result['sa_layout'], self.test_cases[result['test_case'] - 1]['room_length'],
                                      self.test_cases[result['test_case'] - 1]['room_width'],
                                      f"Test Case {result['test_case']} SA Layout")

                # 將圖表嵌入到Tkinter
                canvas_fig = FigureCanvasTkAgg(fig, master=layout_frame)
                canvas_fig.draw()
                canvas_fig.get_tk_widget().pack()

                # 另存圖表為圖片
                layout_image_path = f"sa_layout_test_case_{result['test_case']}.png"
                fig.savefig(layout_image_path)
                print(f"  Layout image saved to {layout_image_path}")

                plt.close(fig)  # 關閉圖表以防止重複顯示

            # 顯示Exact Solver佈局圖表
            if result['exact_layout']:
                exact_layout_frame = tk.Frame(frame)
                exact_layout_frame.pack(side='left', padx=10)

                # 使用 matplotlib 繪製佈局並嵌入到Tkinter
                fig_exact, ax_exact = plot_layout(result['exact_layout'], self.test_cases[result['test_case'] - 1]['room_length'],
                                                 self.test_cases[result['test_case'] - 1]['room_width'],
                                                 f"Test Case {result['test_case']} Exact Layout")

                # 將圖表嵌入到Tkinter
                exact_canvas_fig = FigureCanvasTkAgg(fig_exact, master=exact_layout_frame)
                exact_canvas_fig.draw()
                exact_canvas_fig.get_tk_widget().pack()

                # 另存圖表為圖片
                exact_layout_image_path = f"exact_layout_test_case_{result['test_case']}.png"
                fig_exact.savefig(exact_layout_image_path)
                print(f"  Exact layout image saved to {exact_layout_image_path}")

                plt.close(fig_exact)  # 關閉圖表以防止重複顯示

        # 繪製能量比較圖
        fig_energy, ax_energy = plt.subplots(figsize=(10, 6))
        width = 0.35  # 柱狀圖寬度
        indices = range(len(test_cases_numbers))

        # 繪製SA能量
        ax_energy.bar([i - width/2 for i in indices], sa_energies, width, label='SA Energy', color='skyblue')

        # 繪製Exact能量（處理None值）
        exact_energies_clean = [e if e is not None else 0 for e in exact_energies]
        ax_energy.bar([i + width/2 for i in indices], exact_energies_clean, width, label='Exact Energy', color='salmon')

        ax_energy.set_xlabel('Test Case')
        ax_energy.set_ylabel('Energy')
        ax_energy.set_title('SA vs Exact Energy Across Test Cases')
        ax_energy.set_xticks(indices)
        ax_energy.set_xticklabels([f"Case {tc}" for tc in test_cases_numbers])
        ax_energy.legend()

        plt.tight_layout()

        # 另存能量比較圖為圖片
        energy_image_path = "energy_comparison.png"
        fig_energy.savefig(energy_image_path)
        print(f"  Energy comparison image saved to {energy_image_path}")

        # 嵌入能量比較圖到Tkinter
        energy_frame = tk.Frame(scrollable_frame, bd=2, relief='groove', padx=10, pady=10)
        energy_frame.pack(padx=10, pady=10, fill='both')

        energy_canvas = FigureCanvasTkAgg(fig_energy, master=energy_frame)
        energy_canvas.draw()
        energy_canvas.get_tk_widget().pack()

        plt.close(fig_energy)  # 關閉圖表以防止重複顯示

        # 繪製時間比較圖
        fig_time, ax_time = plt.subplots(figsize=(10, 6))
        width = 0.35  # 柱狀圖寬度

        # 繪製SA時間
        ax_time.bar([i - width/2 for i in indices], sa_times, width, label='SA Time (s)', color='lightgreen')

        # 繪製Exact時間（處理None值）
        exact_times_clean = [t if t is not None else 0 for t in exact_times]
        ax_time.bar([i + width/2 for i in indices], exact_times_clean, width, label='Exact Time (s)', color='lightcoral')

        ax_time.set_xlabel('Test Case')
        ax_time.set_ylabel('Time (s)')
        ax_time.set_title('SA vs Exact Time Across Test Cases')
        ax_time.set_xticks(indices)
        ax_time.set_xticklabels([f"Case {tc}" for tc in test_cases_numbers])
        ax_time.legend()

        plt.tight_layout()

        # 另存時間比較圖為圖片
        time_image_path = "time_comparison.png"
        fig_time.savefig(time_image_path)
        print(f"  Time comparison image saved to {time_image_path}")

        # 嵌入時間比較圖到Tkinter
        time_frame = tk.Frame(scrollable_frame, bd=2, relief='groove', padx=10, pady=10)
        time_frame.pack(padx=10, pady=10, fill='both')

        time_canvas = FigureCanvasTkAgg(fig_time, master=time_frame)
        time_canvas.draw()
        time_canvas.get_tk_widget().pack()

        plt.close(fig_time)  # 關閉圖表以防止重複顯示

        # 新增綜合數據比較表格
        table_frame = tk.Frame(scrollable_frame, bd=2, relief='groove', padx=10, pady=10)
        table_frame.pack(padx=10, pady=10, fill='both')

        # 使用 ttk.Treeview 創建表格
        tree = ttk.Treeview(table_frame, columns=("Test Case", "Room Size", "SA Energy", "SA Time(s)", "Exact Energy", "Exact Time(s)"), show='headings')
        tree.heading("Test Case", text="Test Case")
        tree.heading("Room Size", text="Room Size")
        tree.heading("SA Energy", text="SA Energy")
        tree.heading("SA Time(s)", text="SA Time(s)")
        tree.heading("Exact Energy", text="Exact Energy")
        tree.heading("Exact Time(s)", text="Exact Time(s)")

        # 設置列寬和對齊方式
        tree.column("Test Case", width=80, anchor='center')
        tree.column("Room Size", width=100, anchor='center')
        tree.column("SA Energy", width=100, anchor='center')
        tree.column("SA Time(s)", width=100, anchor='center')
        tree.column("Exact Energy", width=100, anchor='center')
        tree.column("Exact Time(s)", width=100, anchor='center')

        # 插入數據
        for result in self.results:
            tree.insert("", "end", values=(
                result['test_case'],
                result['room_size'],
                f"{result['sa_energy']:.2f}",
                f"{result['sa_time']:.4f}",
                f"{result['exact_energy']:.2f}" if result['exact_energy'] is not None else "N/A",
                f"{result['exact_time']:.4f}s" if result['exact_time'] is not None else "N/A"
            ))

        tree.pack(padx=10, pady=10, fill='x')

        # 另存數據比較表格為圖片
        fig_table, ax_table = plt.subplots(figsize=(8, 2 + 0.3 * len(self.results)), dpi=100)
        ax_table.axis('tight')
        ax_table.axis('off')
        table_data = [
            ["Test Case", "Room Size", "SA Energy", "SA Time(s)", "Exact Energy", "Exact Time(s)"]
        ]
        for result in self.results:
            table_data.append([
                result['test_case'],
                result['room_size'],
                f"{result['sa_energy']:.2f}",
                f"{result['sa_time']:.4f}s",
                f"{result['exact_energy']:.2f}" if result['exact_energy'] is not None else "N/A",
                f"{result['exact_time']:.4f}s" if result['exact_time'] is not None else "N/A"
            ])
        table = ax_table.table(cellText=table_data, cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.auto_set_column_width(col=list(range(len(table_data[0]))))

        plt.tight_layout()
        table_image_path = "results_comparison_table.png"
        fig_table.savefig(table_image_path)
        print(f"  Results comparison table image saved to {table_image_path}")
        plt.close(fig_table)

        # 顯示提示用戶圖片已保存
        tk.Label(table_frame, text="數據比較表格已另存為 'results_comparison_table.png'。", font=('Arial', 12)).pack(pady=10)