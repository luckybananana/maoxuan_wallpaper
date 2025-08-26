import os, sys, json, random, ctypes, math
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from PIL import Image, ImageDraw, ImageFont

# ===== 基本配置 =====
W, H = 2560, 1440
BASE_DIR = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
OUT = os.path.join(BASE_DIR, "output.jpg")
FONT_PATH = os.path.join(BASE_DIR, "simhei.ttf")
QUOTES_PATH = os.path.join(BASE_DIR, "mao_quotes.json")

# 主色候选
COLORS = [
    "#E57373","#F06292","#BA68C8","#9575CD","#7986CB",
    "#64B5F6","#4DB6AC","#81C784","#DCE775","#FFD54F",
    "#5488BC","#917C6B","#AA9F7C","#A29296","#515E68"
]

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def adjust_color(rgb, factor=1.0):
    """同色系亮度微调：factor<1变暗，>1变亮"""
    r, g, b = rgb
    return (max(0, min(255, int(r*factor))),
            max(0, min(255, int(g*factor))),
            max(0, min(255, int(b*factor))))

def draw_layered_waves(draw, base_rgb):
    """画 6 层同色系正弦波：上浅下深"""
    num_layers = 6
    base_from_bottom = int(H * 0.32)   # 顶层离底部距离
    gap_per_layer   = int(H * 0.035)   # 层间距
    base_wavelength = 420
    base_amplitude  = 52
    step = 6

    for i in range(num_layers):
        color = adjust_color(base_rgb, 1 - i*0.06)
        alpha = min(255, 25 + i*38)  # 顶层淡，底层厚重
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
        return random.choice(quotes) or "为有牺牲多壮志，敢教日月换新天。"
    except Exception:
        return "为有牺牲多壮志，敢教日月换新天。"

def make_wallpaper():
    # 背景
    img = Image.new("RGBA", (W, H), "#E6E6E6")
    draw = ImageDraw.Draw(img, "RGBA")

    # 随机主色 & 波浪
    base_hex = random.choice(COLORS)
    base_rgb = hex_to_rgb(base_hex)
    draw_layered_waves(draw, base_rgb)

    # 文字（黑色，向上移）
    text = pick_text()
    try:
        font = ImageFont.truetype(FONT_PATH, 80)  # 字号调小
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
    y = (H - total_h)//2 - int(H*0.20)  # 上移 20%
    for ln in lines:
        w = draw.textbbox((0,0), ln, font=font)[2]
        draw.text(((W - w)//2, y), ln, font=font, fill="#000000")
        y += line_h

    # 保存 + 设置壁纸
    img = img.convert("RGB")
    img.save(OUT, quality=95)
    ctypes.windll.user32.SystemParametersInfoW(20, 0, OUT, 3)

# ===== 托盘逻辑 =====
class TrayApp(QSystemTrayIcon):
    def __init__(self):
        super().__init__()
        self.setToolTip("毛语录壁纸")
        self.setIcon(QIcon(os.path.join(BASE_DIR, "tray.ico")))
        menu = QMenu()
        next_action = QAction("下一张", triggered=self.next_wallpaper)
        quit_action = QAction("退出", triggered=QApplication.quit)
        menu.addAction(next_action)
        menu.addSeparator()
        menu.addAction(quit_action)
        self.setContextMenu(menu)
        self.activated.connect(self.on_activated)

    def next_wallpaper(self):
        make_wallpaper()

    def on_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:  # 左键单击
            self.next_wallpaper()

if __name__ == "__main__":
    import PyQt5.QtWidgets as QW
    app = QW.QApplication(sys.argv)
    tray = TrayApp()
    tray.show()
    tray.next_wallpaper()  # 启动即生成第一张
    sys.exit(app.exec_())
