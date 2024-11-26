import random
import copy
import math
import matplotlib.pyplot as plt

# 優化器類別（模擬退火）
class RoomLayoutOptimizer:
    def __init__(self, room_length, room_width, furniture_list):
        self.room_length = room_length
        self.room_width = room_width
        self.furniture_list = furniture_list
        self.best_layout = None

    def optimize_layout(self, runs=1):
        best_layout_overall = None
        best_energy_overall = float('inf')

        for run in range(runs):
            # 初始化
            initial_state = self.generate_random_layout()
            current_state = copy.deepcopy(initial_state)
            current_energy = self.calculate_energy(current_state)
            best_state = copy.deepcopy(current_state)
            best_energy = current_energy

            T = 5000  # 提高初始溫度
            T_min = 1  # 最小溫度
            alpha = 0.85  # 降溫速率（降低以保持更長的高溫階段）
            iteration = 0
            max_iterations = 50000  # 增加最大迭代次數

            while T > T_min and iteration < max_iterations:
                for _ in range(100):
                    new_state = self.generate_neighbor(current_state)
                    new_energy = self.calculate_energy(new_state)
                    delta_energy = new_energy - current_energy
                    if delta_energy < 0:
                        current_state = new_state
                        current_energy = new_energy
                        if new_energy < best_energy:
                            best_state = copy.deepcopy(new_state)
                            best_energy = new_energy
                    else:
                        probability = math.exp(-delta_energy / T)
                        if random.random() < probability:
                            current_state = new_state
                            current_energy = new_energy
                T *= alpha  # 降溫
                iteration += 1
                # 打印當前能量以監控優化過程
                if iteration % 1000 == 0:
                    print(f"  Run {run+1}, Iteration {iteration}, Temperature {T:.2f}, Best Energy {best_energy:.2f}")

            # 更新全域最佳佈局
            if best_energy < best_energy_overall:
                best_energy_overall = best_energy
                best_layout_overall = copy.deepcopy(best_state)

        self.best_layout = best_layout_overall
        return best_energy_overall

    def generate_random_layout(self):
        layout = []
        for furniture in self.furniture_list:
            for _ in range(furniture.quantity):
                orientation = random.choice([0, 90])
                if orientation == 90:
                    length, width = furniture.width, furniture.length
                else:
                    length, width = furniture.length, furniture.width
                x = random.uniform(0, self.room_length - length)
                y = random.uniform(0, self.room_width - width)
                layout.append({
                    'name': furniture.name,
                    'length': length,
                    'width': width,
                    'x': x,
                    'y': y,
                    'orientation': orientation
                })
        return layout

    def generate_neighbor(self, current_state):
        neighbor = copy.deepcopy(current_state)
        idx = random.randint(0, len(neighbor) - 1)
        move_x = random.uniform(-0.5, 0.5)  # 減小移動範圍以避免超出邊界
        move_y = random.uniform(-0.5, 0.5)
        # 確保移動後不超出邊界
        neighbor[idx]['x'] = min(max(neighbor[idx]['x'] + move_x, 0), self.room_length - neighbor[idx]['length'])
        neighbor[idx]['y'] = min(max(neighbor[idx]['y'] + move_y, 0), self.room_width - neighbor[idx]['width'])
        
        # 隨機旋轉家具（20%概率）
        if random.random() < 0.2:
            neighbor[idx]['orientation'] = (neighbor[idx]['orientation'] + 90) % 180
            neighbor[idx]['length'], neighbor[idx]['width'] = neighbor[idx]['width'], neighbor[idx]['length']
        
        return neighbor

    def is_overlap(self, item1, item2):
        # 判斷兩個家具是否重疊
        if (item1['x'] < item2['x'] + item2['length'] and
            item1['x'] + item1['length'] > item2['x'] and
            item1['y'] < item2['y'] + item2['width'] and
            item1['y'] + item1['width'] > item2['y']):
            return True
        return False

    def calculate_energy(self, layout):
        # 能量函數，越小越好（僅重疊懲罰）
        overlap_penalty = 0

        # 檢查家具重疊
        for i in range(len(layout)):
            for j in range(i + 1, len(layout)):
                if self.is_overlap(layout[i], layout[j]):
                    overlap_area = self.calculate_overlap_area(layout[i], layout[j])
                    overlap_penalty += overlap_area

        # 能量函數僅基於重疊懲罰
        total_energy = overlap_penalty
        return total_energy

    def calculate_overlap_area(self, item1, item2):
        x_overlap = max(0, min(item1['x'] + item1['length'], item2['x'] + item2['length']) - max(item1['x'], item2['x']))
        y_overlap = max(0, min(item1['y'] + item1['width'], item2['y'] + item2['width']) - max(item1['y'], item2['y']))
        return x_overlap * y_overlap

    def display_layout(self, layout, title, save_path=None):
        # 繪製佈局
        fig, ax = plt.subplots(figsize=(6, 6))
        scale_x = self.room_length
        scale_y = self.room_width

        # 繪製房間
        ax.add_patch(plt.Rectangle((0, 0), self.room_length, self.room_width, fill=False, edgecolor='black', linewidth=2))

        # 繪製家具
        colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange', 'cyan', 'magenta']
        for idx, item in enumerate(layout):
            x = item['x']
            y = item['y']
            length = item['length']
            width = item['width']
            color = colors[idx % len(colors)]
            rect = plt.Rectangle((x, y), length, width, facecolor=color, edgecolor='black', alpha=0.7)
            ax.add_patch(rect)
            # 添加家具名稱
            ax.text(x + length/2, y + width/2, item['name'], ha='center', va='center', color='white', fontsize=8, clip_on=True)

        ax.set_xlim(0, self.room_length)
        ax.set_ylim(0, self.room_width)
        ax.margins(0.05)  # 添加一些邊距以防止文字被裁剪
        ax.set_aspect('equal')
        ax.set_title(title)
        ax.set_xlabel('Length (m)')
        ax.set_ylabel('Width (m)')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)
            print(f"  Layout image saved to {save_path}")

        plt.close(fig)  # 關閉圖表以防止重複顯示