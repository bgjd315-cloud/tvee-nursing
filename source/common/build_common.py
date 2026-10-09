"""由護理類兩個網頁（統測 exams/、二技 exams2y/）改寫出「共同科目 國文、英文」考題分析網站，輸出到 ../site_common/。
統測、二技的國文與英文是各群類共用的試卷，題目、章節、解析直接沿用護理類資料，只保留這兩科，並拿掉目標校與採計權重。
護理類範本或資料更新後，重跑 exams/build_page.py、exams2y/make_template.py + build_page.py，再跑本檔即可同步。"""
import base64, csv, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "site_common")
SITE = "https://bgjd315-cloud.github.io/tvee-common/"
KEEP = ("國文", "英文")
ASCII = {"國文": "ch", "英文": "en"}
HEAD = '<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">\n'

# 兩個版本的差異設定
VARIANTS = {
    "tvee": dict(
        src="exams", outdir=OUT, years="110–115", n_years="六年",
        eyebrow="四技二專統測 · 共同科目 · 110–115 學年度",
        title="統測國文英文考題分析",
        intro="依技專校院入學測驗中心公告的 110–115 學年度四技二專統測共同科目試題（國文、英文選擇題共 {n} 題，各群類共用），整理各題型的出題趨勢、逐題截圖與解析，排出準備優先順序。",
        sibling=f'也有二技版：<a href="{SITE}erji/">二技國文英文考題分析 →</a>',
        store="tvee-common",
        exam_word="統測",
        note=[
            "試題與公告答案來自技專校院入學測驗中心公告的 110–115 學年度四技二專統一入學測驗共同科目國文、英文試題，所有群類共用同一份試卷。",
            "國文依題型分類、英文依試題本標示的大題分類，為 Claude 依題意初標的暫定分類，國文需任課老師覆核。",
            "逐題解析由 Claude 撰寫，已逐題比對公告答案，並經過一次全面複查，但推理與說明仍可能有誤，使用前請任課老師覆核。其中 <span id=\"rv-count\"></span> 題標示「建議覆核」，展開後可看到原因。題目截圖取自測驗中心公告的試題本。",
            "國文寫作（每年 24 分）與英文非選擇題（110 年 18 分、其後 16 分）不在逐題資料中，以固定配分列入排序。各校對國文、英文的採計倍率不同，本頁以兩科同等權重排序。",
        ],
    ),
    "erji": dict(
        src="exams2y", outdir=os.path.join(OUT, "erji"), years="108–115", n_years="八年",
        eyebrow="二技統一入學測驗 · 共同科目 · 108–115 學年度",
        title="二技國文英文考題分析",
        intro="依技專校院入學測驗中心公告的 108–115 學年度二技統一入學測驗共同科目試題（國文、英文選擇題共 {n} 題，各類別共用），整理各題型的出題趨勢、逐題截圖與解析，排出準備優先順序。",
        sibling=f'也有統測（四技）版：<a href="{SITE}">統測國文英文考題分析 →</a>',
        store="tvee2y-common",
        exam_word="二技統測",
        note=[
            "試題與公告答案來自技專校院入學測驗中心公告的 108–115 學年度二技統一入學測驗共同科目國文、英文試題，所有類別共用同一份試卷。108 年國文第 31–36 題所在頁為掃描圖，截圖依頁面位置人工裁切。",
            "國文依題型分類、英文依試題本的大題分類（字彙、對話、綜合測驗、閱讀測驗），為 Claude 依題意初標的暫定分類，國文需任課老師覆核。",
            "逐題解析由 Claude 撰寫，已逐題比對公告答案，但推理與說明仍可能有誤，使用前請任課老師覆核。其中 <span id=\"rv-count\"></span> 題標示「建議覆核」，展開後可看到原因。題目截圖取自測驗中心公告的試題本。",
            "二技國文、英文全為選擇題，每科 50 題、每題 2 分。各校對國文、英文的採計倍率不同，本頁以兩科同等權重排序。",
        ],
    ),
}


