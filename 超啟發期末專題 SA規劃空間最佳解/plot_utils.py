# plot_utils.py

import matplotlib.pyplot as plt
from matplotlib import rcParams
import matplotlib.font_manager as fm

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

def plot_layout(layout, room_length, room_width, title, save_path=None):
    """
    繪製家具佈局圖的通用函數。

    :param layout: 佈局列表，每個元素是一個字典，包含家具的詳細信息。
    :param room_length: 房間的長度。
    :param room_width: 房間的寬度。
    :param title: 圖表標題。
    :param save_path: 保存圖表的路徑（可選）。
    """
    fig, ax = plt.subplots(figsize=(6, 6))  # 統一圖表尺寸

    # 繪製房間邊界
    ax.add_patch(plt.Rectangle((0, 0), room_length, room_width, fill=False, edgecolor='black', linewidth=2))

    # 定義顏色列表，確保每次繪製使用相同的顏色
    colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange', 'cyan', 'magenta']

    # 繪製家具
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

    ax.set_xlim(0, room_length)
    ax.set_ylim(0, room_width)
    ax.margins(0.05)  # 添加邊距
    ax.set_aspect('equal')
    ax.set_title(title)
    ax.set_xlabel('Length (m)')
    ax.set_ylabel('Width (m)')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
        print(f"  Layout image saved to {save_path}")

    return fig, ax  # 返回圖表和軸對象以便嵌入GUI
