"""由統測（四技）網頁範本改寫出二技版範本 page_template.html。
統測範本更新後重跑本檔即可同步版面與功能；二技特有的文字與設定都集中在這裡。"""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "..", "exams", "page_template.html"), encoding="utf-8").read()
s = src


def rep(old, new, count=1):
    global s
    assert old in s, old[:80]
    s = s.replace(old, new) if count == 0 else s.replace(old, new, count)


# ---- 標題與說明 ----
rep("<title>統測護理類考題分析</title>", "<title>二技護理類考題分析</title>")
rep('<span class="eyebrow">衛生與護理類 · 四技二專 · 110–115 學年度</span>', '<span class="eyebrow">護理類 · 二技 · 108–115 學年度</span>')
rep("<h1>統測護理類考題分析</h1>", "<h1>二技護理類考題分析</h1>")
rep("依技專校院入學測驗中心公告的六年試題（五科選擇題共 1,229 題），結合 115 學年度招生簡章的統測採計方式，排出目標校的準備優先順序。",
    "依技專校院入學測驗中心公告的八年二技統一入學測驗護理類試題（四科選擇題共 1,600 題），結合 115 學年度各校二技護理系申請入學簡章的採計方式，排出目標校的準備優先順序。")
s = re.sub(r'<div class="row"><span class="label">入學管道</span>.*?</div>\s*<span class="muted" style="font-size:13px" id="mode-hint"></span>\s*</div>',
           '<div class="row"><span class="label">入學管道</span><span class="muted" style="font-size:13px;flex:1 1 220px;min-width:0" id="mode-hint"></span></div>', s, count=1, flags=re.S)
rep("依「六年平均配分 × 近三年趨勢 × 該科權重」排序。", "依「八年平均配分 × 近三年趨勢 × 該科權重」排序。")
rep('<div class="sec-head"><h2>各科章節熱度</h2><span class="tag">110–115</span></div>', '<div class="sec-head"><h2>各科章節熱度</h2><span class="tag">108–115</span></div>')
rep("依上方選的目標校與入學管道，排出到統測前的每週進度", "依上方選的目標校，排出到二技統測前的每週進度")
rep("<label>統測日期 <input", "<label>二技統測日期 <input")
rep("統測日期預設為 2027/4/24（預估），請依技專校院入學測驗中心公告調整。", "二技統測日期預設為 2027/4/24（預估，115 學年度與四技統測同日），請依技專校院入學測驗中心公告調整。")
s = re.sub(r'(<section class="note" aria-label="資料說明">\s*<div class="sec-head"[^\n]*\n).*?(\s*</section>)', lambda m: m.group(1) + """    <p>試題與公告答案來自技專校院入學測驗中心（108–115 學年度二技統一入學測驗護理類）；採計方式來自各校 115 學年度二技日間部申請入學簡章：國北護護理系、長庚護理系（甲類聯合招生）、弘光護理系、輔英護理系護理組 A 組。116 學年度簡章公告後需更新。中科大護理系目前查無二技招生，未列入。</p>
    <p>章節與題型為 Claude 依題意初標的暫定分類，專業科目與國文需任課老師覆核；英文依試題本的大題分類（字彙、對話、綜合測驗、閱讀測驗）。</p>
    <p>題目截圖取自測驗中心公告的試題本；108 年國文第 31–36 題所在頁為掃描圖，截圖依頁面位置人工裁切。逐題解析由 Claude 撰寫，已逐題比對公告答案，但推理與說明仍可能有誤，使用前請任課老師覆核；其中 <span id="rv-count"></span> 題標示「建議覆核」，展開後可看到原因。</p>
    <p>二技無聯合登記分發，各校自辦申請入學。國北護另採書面資料 30%，未列入本頁的章節排序；長庚、弘光、輔英 A 組只看統測成績。各校同分參酌順序不同，見上方各校說明。</p>""" + m.group(2), s, count=1, flags=re.S)



rep('也有二技版：<a href="https://bgjd315-cloud.github.io/tvee-nursing/erji/">二技護理類考題分析 →</a>',
    '也有統測（四技）版：<a href="https://bgjd315-cloud.github.io/tvee-nursing/">統測護理類考題分析 →</a>')

