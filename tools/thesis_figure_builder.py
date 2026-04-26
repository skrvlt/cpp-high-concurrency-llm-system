from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
FIGURE_DIR = ROOT / "output" / "figures"

CANVAS_WIDTH = 1600
CANVAS_HEIGHT = 1000
BG = "white"
FG = "black"
FILL = "#f5f5f5"


def _load_font(size: int, bold: bool = False):
    candidates = []
    if bold:
        candidates.extend(
            [
                Path("C:/Windows/Fonts/msyhbd.ttc"),
                Path("C:/Windows/Fonts/simhei.ttf"),
            ]
        )
    candidates.extend(
        [
            Path("C:/Windows/Fonts/msyh.ttc"),
            Path("C:/Windows/Fonts/simsun.ttc"),
            Path("C:/Windows/Fonts/simhei.ttf"),
        ]
    )
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


FONT_TITLE = _load_font(36, bold=True)
FONT_LABEL = _load_font(24, bold=False)
FONT_SMALL = _load_font(20, bold=False)
FONT_CAPTION = _load_font(18, bold=False)


def _new_canvas():
    image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    return image, draw


def _text_size(draw: ImageDraw.ImageDraw, text: str, font) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    if not text:
        return [""]
    lines: list[str] = []
    current = ""
    for char in text:
        candidate = current + char
        width, _ = _text_size(draw, candidate, font)
        if current and width > max_width:
            lines.append(current)
            current = char
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def _draw_centered_text(draw, box, text, font=FONT_LABEL):
    x1, y1, x2, y2 = box
    lines = _wrap_text(draw, text, font, x2 - x1 - 20)
    line_height = _text_size(draw, "高", font)[1] + 6
    total_height = line_height * len(lines)
    current_y = y1 + (y2 - y1 - total_height) / 2
    for line in lines:
        width, height = _text_size(draw, line, font)
        draw.text((x1 + (x2 - x1 - width) / 2, current_y), line, fill=FG, font=font)
        current_y += max(height, line_height)


def _draw_left_text(draw, box, text, font=FONT_LABEL, padding: int = 14):
    x1, y1, x2, y2 = box
    lines = _wrap_text(draw, text, font, x2 - x1 - padding * 2)
    line_height = _text_size(draw, "高", font)[1] + 6
    current_y = y1 + padding
    for line in lines:
        draw.text((x1 + padding, current_y), line, fill=FG, font=font)
        current_y += line_height


def _draw_actor(draw, center_x: int, top_y: int, label: str):
    r = 16
    draw.ellipse((center_x - r, top_y, center_x + r, top_y + r * 2), outline=FG, width=3)
    draw.line((center_x, top_y + 32, center_x, top_y + 95), fill=FG, width=3)
    draw.line((center_x - 30, top_y + 55, center_x + 30, top_y + 55), fill=FG, width=3)
    draw.line((center_x, top_y + 95, center_x - 28, top_y + 135), fill=FG, width=3)
    draw.line((center_x, top_y + 95, center_x + 28, top_y + 135), fill=FG, width=3)
    _draw_centered_text(draw, (center_x - 90, top_y + 145, center_x + 90, top_y + 200), label, FONT_LABEL)


def _draw_ellipse(draw, box, text):
    draw.ellipse(box, outline=FG, width=3, fill=FILL)
    _draw_centered_text(draw, box, text, FONT_LABEL)


def _draw_rect(draw, box, text, fill=FILL):
    draw.rounded_rectangle(box, radius=12, outline=FG, width=3, fill=fill)
    _draw_centered_text(draw, box, text, FONT_LABEL)


def _draw_diamond(draw, box, text):
    x1, y1, x2, y2 = box
    points = [((x1 + x2) / 2, y1), (x2, (y1 + y2) / 2), ((x1 + x2) / 2, y2), (x1, (y1 + y2) / 2)]
    draw.polygon(points, outline=FG, fill=FILL, width=3)
    _draw_centered_text(draw, box, text, FONT_LABEL)


