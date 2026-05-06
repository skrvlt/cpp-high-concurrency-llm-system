from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "doc" / "figures"


def load_font(size, bold=False):
    candidates = [
        Path("C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("C:/Windows/Fonts/simsun.ttc"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


FONT = load_font(28)
SMALL = load_font(22)
BOLD = load_font(28, bold=True)


def canvas(width=1500, height=900):
    image = Image.new("RGB", (width, height), "#f8fafc")
    draw = ImageDraw.Draw(image)
    return image, draw


def text_size(draw, text, font):
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def center_text(draw, box, text, font=FONT, fill="#111827"):
    x1, y1, x2, y2 = box
    width, height = text_size(draw, text, font)
    draw.text((x1 + (x2 - x1 - width) / 2, y1 + (y2 - y1 - height) / 2), text, font=font, fill=fill)


def rounded_box(draw, box, text, fill="#ffffff", outline="#2563eb", font=FONT):
    draw.rounded_rectangle(box, radius=24, fill=fill, outline=outline, width=3)
    center_text(draw, box, text, font=font)


def arrow(draw, start, end, fill="#334155", width=4):
    draw.line([start, end], fill=fill, width=width)
    x1, y1 = start
    x2, y2 = end
    if abs(x2 - x1) >= abs(y2 - y1):
        sign = 1 if x2 >= x1 else -1
        points = [(x2, y2), (x2 - sign * 18, y2 - 10), (x2 - sign * 18, y2 + 10)]
    else:
        sign = 1 if y2 >= y1 else -1
        points = [(x2, y2), (x2 - 10, y2 - sign * 18), (x2 + 10, y2 - sign * 18)]
    draw.polygon(points, fill=fill)


def title(draw, text):
    center_text(draw, (0, 24, 1500, 84), text, font=BOLD, fill="#0f172a")


def save(image, name):
    OUT.mkdir(parents=True, exist_ok=True)
    image.save(OUT / name)


def use_case():
    image, draw = canvas()
    title(draw, "系统用例图")
    rounded_box(draw, (580, 130, 920, 760), "智能交互系统", fill="#eef6ff", outline="#1d4ed8", font=BOLD)
    user = (120, 260, 320, 360)
    admin = (1180, 260, 1380, 360)
    rounded_box(draw, user, "普通用户", fill="#fff7ed", outline="#ea580c")
    rounded_box(draw, admin, "系统管理员", fill="#f0fdf4", outline="#16a34a")
    cases = [
        (610, 180, 890, 240, "用户登录"),
        (610, 290, 890, 350, "发起问答"),
        (610, 400, 890, 460, "查看历史记录"),
        (610, 510, 890, 570, "查看系统概览"),
        (610, 620, 890, 680, "日志与配置维护"),
    ]
    for x1, y1, x2, y2, label in cases:
        rounded_box(draw, (x1, y1, x2, y2), label, fill="#ffffff", outline="#64748b", font=SMALL)
    for y in [210, 320, 430]:
        arrow(draw, (320, 310), (610, y))
    for y in [210, 540, 650]:
        arrow(draw, (1180, 310), (890, y))
    save(image, "figure-3-1-use-case.png")


def architecture():
    image, draw = canvas()
    title(draw, "系统总体结构图")
    boxes = [
        (90, 360, 330, 470, "Web 前端\n用户页/管理页", "#fff7ed", "#ea580c"),
        (440, 340, 700, 490, "C++ 高并发接入层\nEpoll/Reactor/线程池", "#eff6ff", "#2563eb"),
        (810, 340, 1070, 490, "Python AI 服务层\nFastAPI/模型封装", "#f0fdf4", "#16a34a"),
        (1180, 360, 1410, 470, "数据与配置层\nSQLite/MySQL Schema", "#fdf2f8", "#db2777"),
    ]
    for box in boxes:
        x1, y1, x2, y2, label, fill, outline = box
        draw.rounded_rectangle((x1, y1, x2, y2), radius=28, fill=fill, outline=outline, width=3)
        lines = label.split("\n")
        for idx, line in enumerate(lines):
            center_text(draw, (x1, y1 + 28 + idx * 42, x2, y1 + 70 + idx * 42), line, font=SMALL if idx else BOLD)
    for start, end in [((330, 415), (440, 415)), ((700, 415), (810, 415)), ((1070, 415), (1180, 415))]:
        arrow(draw, start, end)
    center_text(draw, (440, 540, 1070, 610), "统一 HTTP/JSON 接口契约：/api/login、/api/chat、/api/history、/api/health", font=SMALL)
    save(image, "figure-4-1-architecture.png")


def chat_flow():
    image, draw = canvas()
    title(draw, "智能问答处理流程图")
    steps = [
        "用户输入问题",
        "浏览器提交请求",
        "C++ 网关读取并转发",
        "Python 服务组织上下文",
        "调用模型接口生成回答",
        "保存会话与日志",
        "返回前端展示",
    ]
    y = 130
    previous = None
    for index, label in enumerate(steps):
        box = (500, y, 1000, y + 70)
        rounded_box(draw, box, f"{index + 1}. {label}", fill="#ffffff", outline="#2563eb", font=SMALL)
        if previous:
            arrow(draw, previous, (750, y))
        previous = (750, y + 70)
        y += 100
    save(image, "figure-4-2-chat-flow.png")


def sequence():
    image, draw = canvas()
    title(draw, "问答处理时序图")
    lanes = [
        (180, "浏览器"),
        (500, "C++ 网关"),
        (820, "Python 服务"),
        (1140, "模型接口"),
    ]
    for x, label in lanes:
        rounded_box(draw, (x - 100, 120, x + 100, 180), label, fill="#ffffff", outline="#0f766e", font=SMALL)
        draw.line([(x, 180), (x, 780)], fill="#94a3b8", width=3)
    messages = [
        (180, 500, 260, "POST /api/chat"),
        (500, 820, 360, "转发标准 JSON"),
        (820, 1140, 460, "模型请求"),
        (1140, 820, 560, "模型回答"),
        (820, 500, 640, "保存并返回结果"),
        (500, 180, 720, "HTTP 响应"),
    ]
    for x1, x2, y, label in messages:
        arrow(draw, (x1, y), (x2, y))
        center_text(draw, (min(x1, x2), y - 36, max(x1, x2), y - 6), label, font=SMALL)
    save(image, "figure-4-3-sequence.png")


def er():
    image, draw = canvas()
    title(draw, "系统 E-R 图")
    entities = [
        (120, 190, 390, 310, "用户\nid, username, role", "#fff7ed", "#ea580c"),
        (620, 190, 890, 310, "会话\nid, user_id, title", "#eff6ff", "#2563eb"),
        (1110, 190, 1380, 310, "消息\nsession_id, content", "#f0fdf4", "#16a34a"),
        (365, 560, 635, 680, "系统日志\nlevel, event_type", "#fdf2f8", "#db2777"),
        (865, 560, 1135, 680, "系统配置\nkey, value", "#fefce8", "#ca8a04"),
    ]
    for x1, y1, x2, y2, label, fill, outline in entities:
        draw.rounded_rectangle((x1, y1, x2, y2), radius=24, fill=fill, outline=outline, width=3)
        lines = label.split("\n")
        center_text(draw, (x1, y1 + 18, x2, y1 + 60), lines[0], font=BOLD)
        center_text(draw, (x1, y1 + 66, x2, y1 + 106), lines[1], font=SMALL)
    arrow(draw, (390, 250), (620, 250))
    center_text(draw, (430, 212, 580, 242), "1:N", font=SMALL)
    arrow(draw, (890, 250), (1110, 250))
    center_text(draw, (930, 212, 1070, 242), "1:N", font=SMALL)
    arrow(draw, (255, 310), (500, 560))
    arrow(draw, (755, 310), (500, 560))
    arrow(draw, (1000, 560), (1000, 310))
    save(image, "figure-4-4-er.png")


def main():
    use_case()
    architecture()
    chat_flow()
    sequence()
    er()


if __name__ == "__main__":
    main()
