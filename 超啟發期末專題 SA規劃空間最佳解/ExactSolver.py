import itertools
import matplotlib.pyplot as plt

# 精確解法類別（暴力搜尋）
class ExactSolver:
    def __init__(self, room_length, room_width, furniture_list):
        self.room_length = room_length
        self.room_width = room_width
        self.furniture_list = furniture_list

    def solve(self):
        try:
            # 生成所有可能的佈局
            furniture_positions = []
            for furniture in self.furniture_list:
                positions = []
                for _ in range(furniture.quantity):
                    possible_positions = []
                    step = 0.25  # 減小步進值以提高精度
                    x_steps = int((self.room_length - furniture.length) / step) + 1
                    y_steps = int((self.room_width - furniture.width) / step) + 1
                    for i in range(x_steps):
                        for j in range(y_steps):
                            x = i * step
                            y = j * step
                            # 不旋轉
                            possible_positions.append({
                                'x': x, 
                                'y': y, 
                                'orientation': 0, 
                                'length': furniture.length, 
                                'width': furniture.width
                            })
                            # 旋轉（如果非正方形）
                            if furniture.length != furniture.width:
                                rotated_length = furniture.width
                                rotated_width = furniture.length
                                if x + rotated_length <= self.room_length and y + rotated_width <= self.room_width:
                                    possible_positions.append({
                                        'x': x, 
                                        'y': y, 
                                        'orientation': 90, 
                                        'length': rotated_length, 
                                        'width': rotated_width
                                    })
                    positions.append(possible_positions)
                furniture_positions.append(positions)

            # 使用 itertools.product 生成所有可能的佈局
            all_possible_layouts = itertools.product(*[
                itertools.product(*furniture_positions[i]) for i in range(len(furniture_positions))
            ])

            best_layout = None
            best_energy = float('inf')
            layout_count = 0
            max_layouts = 1000000  # 限制最大佈局數以防計算時間過長

            for layout_tuple in all_possible_layouts:
                if layout_count >= max_layouts:
                    print("  Reached maximum layout limit without finding optimal solution.")
                    break
                layout = []
                overlap = False
                for furniture_index, furniture in enumerate(self.furniture_list):
                    for item in layout_tuple[furniture_index]:
                        # 檢查是否超出邊界
                        if item['x'] + item['length'] > self.room_length or item['y'] + item['width'] > self.room_width:
                            overlap = True
                            break
                        layout.append({
                            'name': furniture.name,
                            'length': item['length'],
                            'width': item['width'],
                            'x': item['x'],
                            'y': item['y'],
                            'orientation': item['orientation']
                        })
                        # 檢查是否與已放置的家具重疊
                        for placed_item in layout[:-1]:
                            if self.is_overlap(placed_item, layout[-1]):
                                overlap = True
                                break
                        if overlap:
                            break
                    if overlap:
                        break
                if not overlap:
                    # 計算能量（重疊懲罰）
                    energy = self.calculate_energy(layout)
                    if energy < best_energy:
                        best_energy = energy
                        best_layout = layout
                        print(f"  Found better layout with energy {best_energy:.2f}")
                        for item in best_layout:
                            print(f"    {item['name']} at ({item['x']:.2f}, {item['y']:.2f}) with size {item['length']}x{item['width']}")
                        if best_energy == 0:
                            break  # 找到最佳解，退出
                layout_count += 1
                if layout_count >= max_layouts:
                    print("  Reached maximum layout limit without finding optimal solution.")
                    break

            if best_layout:
                print(f"Exact Solver found layout with energy {best_energy:.2f}")
            else:
                print("Exact Solver did not find any valid layout.")

            return best_layout, best_energy

        except MemoryError:
            print("  Exact Solver encountered a MemoryError and cannot continue.")
            return None, None

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
        for i in range(len(layout)):
            for j in range(i + 1, len(layout)):
                if self.is_overlap(layout[i], layout[j]):
                    overlap_area = self.calculate_overlap_area(layout[i], layout[j])
                    overlap_penalty += overlap_area
        return overlap_penalty

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