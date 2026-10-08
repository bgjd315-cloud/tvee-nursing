"""（二技版）從測驗中心試題本 PDF 逐題裁切題目圖，題組的共同文章另存一張。

輸出 img/<年度>-<考科>-<題號>.png 與 img/<年度>-<考科>-g<起題>.png，並寫出 crops.json：
{題目編號: {"img": 檔名, "group": 題組圖檔名或 null}}
"""
import io, json, os, re
import pymupdf
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "img")
SUBJECTS = {"01-1": "專業一", "01-2": "專業二", "00-c": "國文", "00-e": "英文"}
TOP, BOTTOM, LEFT, RIGHT = 60, 806, 50, 550   # 頁首頁尾以外的內容區（pt）
DPI = 130

QNUM = re.compile(r"^(\d{1,2})(\s*[\.．]|\s+\(A\))")
GROUP = re.compile(r"^▲")
RANGE = re.compile(r"第\s*(\d+)\s*[-－–~～至]\s*(\d+)\s*題")
SECTION = re.compile(r"^(二、|三、|[ⅠⅡⅢⅣⅤⅥ]\s*[\.．]|(?:I{1,3}|IV|V|VI)\s*[\.．]\s*\S|【以下空白】)")   # 二技英文大題用 ASCII 羅馬數字


def lines_of(doc):
    """依閱讀順序列出 (頁, y0, x0, 文字)，略過封面。"""
    out = []
    for pno in range(1, doc.page_count):
        page = doc[pno]
        for b in page.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                t = "".join(s["text"] for s in l["spans"]).strip()
                x0, y0 = l["bbox"][0], l["bbox"][1]
                if t and TOP < y0 < BOTTOM:
                    out.append((pno, y0, x0, t))
    out.sort(key=lambda r: (r[0], r[1], r[2]))
    return out


def find_marks(lines, nq):
    """回傳依序的邊界：("q", n) 題目起點、("g", (a, b)) 題組文章起點、("s", None) 大題標題。"""
    marks, expect = [], 1
    in_sheet = any("參考公式" in t for _, _, _, t in lines)
    sheet_first_seen = False
    for pno, y, x, t in lines:
        if "以下空白" in t and expect > 1:
            marks.append((pno, y, "s", None))   # 試卷結尾標記置中，不受左邊界限制
            continue
        if x > 75 and not (x <= 85 and GROUP.match(t)):   # 110 英文的 ▲ 縮排到 x≈79
            continue
        m = QNUM.match(t)
        if m and expect < int(m.group(1)) <= min(expect + 8, nq) and re.match(r"^\d{1,2}\.\s*\S", t):
            expect = int(m.group(1))   # 掃描頁（如 108 國文第 6 頁）上的題目抓不到文字，跳過缺號，另以 MANUAL 補裁
        if m and int(m.group(1)) == expect and expect <= nq:
            if in_sheet and expect == 1 and not sheet_first_seen:
                sheet_first_seen = True      # 數學參考公式的 1.，不是題目
                continue
            marks.append((pno, y, "q", expect))
            expect += 1
        elif GROUP.match(t):
            r = RANGE.search(t)
            marks.append((pno, y, "g", (int(r.group(1)), int(r.group(2))) if r else None))
        elif SECTION.match(t) and expect > 1:
            marks.append((pno, y, "s", None))
    return marks


_boxes = {}


def page_boxes(doc, pno):
    """頁面上所有文字行與線條的外框 (y0, y1)。"""
    key = (doc.name, pno)
    if key not in _boxes:
        page = doc[pno]
        out = []
        for b in page.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                if "".join(sp["text"] for sp in l["spans"]).strip():
                    out.append((l["bbox"][1], l["bbox"][3]))
        for d in page.get_drawings():
            r = d["rect"]
            if r.height < 60 and r.x0 >= LEFT - 5:
                out.append((r.y0, r.y1))
        _boxes[key] = out
    return _boxes[key]


def ink_top(doc, pno, y):
    """題號那一行的實際上緣。
    分數、矩陣括號、根號會高出行框：只把與題號行實際重疊（至少 2pt）的文字或線條上緣算進來，最多往上 45pt。
    一般文字行彼此不會重疊 2pt，所以不會沿著文章或圖表一路往上吃到上一題。"""
    boxes = page_boxes(doc, pno)
    line = [b for b in boxes if abs(b[0] - y) < 0.5]
    bottom = max([b[1] for b in line] + [y + 10])
    top = y
    changed = True
    while changed:   # 分段函數的大括號上方還有分子，需再往上接一層（仍要求實際重疊 2pt）
        changed = False
        for b0, b1 in boxes:
            if b0 < top and b1 >= top + 2 and b0 < bottom and y - b0 <= 45:
                top = b0
                changed = True
    return max(top - 2, TOP)


