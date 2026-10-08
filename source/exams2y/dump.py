"""列出一份試卷的逐題全文與公告答案，供撰寫解析：python dump.py 115 專業二 [起 迄]
題組文章（取自 group_text.json）在該題組第一題前印一次。"""
import json, re, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
y, subj = int(sys.argv[1]), sys.argv[2]
a, b = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (1, 50)
q = json.load(open(os.path.join(HERE, "questions.json"), encoding="utf-8"))
crops = json.load(open(os.path.join(HERE, "crops.json"), encoding="utf-8"))
gtext = json.load(open(os.path.join(HERE, "group_text.json"), encoding="utf-8"))
shown = set()
for x in q:
    if x["year"] == y and x["subject"] == subj and a <= x["no"] <= b:
        g = crops[x["id"]]["group"]
        if g and g not in shown:
            shown.add(g)
            print("\n▲〔" + g + "〕" + gtext.get(g, "") + "\n")
        stem = re.sub(r"\s+", " ", x["stem"])
        opts = " ".join(f"({k}){re.sub(r'\s+', ' ', v).strip()}" for k, v in x["options"].items())
        print(f"{x['no']}【{x['answer']}】{stem} {opts}")
