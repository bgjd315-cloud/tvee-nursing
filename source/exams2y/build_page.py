"""把二技 questions_tagged.csv、章節字典與逐題截圖嵌入網頁範本，輸出 ../二技護理考題分析.html 與 ../site2y/。"""
import base64, csv, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
chapters = json.load(open(os.path.join(HERE, "chapters.json"), encoding="utf-8"))
rows = list(csv.DictReader(open(os.path.join(HERE, "questions_tagged.csv"), encoding="utf-8-sig")))
questions = [[r["題目編號"], int(r["年度"]), r["考科"], int(r["題號"]), r["章節代碼"],
              r["公告答案"], int(r["配分"]), r["題幹摘要"]] for r in rows]

# 逐題截圖：每份試卷一個 JSON（data URI），展開題目時才載入
ASCII = {"專業一": "p1", "專業二": "p2", "國文": "ch", "英文": "en"}
crops = json.load(open(os.path.join(HERE, "crops.json"), encoding="utf-8"))
DATA_DIR = os.path.join(ROOT, "site2y", "data")
os.makedirs(DATA_DIR, exist_ok=True)
bundles = {}


def publish_img(name):
    if not name:
        return None
    y, subj, _ = name.split("-", 2)
    key = f"{y}-{ASCII[subj]}"
    raw = open(os.path.join(HERE, "img", name), "rb").read()
    bundles.setdefault(key, {})[name] = "data:image/png;base64," + base64.b64encode(raw).decode()
    return f"data/{key}.json#{name}"


# 解析：有 explain/<年>-<科>.json 就帶入，否則留空（網頁顯示「解析尚未撰寫」）
ex = {}
for q in questions:
    qid, y, subj, n = q[0], q[1], q[2], q[3]
    path = os.path.join(HERE, "explain", f"{y}-{subj}.json")
    text = ""
    if os.path.exists(path):
        v = json.load(open(path, encoding="utf-8")).get(str(n))
        text = (v[1] if isinstance(v, list) else v) or ""
    c = crops[qid]
    ex[qid] = [text, publish_img(c["img"]), publish_img(c["group"])]

for key, imgs in bundles.items():
    json.dump(imgs, open(os.path.join(DATA_DIR, key + ".json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))

flags_path = os.path.join(HERE, "review_flags.json")
flags = json.load(open(flags_path, encoding="utf-8")) if os.path.exists(flags_path) else {}
notes_path = os.path.join(HERE, "notes.json")
notes = json.load(open(notes_path, encoding="utf-8")) if os.path.exists(notes_path) else {}

data = {"chapters": chapters, "questions": questions, "fixed": [], "ex": ex, "flags": flags, "notes": notes}
tpl = open(os.path.join(HERE, "page_template.html"), encoding="utf-8").read()
out = tpl.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
open(os.path.join(ROOT, "二技護理考題分析.html"), "w", encoding="utf-8").write(out)
open(os.path.join(ROOT, "site2y", "index.html"), "w", encoding="utf-8").write(
    '<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">\n' + out)
print("questions", len(questions), "bytes", len(out.encode("utf-8")), "bundles", len(bundles))