def crop(doc, start, end):
    """從 (頁, y) 裁到 (頁, y)，跨頁時上下拼接。y 為題號行框上緣，實際邊界由 ink_top 決定。"""
    parts = []
    (p0, y0), (p1, y1) = start, end
    for p in range(p0, p1 + 1):
        top = ink_top(doc, p0, y0) if p == p0 else TOP
        bot = (ink_top(doc, p1, y1) if y1 <= BOTTOM else y1 - 2) if p == p1 else BOTTOM
        if p == p0 == p1:
            bot = max(bot, y0 + 12)   # 兩個標記緊貼、中間沒有空白列時，至少保留起點那一行
        if bot - top < 6:
            continue
        pix = doc[p].get_pixmap(clip=pymupdf.Rect(LEFT, top, RIGHT, bot), dpi=DPI, colorspace=pymupdf.csGRAY)
        parts.append(Image.open(io.BytesIO(pix.tobytes("png"))))
    w = max(im.width for im in parts)
    img = Image.new("L", (w, sum(im.height for im in parts)), 255)
    y = 0
    for im in parts:
        img.paste(im, (0, y))
        y += im.height
    return img


def clip_text(doc, start, end):
    """裁切範圍內的文字（題組文章寫解析時參考）。"""
    (p0, y0), (p1, y1) = start, end
    out = []
    for p in range(p0, p1 + 1):
        top = ink_top(doc, p0, y0) if p == p0 else TOP
        bot = (ink_top(doc, p1, y1) if y1 <= BOTTOM else y1 - 2) if p == p1 else BOTTOM
        if bot - top >= 6:
            out.append(doc[p].get_text("text", clip=pymupdf.Rect(LEFT, top, RIGHT, bot)))
    return re.sub(r"\s+", " ", " ".join(out)).strip()


# 掃描頁的題目：{題目編號或題組: (頁, 上緣 pt, 下緣 pt, 題組圖檔)}，座標依頁面圖目測
CODE = {v: k for k, v in SUBJECTS.items()}
MANUAL = {
    "108-國文-g31": (5, 72, 185, None),
    "108-國文-31": (5, 185, 228, "108-國文-g31.png"),
    "108-國文-32": (5, 228, 304, "108-國文-g31.png"),
    "108-國文-33": (5, 304, 334, "108-國文-g31.png"),
    "108-國文-g34": (5, 334, 588, None),
    "108-國文-34": (5, 588, 657, "108-國文-g34.png"),
    "108-國文-35": (5, 657, 705, "108-國文-g34.png"),
    "108-國文-36": (5, 705, 770, "108-國文-g34.png"),
}


def crop_raw(doc, pno, top, bot):
    pix = doc[pno].get_pixmap(clip=pymupdf.Rect(LEFT, top, RIGHT, bot), dpi=DPI, colorspace=pymupdf.csGRAY)
    return Image.open(io.BytesIO(pix.tobytes("png")))


def save(img, name):
    # 修掉下方空白（頁尾留白或題組間距），保留 8px
    box = Image.eval(img, lambda v: 255 - v).point(lambda v: 255 if v > 40 else 0).getbbox()
    if box:
        img = img.crop((0, 0, img.width, min(img.height, box[3] + 8)))
    img.quantize(colors=16).save(os.path.join(OUT, name), optimize=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    qs = json.load(open(os.path.join(HERE, "questions.json"), encoding="utf-8"))
    count = {}
    for q in qs:
        count[(q["year"], q["subject"])] = max(count.get((q["year"], q["subject"]), 0), q["no"])
    result = {}
    group_text = {}
    for year in range(108, 116):
        for code, subj in SUBJECTS.items():
            doc = pymupdf.open(os.path.join(HERE, f"{year}-2y-{code}.pdf"))
            nq = count[(year, subj)]
            lines = lines_of(doc)
            marks = find_marks(lines, nq)
            last = lines[-1]
            stop = (last[0], BOTTOM + 2)
            got = 0
            pending_group = None
            for i, (pno, y, kind, val) in enumerate(marks):
                nxt = (marks[i + 1][0], marks[i + 1][1]) if i + 1 < len(marks) else stop
                if nxt[0] - pno >= 2:
                    nxt = (pno, BOTTOM + 2)   # 中間隔了一整頁（掃描頁），只裁到本頁底
                if kind == "g":
                    gname = None
                    if val is None or val[0] <= nq:
                        first = val[0] if val else (next((m[3] for m in marks[i:] if m[2] == "q"), 0))
                        gname = f"{year}-{subj}-g{first:02d}.png"
                        save(crop(doc, (pno, y), nxt), gname)
                        group_text[gname] = clip_text(doc, (pno, y), nxt)
                    pending_group = (val, gname)
                elif kind == "q":
                    name = f"{year}-{subj}-{val:02d}.png"
                    save(crop(doc, (pno, y), nxt), name)
                    group = None
                    if pending_group:
                        rng, gname = pending_group
                        if rng is None or rng[0] <= val <= rng[1]:
                            group = gname
                        if rng and val >= rng[1]:
                            pending_group = None
                    result[f"{year}-{subj}-{val:02d}"] = {"img": name, "group": group}
                    got += 1
                elif kind == "s":
                    pending_group = None
            print(year, subj, "cropped", got, "/", nq)
    for key, (pno, y0, y1, group) in MANUAL.items():
        y, subj, n = key.split("-")
        doc = pymupdf.open(os.path.join(HERE, f"{y}-2y-{CODE[subj]}.pdf"))
        img = crop_raw(doc, pno, y0, y1)
        name = f"{key}.png" if not n.startswith("g") else f"{y}-{subj}-{n}.png"
        save(img, name)
        if not n.startswith("g"):
            result[key] = {"img": name, "group": group}
    json.dump(result, open(os.path.join(HERE, "crops.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump(group_text, open(os.path.join(HERE, "group_text.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)


if __name__ == "__main__":
    main()
