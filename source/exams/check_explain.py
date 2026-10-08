"""核對解析檔：每題都有、且解析標註的答案與公告答案一致。"""
import json, glob, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
qs = json.load(open(os.path.join(HERE, "questions.json"), encoding="utf-8"))
key = {(q["year"], q["subject"], q["no"]): q["answer"] for q in qs}
bad = 0
for f in sorted(glob.glob(os.path.join(HERE, "explain", "*.json"))):
    year, subj = os.path.basename(f)[:-5].split("-")
    d = json.load(open(f, encoding="utf-8"))
    n = max(k[2] for k in key if k[0] == int(year) and k[1] == subj)
    for i in range(1, n + 1):
        v = d.get(str(i))
        if v is None:
            print(f, i, "缺解析"); bad += 1; continue
        if isinstance(v, list) and v[0] != key[(int(year), subj, i)]:
            print(f, i, "解析答案", v[0], "公告", key[(int(year), subj, i)]); bad += 1
print("problems", bad)
