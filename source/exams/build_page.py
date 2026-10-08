"""把 questions_tagged.csv 與章節字典嵌入分析網頁範本，輸出 ../統測護理考題分析.html。"""
import csv, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

chapters = json.load(open(os.path.join(HERE, "chapters.json"), encoding="utf-8"))
rows = list(csv.DictReader(open(os.path.join(HERE, "questions_tagged.csv"), encoding="utf-8-sig")))

questions = [[r["題目編號"], int(r["年度"]), r["考科"], int(r["題號"]), r["章節代碼"],
              r["公告答案"], int(r["配分"]), r["題幹摘要"]] for r in rows]

# 非選擇題部分不在逐題資料中，以固定配分列入
fixed = [
    {"subject": "國文", "code": "C99", "name": "寫作測驗", "pts": {str(y): 24 for y in range(110, 116)}},
    {"subject": "英文", "code": "E99", "name": "非選擇題（填充、句子重組、中譯英）",
     "pts": {"110": 18, **{str(y): 16 for y in range(111, 116)}}},
]
chapters["國文"]["C99"] = "寫作測驗"
chapters["英文"]["E99"] = "非選擇題（填充、句子重組、中譯英）"

# 逐題截圖與解析：圖檔改用英數檔名複製到 ../site/img，發布時當作附屬檔案
import base64
ASCII = {"專業一": "p1", "專業二": "p2", "國文": "ch", "英文": "en", "數學": "ma"}
crops = json.load(open(os.path.join(HERE, "crops.json"), encoding="utf-8"))
DATA_DIR = os.path.join(ROOT, "site", "data")   # 每份試卷一個 JSON，內含該卷所有截圖（data URI），展開題目時才載入
os.makedirs(DATA_DIR, exist_ok=True)
bundles = {}

def publish_img(name):
    if not name:
        return None
    y, subj, rest = name.split("-", 2)
    key = f"{y}-{ASCII[subj]}"
    raw = open(os.path.join(HERE, "img", name), "rb").read()
    bundles.setdefault(key, {})[name] = "data:image/png;base64," + base64.b64encode(raw).decode()
    return f"data/{key}.json#{name}"

ex = {}
for (y, subj), _ in {(q[1], q[2]): 1 for q in questions}.items():
    for no, v in json.load(open(os.path.join(HERE, "explain", f"{y}-{subj}.json"), encoding="utf-8")).items():
        qid = f"{y}-{subj}-{int(no):02d}"
        c = crops[qid]
        ex[qid] = [v[1] if isinstance(v, list) else v, publish_img(c["img"]), publish_img(c["group"])]

for key, imgs in bundles.items():
    json.dump(imgs, open(os.path.join(DATA_DIR, key + ".json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))

# 複查後建議老師優先覆核的題目：{題目編號: 原因}
flags = json.load(open(os.path.join(HERE, "review_flags.json"), encoding="utf-8"))

# 各章節重點筆記：{章節代碼: {key: [...], trap: [...]}}
notes = json.load(open(os.path.join(HERE, "notes.json"), encoding="utf-8"))

data = {"chapters": chapters, "questions": questions, "fixed": fixed, "ex": ex, "flags": flags, "notes": notes}
tpl = open(os.path.join(HERE, "page_template.html"), encoding="utf-8").read()
out = tpl.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
open(os.path.join(ROOT, "統測護理考題分析.html"), "w", encoding="utf-8").write(out)
print("questions", len(questions), "bytes", len(out.encode("utf-8")))