# ---- 資料設定 ----
rep("const YEARS = [110, 111, 112, 113, 114, 115];", "const YEARS = [108, 109, 110, 111, 112, 113, 114, 115];")
s = re.sub(r"const SUBJ = \[.*?\];\n// 115 學年度採計.*?\nconst SCHOOLS = \[.*?\n\];", """const SUBJ = [
  { key: '國文', label: '國文' },
  { key: '英文', label: '英文' },
  { key: '專業一', label: '專一 解剖生理學' },
  { key: '專業二', label: '專二 基本護理學' },
];
// 115 學年度二技日間部申請入學護理系：w 依序為 國、英、專一、專二；share 為統測占總成績的百分比
const SCHOOLS = [
  { id: 'ntunhs', name: '國北護', full: '國立臺北護理健康大學 護理系',
    apply: { share: 70, w: [1, 1, 1, 1], quota: '依簡章', formula: '護理類統測四科平均 × 70% ＋ 書面資料 × 30%', tie: '' } },
  { id: 'cgust', name: '長庚', full: '長庚科技大學 護理系（甲類聯合招生）',
    apply: { share: 100, w: [1, 1, 1, 1], quota: '林口 294、嘉義 196', formula: '四科各 ×1，總分 400，採網路志願序分發', tie: '英文 → 國文 → 專一 → 專二 → 專科歷年成績' } },
  { id: 'hk', name: '弘光', full: '弘光科技大學 護理系',
    apply: { share: 100, w: [1, 1, 1, 1], quota: '356', formula: '四科原始分數加總，總分 400', tie: '專二 → 專一 → 英文 → 國文 → 專科歷年成績' } },
  { id: 'fy', name: '輔英', full: '輔英科技大學 護理系護理組 A 組',
    apply: { share: 100, w: [1, 1, 1, 1], quota: '210', formula: '統測加權成績 100%，各科 1 倍（B 組 210 名為書審，不採統測）', tie: '專二 → 專一 → 英文 → 國文' } },
];
for (const sc of SCHOOLS) sc.dist = sc.apply;   // 二技只有申請入學，沿用範本的管道切換時兩者相同""", s, count=1, flags=re.S)
rep("'tvee-nursing", "'tvee2y-nursing", count=0)
rep("{ id: 'all', label: '五科混排' }", "{ id: 'all', label: '四科混排' }")
rep("c.avg = v.reduce((a, b) => a + b, 0) / 6;", "c.avg = v.reduce((a, b) => a + b, 0) / YEARS.length;")
rep("c.early = (v[0] + v[1] + v[2]) / 3;", "c.early = v.slice(0, -3).reduce((a, b) => a + b, 0) / (v.length - 3);")
rep("c.late = (v[3] + v[4] + v[5]) / 3;", "c.late = v.slice(-3).reduce((a, b) => a + b, 0) / 3;")
rep("const out = [0, 0, 0, 0, 0];", "const out = SUBJ.map(() => 0);")
rep('title="110–112 年平均', 'title="108–112 年平均', count=0)
s = re.sub(r"document\.getElementById\('mode-hint'\)\.textContent = state\.mode === 'apply'\s*\?[^;]*;",
           "document.getElementById('mode-hint').textContent = '二技日間部申請入學（各校自辦）：國北護統測占 70%，長庚、弘光、輔英 A 組統測占 100%';", s, count=1)
s = re.sub(r"\(state\.mode === 'apply' \? '甄選總成績中，各科統測分數換算後的占比。' : '登記分發總成績中，各科的占比。'\)",
           "'申請入學總成績中，各科二技統測分數換算後的占比。'", s, count=1)
s = re.sub(r"document\.getElementById\('school-notes'\)\.innerHTML = sel\.map\(s => state\.mode === 'apply'.*?\.join\(''\);",
           "document.getElementById('school-notes').innerHTML = sel.map(s => `<div class=\"sn\"><b>${esc(s.full)}</b>　名額 <span class=\"num\">${esc(s.apply.quota)}</span><br>${esc(s.apply.formula)}${s.apply.tie ? `<br>同分參酌：${esc(s.apply.tie)}` : ''}</div>`).join('');",
           s, count=1, flags=re.S)
rep("${state.mode === 'apply' ? '甄選入學' : '登記分發'}時，目前選的學校不採計這一科。", "目前選的學校不採計這一科。")
s = re.sub(r"document\.getElementById\('subj-sub'\)\.textContent = \{.*?\}\[state\.subj\]", """document.getElementById('subj-sub').textContent = {
    '國文': '國文依題型分類（二技國文以閱讀題組為主，約 30 題為文言或白話閱讀）。每年 50 題、每題 2 分。',
    '英文': '英文依試題本的大題分類。每年 50 題、每題 2 分；113 年起綜合測驗 12 題、閱讀測驗 13 題。',
    '專業一': '專業科目(一) 解剖生理學，依器官系統分類（每年第 1–25 題解剖、第 26–50 題生理）。每年 50 題、每題 2 分。',
    '專業二': '專業科目(二) 基本護理學，依主題分類。每年 50 題、每題 2 分。',
  }[state.subj]""", s, count=1, flags=re.S)
rep("該章節 110–115 年的所有題目與公告答案，點題目可展開截圖與解析。例如「${esc(top.name)}」六年共", "該章節 108–115 年的所有題目與公告答案，點題目可展開截圖。例如「${esc(top.name)}」八年共")
rep("由 Claude 依 110–115 年歷屆題目與解析整理", "由 Claude 依 108–115 年歷屆題目整理")
rep("<div class=\"explain\"><b>答案 ${esc(ans)}</b>　${esc(text)}</div>", "<div class=\"explain\"><b>答案 ${esc(ans)}</b>　${esc(text || '解析尚未撰寫，請先以公告答案對照。')}</div>")
rep("<div class=\"explain\" style=\"margin-top:8px\">${esc(text)}</div>", "${text ? `<div class=\"explain\" style=\"margin-top:8px\">${esc(text)}</div>` : ''}")
rep("const years = [115, 114, 113, 112, 111, 110];", "const years = [115, 114, 113, 112, 111, 110, 109, 108];")
rep("'統測日期需晚於開始日期。'", "'二技統測日期需晚於開始日期。'")
rep("'距離統測不到 6 週", "'距離二技統測不到 6 週")

rep("${state.mode === 'apply' ? '甄選入學' : '登記分發'}，共 ${p.W} 週", "二技申請入學，共 ${p.W} 週")

for bad in ["數學", "五科", "110–115", "1,229", "甄選", "分發總成績"]:
    hits = [m.start() for m in re.finditer(bad, s)]
    if hits:
        print("仍含「%s」%d 處：" % (bad, len(hits)), [s[max(0, h - 30):h + 30].replace("\n", " ") for h in hits[:3]])
open(os.path.join(HERE, "page_template.html"), "w", encoding="utf-8").write(s)
print("ok", len(s))
