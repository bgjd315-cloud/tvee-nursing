"""檢查解析檔：每題都有、答案欄與公告答案一致、文字非空。"""
import json, os, glob, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__))
q = {(x["year"], x["subject"], x["no"]): x["answer"] for x in json.load(open(os.path.join(HERE, "questions.json"), encoding="utf-8"))}
bad, done = [], 0
for f in sorted(glob.glob(os.path.join(HERE, "explain", "*.json"))):
    y, s = os.path.basename(f)[:-5].split("-", 1)
    d = json.load(open(f, encoding="utf-8"))
    for n in range(1, 51):
        v = d.get(str(n))
        ans = unicodedata.normalize("NFKC", q[(int(y), s, n)])
        if not v: bad.append(f"{y}-{s}-{n} 缺"); continue
        if v[0] != ans: bad.append(f"{y}-{s}-{n} 答案 {v[0]} ≠ 公告 {ans}")
        if len(v[1]) < 15: bad.append(f"{y}-{s}-{n} 解析太短")
    done += 1
print("files", done, "problems", len(bad)); print("\n".join(bad[:30]))