def _draw_arrow(draw, start, end, label: str | None = None):
    draw.line((start, end), fill=FG, width=3)
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = max((dx * dx + dy * dy) ** 0.5, 1)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    arrow_len = 16
    arrow_width = 8
    p1 = (end[0] - ux * arrow_len + px * arrow_width, end[1] - uy * arrow_len + py * arrow_width)
    p2 = (end[0] - ux * arrow_len - px * arrow_width, end[1] - uy * arrow_len - py * arrow_width)
    draw.polygon([end, p1, p2], fill=FG)
    if label:
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2 - 26
        width, height = _text_size(draw, label, FONT_SMALL)
        draw.rectangle((mid_x - width / 2 - 8, mid_y - 4, mid_x + width / 2 + 8, mid_y + height + 4), fill=BG)
        draw.text((mid_x - width / 2, mid_y), label, fill=FG, font=FONT_SMALL)


def _draw_vertical_lifeline(draw, x: int, top: int, bottom: int, label: str):
    _draw_rect(draw, (x - 80, top, x + 80, top + 50), label, fill="#fafafa")
    segment = 12
    current = top + 50
    while current < bottom:
        draw.line((x, current, x, min(current + segment, bottom)), fill=FG, width=2)
        current += segment * 2


def _save(image: Image.Image, target: Path):
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target)


def _figure_3_1(target: Path):
    image, draw = _new_canvas()
    _draw_centered_text(draw, (0, 20, CANVAS_WIDTH, 90), "系统角色与核心用例图", FONT_TITLE)
    draw.rectangle((320, 120, 1280, 860), outline=FG, width=3)
    _draw_centered_text(draw, (700, 120, 900, 170), "交互系统", FONT_LABEL)

    actors = [
        (120, 230, "普通用户"),
        (120, 520, "业务管理人员"),
        (1480, 360, "系统管理员"),
    ]
    for x, y, label in actors:
        _draw_actor(draw, x, y, label)

    use_cases = {
        "用户登录": (520, 190, 760, 280),
        "智能问答": (520, 340, 760, 430),
        "查看历史记录": (520, 490, 760, 580),
        "查看系统概览": (860, 220, 1140, 310),
        "查看运行日志": (860, 380, 1140, 470),
        "配置维护": (860, 540, 1140, 630),
    }
    for label, box in use_cases.items():
        _draw_ellipse(draw, box, label)

    _draw_arrow(draw, (170, 260), (520, 235))
    _draw_arrow(draw, (170, 290), (520, 385))
    _draw_arrow(draw, (170, 320), (520, 535))
    _draw_arrow(draw, (170, 550), (520, 535))
    _draw_arrow(draw, (170, 580), (860, 265))
    _draw_arrow(draw, (1430, 420), (1140, 265))
    _draw_arrow(draw, (1430, 450), (1140, 425))
    _draw_arrow(draw, (1430, 480), (1140, 585))
    _save(image, target)


def _flow_blocks(draw, blocks, arrows):
    for shape, box, label in blocks:
        if shape == "terminator":
            draw.rounded_rectangle(box, radius=28, outline=FG, width=3, fill="#fafafa")
            _draw_centered_text(draw, box, label, FONT_LABEL)
        elif shape == "process":
            _draw_rect(draw, box, label)
        else:
            _draw_diamond(draw, box, label)
    for start, end, label in arrows:
        _draw_arrow(draw, start, end, label)


def _figure_3_2(target: Path):
    image, draw = _new_canvas()
    _draw_centered_text(draw, (0, 20, CANVAS_WIDTH, 90), "用户问答业务流程图", FONT_TITLE)
    blocks = [
        ("terminator", (640, 110, 960, 180), "开始"),
        ("process", (590, 220, 1010, 300), "用户登录并进入问答页面"),
        ("process", (590, 340, 1010, 420), "输入问题并提交请求"),
        ("process", (590, 460, 1010, 540), "C++ 网关接收请求并转发"),
        ("process", (590, 580, 1010, 660), "Python 服务拼接上下文并调用模型"),
        ("process", (590, 700, 1010, 780), "保存问答记录并返回结果"),
        ("diamond", (580, 820, 1020, 910), "是否继续提问"),
        ("terminator", (1120, 830, 1440, 900), "结束"),
    ]
    arrows = [
        ((800, 180), (800, 220), None),
        ((800, 300), (800, 340), None),
        ((800, 420), (800, 460), None),
        ((800, 540), (800, 580), None),
        ((800, 660), (800, 700), None),
        ((800, 780), (800, 820), None),
        ((1020, 865), (1120, 865), "否"),
        ((580, 865), (470, 865), "是"),
        ((470, 865), (470, 380), None),
        ((470, 380), (590, 380), None),
    ]
    _flow_blocks(draw, blocks, arrows)
    _save(image, target)


