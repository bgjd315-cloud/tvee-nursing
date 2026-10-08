"""把測驗中心試題本與公告答案的文字檔切成逐題資料 questions.json。"""
import json, re, glob, os, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
TXT = os.path.join(HERE, "txt")
SUBJECTS = {"01-1": "專業一", "01-2": "專業二", "00-c": "國文", "00-e": "英文"}
# 英文選擇題 110 年 41 題、111 年起 42 題，依公告答案題數決定
COUNT = {}
NOISE = re.compile(r"^(第\s*\d+\s*頁|共\s*\d+\s*頁|-\s*\d+\s*-.*|\d{3}\s*年二技|護理類\s*(專業科目.*|國文|英文)|共同科目\s*(國文|英文)|ˉ|公告試題僅供參考|【以下空白】.*)$")


def parse_answers(path):
    # 公告答案偶有全形字母（如 112 國文第 36 題的「Ｃ」），先轉半形
    toks = [unicodedata.normalize("NFKC", t).strip() for t in open(path, encoding="utf-8").read().split("\n")]
    toks = [t for t in toks if t]
    ans = {}
    i = 0
    while i < len(toks) - 1:
        if toks[i].isdigit() and not toks[i + 1].isdigit() and re.fullmatch(r"[A-E#、或,，]+|送分", toks[i + 1]):
            ans[int(toks[i])] = toks[i + 1]
            i += 2
        else:
            i += 1
    return ans


def parse_paper(path):
    lines = []
    for raw in open(path, encoding="utf-8").read().split("\n"):
        s = raw.strip()
        if not s or NOISE.match(s):
            continue
        lines.append(s)
    text = "\n".join(lines)
    text = re.sub(r"\(\s*([A-D])\s*\)", r"(\1)", text)   # 108 年試題本選項代號內有空格，如「( B)」
    # 只取第 1 題之後的內容
    anchor = text.find("翻閱試題本作答")
    anchor = anchor if anchor >= 0 else text.find("再翻閱試題")
    start = re.compile(r"(?m)^1\.\s*").search(text, max(anchor, 0))
    # 數學試題本前附「參考公式」，公式也從 1. 編號，第 1 題是公式頁之後的下一個 1.
    if "參考公式" in text[max(start.start() - 400, 0):start.start()]:
        start = re.compile(r"(?m)^1\.\s*").search(text, start.end())
    text = text[start.start():]
    qs = {}
    expect = 1
    pos = 0
    marks = []
    while True:
        # 題號後通常有句點；少數題（如 111 英文第 25 題）只印「25 (A)」
        m = re.compile(r"(?m)^%d(\.\s*|\s+(?=\(A\)))" % expect).search(text, pos)
        if not m:
            # 少數試題頁是掃描圖（如 108 國文第 6 頁），跳過缺頁的題號繼續找
            skip = next((k for k in range(expect + 1, expect + 9) if re.compile(r"(?m)^%d\.\s*" % k).search(text, pos)), None)
            if skip is None:
                break
            expect = skip
            continue
        marks.append((expect, m.start(), m.end()))
        pos = m.end()
        expect += 1
    for k, (n, s, e) in enumerate(marks):
        end = marks[k + 1][1] if k + 1 < len(marks) else len(text)
        body = text[e:end].strip()
        # 題組的共同引文（如「▲閱讀下文，回答第45-46題」）會夾在上一題尾端，切開保留
        lead = ""
        g = re.search(r"\n(▲[^\n]*)", body)
        if g:
            lead = body[g.start():].strip()
            body = body[:g.start()].strip()
        opts = dict(re.findall(r"\(([A-D])\)\s*(.+?)(?=\s*\([A-D]\)|\Z)", body.replace("\n", " "), re.S))
        stem = re.split(r"\(A\)", body.replace("\n", " "), maxsplit=1)[0].strip()
        qs[n] = {"stem": stem, "options": opts, "next_group_lead": lead}
    return qs


def main():
    out = []
    for year in range(108, 116):
        for code, subj in SUBJECTS.items():
            paper = os.path.join(TXT, f"{year}-2y-{code}.txt")
            ans = parse_answers(os.path.join(TXT, f"{year}-2y-{code}-standard.txt"))
            qs = parse_paper(paper)
            manual = os.path.join(HERE, f"manual_{year}{code[-1]}.json")
            if os.path.exists(manual):   # 掃描頁的題目以人工轉錄補上
                qs.update({int(k): {**v, "next_group_lead": ""} for k, v in json.load(open(manual, encoding="utf-8")).items()})
            for n in range(1, (COUNT.get(subj) or max(ans)) + 1):
                q = qs.get(n, {"stem": "", "options": {}, "next_group_lead": ""})
                out.append({
                    "id": f"{year}-{subj}-{n:02d}",
                    "year": year, "subject": subj, "no": n,
                    "answer": ans.get(n, ""), "points": 4 if subj == "數學" else 2,
                    "stem": q["stem"], "options": q["options"],
                })
            print(year, subj, "questions", len(qs), "answers", len(ans))
    json.dump(out, open(os.path.join(HERE, "questions.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