def rep(s, old, new, count=1):
    assert old in s, old[:80]
    return s.replace(old, new) if count == 0 else s.replace(old, new, count)


def sub(s, pat, new, flags=0):
    s2, n = re.subn(pat, new, s, count=1, flags=flags)
    assert n == 1, pat[:80]
    return s2


def template(v, n):
    s = open(os.path.join(ROOT, v["src"], "page_template.html"), encoding="utf-8").read()
    # 標題與說明
    s = sub(s, r"<title>[^<]*</title>", f"<title>{v['title']}</title>")
    s = sub(s, r'<span class="eyebrow">[^<]*</span>', f'<span class="eyebrow">{v["eyebrow"]}</span>')
    s = sub(s, r"<h1>[^<]*</h1>", f"<h1>{v['title']}</h1>")
    s = sub(s, r'(</h1>\s*<p class="muted">)[^<]*(</p>)', lambda m: m.group(1) + v["intro"].format(n=f"{n:,}") + m.group(2))
    s = sub(s, r'<p class="sibling">.*?</p>', f'<p class="sibling">{v["sibling"]}</p>')
    # 不選學校：隱藏目標校控制列與各科權重欄，優先清單佔滿整列
    s = rep(s, "</style>", ".controls[aria-label=\"選擇目標校\"], .grid2 > section:first-child { display: none; }\n.grid2 { grid-template-columns: minmax(0, 1fr) !important; }\n</style>")
    s = sub(s, r"依「[^」]*平均配分 × 近三年趨勢 × 該科權重」排序。「占總成績」是該章每年平均配分換算成總成績的百分比。",
            f"依「{v['n_years']}平均配分 × 近三年趨勢」排序。「占兩科總分」是該題型每年平均配分占國文、英文兩科總分的百分比。")
    s = rep(s, "<th>占總成績</th>", "<th>占兩科總分</th>")
    s = sub(s, r"依上方選的目標校(與入學管道)?，排出到[^統二]*(二技)?統測前的每週進度", f"依國文、英文各題型的優先分數，排出到{v['exam_word']}前的每週進度")
    s = sub(s, r'(<section class="note" aria-label="資料說明">\s*<div class="sec-head"[^\n]*\n).*?(\s*</section>)',
            lambda m: m.group(1) + "\n".join(f"    <p>{p}</p>" for p in v["note"]) + m.group(2), flags=re.S)
    # 只留國文、英文；單一虛擬「學校」讓兩科權重各半
    s = sub(s, r"const SUBJ = \[.*?\];", "const SUBJ = [\n  { key: '國文', label: '國文' },\n  { key: '英文', label: '英文' },\n];", flags=re.S)
    s = sub(s, r"const SCHOOLS = \[.*?\n\];(\nfor \(const sc of SCHOOLS\)[^\n]*)?",
            "const SCHOOLS = [\n  { id: 'common', name: '國文、英文', full: '共同科目',\n"
            "    apply: { share: 100, w: [1, 1], quota: '', screen: '', other: '', formula: '', tie: '' },\n"
            "    dist: { w: [1, 1], quota: '' } },\n];", flags=re.S)
    s = sub(s, r"const state = \{ schools: new Set\(\['[^']*'\]\), mode: 'apply', subj: '[^']*',(.*?)pfilter: 'pro',",
            r"const state = { schools: new Set(['common']), mode: 'dist', subj: '國文',\1pfilter: 'all',")
    s = sub(s, r"const PFILTERS = \[.*?\];", "const PFILTERS = [{ id: 'all', label: '兩科混排' }, ...SUBJ.map(s => ({ id: s.key, label: s.label }))];")
    s = sub(s, r"if \(!state\.schools\.size\) state\.schools\.add\('[^']*'\);", "state.schools = new Set(['common']); state.mode = 'dist';")
    s = rep(s, "warn.hidden = state.pfilter !== 'all';", "warn.hidden = true;")
    s = rep(s, "const out = [0, 0, 0, 0, 0];", "const out = SUBJ.map(() => 0);") if "const out = [0, 0, 0, 0, 0];" in s else s
    s = sub(s, r"sum\.innerHTML = `\$\{esc\(sel\)\}・[^，]*，共", "sum.innerHTML = `國文、英文，共")
    s = re.sub(r"'tvee2?y?-nursing", f"'{v['store']}", s)
    # 統測範本的 5 科陣列寫法改為依 SUBJ 長度
    left = [w for w in ("數學", "專業一", "專業二", "專一", "專二", "護理", "甄選", "分發", "目標校") if w in re.sub(r"<style>.*?</style>", "", s, flags=re.S).split("const D =")[0]]
    if left:
        print("  版面文字仍含：", left)
    return s