def _figure_3_3(target: Path):
    image, draw = _new_canvas()
    _draw_centered_text(draw, (0, 20, CANVAS_WIDTH, 90), "管理员运维业务流程图", FONT_TITLE)
    blocks = [
        ("terminator", (630, 110, 970, 180), "开始"),
        ("process", (580, 220, 1020, 300), "管理员登录后台"),
        ("diamond", (560, 340, 1040, 430), "权限校验是否通过"),
        ("process", (210, 500, 610, 580), "查看系统概览与运行日志"),
        ("process", (760, 500, 1190, 580), "修改配置参数"),
        ("process", (760, 630, 1190, 710), "服务端保存配置并写入日志"),
        ("terminator", (1230, 640, 1490, 710), "结束"),
        ("terminator", (200, 350, 450, 420), "拒绝访问"),
    ]
    arrows = [
        ((800, 180), (800, 220), None),
        ((800, 300), (800, 340), None),
        ((560, 385), (450, 385), "否"),
        ((1040, 385), (1220, 385), "是"),
        ((1220, 385), (1220, 540), None),
        ((1220, 540), (1190, 540), None),
        ((800, 430), (800, 500), None),
        ((800, 580), (800, 630), None),
        ((1190, 670), (1230, 670), None),
        ((560, 385), (410, 385), None),
    ]
    _flow_blocks(draw, blocks, arrows)
    _draw_arrow(draw, (800, 430), (410, 540), "查看")
    _save(image, target)


def _figure_4_1(target: Path):
    image, draw = _new_canvas()
    _draw_centered_text(draw, (0, 20, CANVAS_WIDTH, 90), "系统总体结构图", FONT_TITLE)
    _draw_rect(draw, (90, 350, 350, 470), "Web 前端")
    _draw_rect(draw, (470, 280, 770, 420), "C++ 高并发接入层\nSocket / Epoll / Reactor / 线程池")
    _draw_rect(draw, (470, 520, 770, 660), "Python FastAPI 服务层\n登录 / 问答 / 历史 / 管理接口")
    _draw_rect(draw, (900, 200, 1210, 340), "大语言模型接口")
    _draw_rect(draw, (900, 420, 1210, 560), "MySQL 数据库")
    _draw_rect(draw, (900, 640, 1210, 780), "日志与配置存储")
    _draw_rect(draw, (1310, 420, 1510, 560), "部署环境\nWindows / Linux / WSL")
    _draw_arrow(draw, (350, 410), (470, 350), "HTTP")
    _draw_arrow(draw, (620, 420), (620, 520), "业务转发")
    _draw_arrow(draw, (770, 320), (900, 270), "模型调用")
    _draw_arrow(draw, (770, 570), (900, 490), "数据读写")
    _draw_arrow(draw, (770, 620), (900, 710), "日志落盘")
    _draw_arrow(draw, (1210, 490), (1310, 490), "跨环境运行")
    _save(image, target)


def _figure_4_2(target: Path):
    image, draw = _new_canvas()
    _draw_centered_text(draw, (0, 20, CANVAS_WIDTH, 90), "智能问答处理流程图", FONT_TITLE)
    blocks = [
        ("terminator", (620, 110, 980, 180), "接收问答请求"),
        ("process", (560, 230, 1040, 310), "网关解析 HTTP 报文并校验路由"),
        ("diamond", (540, 360, 1060, 450), "用户 Token 与参数是否合法"),
        ("process", (560, 500, 1040, 580), "Python 服务读取会话上下文"),
        ("process", (560, 620, 1040, 700), "封装 Prompt 并调用模型接口"),
        ("process", (560, 740, 1040, 820), "保存问答记录与日志"),
        ("terminator", (1130, 750, 1450, 820), "返回答案"),
        ("terminator", (150, 370, 430, 440), "返回错误"),
    ]
    arrows = [
        ((800, 180), (800, 230), None),
        ((800, 310), (800, 360), None),
        ((540, 405), (430, 405), "否"),
        ((1060, 405), (1200, 405), "是"),
        ((1200, 405), (1200, 540), None),
        ((1200, 540), (1040, 540), None),
        ((800, 580), (800, 620), None),
        ((800, 700), (800, 740), None),
        ((1040, 780), (1130, 780), None),
    ]
    _flow_blocks(draw, blocks, arrows)
    _save(image, target)


