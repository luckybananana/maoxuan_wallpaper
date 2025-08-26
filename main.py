import os, sys, json, random, ctypes, math
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon, QCursor
from PIL import Image, ImageDraw, ImageFont

# ===== 工具函数：获取资源路径 =====
def resource_path(relative_path):
    """获取资源文件路径，兼容开发环境和 PyInstaller 打包"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# ===== 基本配置 =====
W, H = 2560, 1440
OUT = os.path.join(os.path.abspath("."), "output.jpg")
FONT_PATH = resource_path("simhei.ttf")
QUOTES_PATH = resource_path("mao_quotes.json")
ICON_PATH = resource_path("tray.ico")

# 主色候选
COLORS = [
    "#E57373","#F06292","#BA68C8","#9575CD","#7986CB",
    "#64B5F6","#4DB6AC","#81C784","#DCE775","#FFD54F",
    "#5488BC","#917C6B","#AA9F7C","#A29296","#515E68"
]

# ===== 绘制工具函数 =====
def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def adjust_color(rgb, factor=1.0):
    r, g, b = rgb
    return (max(0, min(255, int(r*factor))),
            max(0, min(255, int(g*factor))),
            max(0, min(255, int(b*factor))))

def draw_layered_waves(draw, base_rgb):
    """画 6 层同色系正弦波：上浅下深"""
    num_layers = 6
    base_from_bottom = int(H * 0.32)
    gap_per_layer   = int(H * 0.035)
    base_wavelength = 420
    base_amplitude  = 52
    step = 6

    for i in range(num_layers):
        color = adjust_color(base_rgb, 1 - i*0.06)
        alpha = min(255, 25 + i*38)   # 顶层更透明，底层更深
        fill = (*color, alpha)

        wavelength = base_wavelength * (1.0 + i*0.03)
        amplitude  = base_amplitude  * (1.0 + i*0.05)
        phase      = random.uniform(0, math.tau)

        layer_offset = H - (base_from_bottom - i*gap_per_layer)

        points = []
        for x in range(0, W + step, step):
            y = layer_offset - amplitude * math.sin(2*math.pi*x / wavelength + phase)
            points.append((x, y))

        points += [(W, H), (0, H)]
        draw.polygon(points, fill=fill)

def pick_text():
    try:
        with open(QUOTES_PATH, encoding="utf-8") as f:
            quotes = json.load(f)
        if quotes:
            return random.choice(quotes)
    except Exception:
        pass
    return "为有牺牲多壮志，敢教日月换新天。"

# ===== 壁纸生成 =====
def make_wallpaper():
    img = Image.new("RGBA", (W, H), "#E6E6E6")
    draw = ImageDraw.Draw(img, "RGBA")

    base_hex = random.choice(COLORS)
    base_rgb = hex_to_rgb(base_hex)
    draw_layered_waves(draw, base_rgb)

    text = pick_text()
    try:
        font = ImageFont.truetype(FONT_PATH, 80)
    except Exception:
        font = ImageFont.load_default()

    max_w = int(W * 0.8)
    lines, line = [], ""
    for ch in text:
        w = draw.textbbox((0,0), line + ch, font=font)[2]
        if w <= max_w:
            line += ch
        else:
            lines.append(line); line = ch
    if line: lines.append(line)

    line_h = draw.textbbox((0,0), "高", font=font)[3]
    total_h = len(lines) * line_h
    y = (H - total_h)//2 - int(H*0.20)
    for ln in lines:
        w = draw.textbbox((0,0), ln, font=font)[2]
        draw.text(((W - w)//2, y), ln, font=font, fill="#000000")
        y += line_h

    img = img.convert("RGB")
    img.save(OUT, quality=95)
    ctypes.windll.user32.SystemParametersInfoW(20, 0, OUT, 3)

# ===== 托盘逻辑 =====
class TrayApp(QSystemTrayIcon):
    def __init__(self):
        super().__init__()
        self.setToolTip("毛语录壁纸")

        if not os.path.exists(ICON_PATH):
            from PyQt5.QtWidgets import QApplication
            self.setIcon(QApplication.style().standardIcon(QApplication.style().SP_ComputerIcon))
        else:
            self.setIcon(QIcon(ICON_PATH))

        # 菜单（只包含“退出”）
        self.menu = QMenu()
        quit_action = QAction("退出程序", self)
        quit_action.triggered.connect(self.quit_app)
        self.menu.addAction(quit_action)

        # 激活事件：左键更换壁纸，右键显示菜单
        self.activated.connect(self.on_activated)

    def next_wallpaper(self):
        make_wallpaper()

    def on_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:  # 左键
            self.next_wallpaper()
        elif reason == QSystemTrayIcon.Context:  # 右键
            cursor_pos = QCursor.pos()
            self.menu.exec_(cursor_pos)

    def quit_app(self):
        self.hide()
        QApplication.quit()

# ===== 程序入口 =====
if __name__ == "__main__":
    import PyQt5.QtWidgets as QW
    app = QW.QApplication(sys.argv)
    tray = TrayApp()
    tray.show()
    tray.next_wallpaper()
    sys.exit(app.exec_())