def build(key, v):
    src = os.path.join(ROOT, v["src"])
    chapters = {k: c for k, c in json.load(open(os.path.join(src, "chapters.json"), encoding="utf-8")).items() if k in KEEP}
    rows = list(csv.DictReader(open(os.path.join(src, "questions_tagged.csv"), encoding="utf-8-sig")))
    questions = [[r["題目編號"], int(r["年度"]), r["考科"], int(r["題號"]), r["章節代碼"], r["公告答案"], int(r["配分"]), r["題幹摘要"]]
                 for r in rows if r["考科"] in KEEP]
    crops = json.load(open(os.path.join(src, "crops.json"), encoding="utf-8"))
    os.makedirs(os.path.join(v["outdir"], "data"), exist_ok=True)
    bundles = {}

    def publish_img(name):
        if not name:
            return None
        y, subj, _ = name.split("-", 2)
        bk = f"{y}-{ASCII[subj]}"
        raw = open(os.path.join(src, "img", name), "rb").read()
        bundles.setdefault(bk, {})[name] = "data:image/png;base64," + base64.b64encode(raw).decode()
        return f"data/{bk}.json#{name}"

    ex = {}
    for q in questions:
        qid, y, subj, n = q[0], q[1], q[2], q[3]
        e = json.load(open(os.path.join(src, "explain", f"{y}-{subj}.json"), encoding="utf-8")).get(str(n))
        c = crops[qid]
        ex[qid] = [(e[1] if isinstance(e, list) else e) or "", publish_img(c["img"]), publish_img(c["group"])]
    for bk, imgs in bundles.items():
        json.dump(imgs, open(os.path.join(v["outdir"], "data", bk + ".json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))

    fixed = []
    if key == "tvee":   # 統測非選擇題以固定配分列入（與護理版相同）
        fixed = [
            {"subject": "國文", "code": "C99", "name": "寫作測驗", "pts": {str(y): 24 for y in range(110, 116)}},
            {"subject": "英文", "code": "E99", "name": "非選擇題（填充、句子重組、中譯英）", "pts": {"110": 18, **{str(y): 16 for y in range(111, 116)}}},
        ]
        chapters["國文"]["C99"] = "寫作測驗"
        chapters["英文"]["E99"] = "非選擇題（填充、句子重組、中譯英）"
    load = lambda name: json.load(open(os.path.join(src, name), encoding="utf-8")) if os.path.exists(os.path.join(src, name)) else {}
    flags = {k: t for k, t in load("review_flags.json").items() if k.split("-")[1] in KEEP}
    codes = {code for subj in chapters.values() for code in subj}
    notes = {k: t for k, t in load("notes.json").items() if k in codes}

    data = {"chapters": chapters, "questions": questions, "fixed": fixed, "ex": ex, "flags": flags, "notes": notes}
    out = template(v, len(questions)).replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    open(os.path.join(v["outdir"], "index.html"), "w", encoding="utf-8").write(HEAD + out)
    print(key, "questions", len(questions), "flags", len(flags), "notes", len(notes), "bundles", len(bundles), "bytes", len(out.encode()))


for key, v in VARIANTS.items():
    build(key, v)
