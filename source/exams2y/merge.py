"""把標準輸入的解析 JSON 併入 explain/<年>-<科>.json：python merge.py 115 專業二 < part.json"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(HERE, "explain", f"{sys.argv[1]}-{sys.argv[2]}.json")
cur = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
cur.update(json.loads(sys.stdin.buffer.read().decode("utf-8")))
cur = dict(sorted(cur.items(), key=lambda kv: int(kv[0])))
json.dump(cur, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(sys.argv[1], sys.argv[2], len(cur))
