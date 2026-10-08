"""套用複查結果：python apply_review.py <批次.json>

批次檔格式：{"<年度>-<考科>": {"fix": {"題號": "新解析"}, "flag": {"題號": "建議覆核的原因"}}}
- fix：改寫解析文字（答案不變，仍由 check_explain.py 比對公告答案）
- flag：寫入 review_flags.json，網頁與講義會在該題標示「建議優先覆核」
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FLAGS = os.path.join(HERE, "review_flags.json")

batch = json.load(open(sys.argv[1], encoding="utf-8"))
flags = json.load(open(FLAGS, encoding="utf-8")) if os.path.exists(FLAGS) else {}
for paper, ops in batch.items():
    year, subj = paper.split("-", 1)
    path = os.path.join(HERE, "explain", f"{paper}.json")
    ex = json.load(open(path, encoding="utf-8"))
    for no, text in ops.get("fix", {}).items():
        v = ex[no]
        ex[no] = [v[0], text] if isinstance(v, list) else text
    for no, note in ops.get("flag", {}).items():
        flags[f"{year}-{subj}-{int(no):02d}"] = note
    with open(path, "w", encoding="utf-8") as f:
        f.write("{\n" + ",\n".join(f"{json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)}" for k, v in ex.items()) + "\n}\n")
    print(paper, "fix", len(ops.get("fix", {})), "flag", len(ops.get("flag", {})))
json.dump(dict(sorted(flags.items())), open(FLAGS, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("flags total", len(flags))