def _figure_4_3(target: Path):
    image, draw = _new_canvas()
    _draw_centered_text(draw, (0, 20, CANVAS_WIDTH, 90), "问答处理时序图", FONT_TITLE)
    lanes = [
        (220, "浏览器"),
        (520, "C++ 网关"),
        (820, "Python 服务"),
        (1120, "大模型接口"),
        (1420, "MySQL"),
    ]
    for x, label in lanes:
        _draw_vertical_lifeline(draw, x, 120, 900, label)

    messages = [
        ((220, 220), (520, 220), "提交问答请求"),
        ((520, 290), (820, 290), "转发 /api/chat"),
        ((820, 360), (1420, 360), "读取会话历史"),
        ((1420, 430), (820, 430), "返回上下文"),
        ((820, 500), (1120, 500), "调用模型生成答案"),
        ((1120, 570), (820, 570), "返回模型结果"),
        ((820, 640), (1420, 640), "写入消息与日志"),
        ((820, 720), (520, 720), "返回 JSON 响应"),
        ((520, 790), (220, 790), "显示问答结果"),
    ]
    for start, end, label in messages:
        _draw_arrow(draw, start, end, label)
    _save(image, target)


def _draw_entity(draw, box, title: str, fields: list[str]):
    x1, y1, x2, y2 = box
    draw.rectangle(box, outline=FG, width=3, fill="#fcfcfc")
    draw.line((x1, y1 + 52, x2, y1 + 52), fill=FG, width=3)
    _draw_centered_text(draw, (x1, y1, x2, y1 + 52), title, FONT_LABEL)
    current_y = y1 + 62
    for field in fields:
        draw.text((x1 + 12, current_y), field, fill=FG, font=FONT_SMALL)
        current_y += 28


def _figure_4_4(target: Path):
    image, draw = _new_canvas()
    _draw_centered_text(draw, (0, 20, CANVAS_WIDTH, 90), "系统 E-R 图", FONT_TITLE)
    _draw_entity(draw, (120, 220, 420, 440), "用户 User", ["user_id (PK)", "username", "password", "role", "created_at"])
    _draw_entity(draw, (560, 180, 900, 430), "会话 Session", ["session_id (PK)", "user_id (FK)", "title", "created_at", "updated_at"])
    _draw_entity(draw, (1030, 180, 1420, 490), "消息 Message", ["message_id (PK)", "session_id (FK)", "sender", "content", "created_at"])
    _draw_entity(draw, (560, 560, 900, 790), "日志 Log", ["log_id (PK)", "user_id (FK)", "action", "level", "created_at"])
    _draw_entity(draw, (1030, 610, 1420, 810), "配置 Config", ["config_id (PK)", "config_key", "config_value", "updated_at"])

    _draw_arrow(draw, (420, 300), (560, 300), "1 : N")
    _draw_arrow(draw, (900, 300), (1030, 300), "1 : N")
    _draw_arrow(draw, (300, 440), (700, 560), "1 : N")
    _draw_arrow(draw, (900, 690), (1030, 690), "1 : 1")
    _save(image, target)


FIGURE_BUILDERS = {
    "图3-1": _figure_3_1,
    "图3-2": _figure_3_2,
    "图3-3": _figure_3_3,
    "图4-1": _figure_4_1,
    "图4-2": _figure_4_2,
    "图4-3": _figure_4_3,
    "图4-4": _figure_4_4,
}


def ensure_all_figures_generated(figure_dir: Path | None = None):
    target_dir = figure_dir or FIGURE_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    for figure_id, builder in FIGURE_BUILDERS.items():
        builder(target_dir / f"{figure_id}.png")


if __name__ == "__main__":
    ensure_all_figures_generated()
