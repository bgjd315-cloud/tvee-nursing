# 原始檔

產生兩個考題分析網頁用的資料與程式。網頁本身在上一層的 `index.html`（統測）與 `erji/`（二技）。

| 資料夾 | 內容 |
|---|---|
| `exams/` | 統測（四技）護理類 110–115：試題 PDF、截圖 `img/`、題目 `questions.json`、章節標記 `questions_tagged.csv`、逐題解析 `explain/`、重點筆記 `notes.json`、覆核標記 `review_flags.json`、Word 講義產生器 `handout.js` |
| `exams2y/` | 二技護理類 108–115：試題 PDF、截圖 `img/`、題目、章節標記 `tags/`、逐題解析 `explain/`、各校採計紀錄 `schools.json`（網頁實際用的設定在 `make_template.py`）、覆核標記 |
| `講義/` | 統測各科逐題解析 Word 講義 |

## 重建網頁

需要 Python 3 與 PyMuPDF（`pip install pymupdf`）；Word 講義另需 Node.js（在 `exams/` 執行 `npm install`）。

統測：

```bash
cd exams
python build_page.py        # 產生 ../統測護理考題分析.html 與 ../site/data/
```

二技（版面沿用統測的 `exams/page_template.html`）：

```bash
cd exams2y
python make_template.py     # 由統測範本改寫出二技範本
python build_page.py        # 產生 ../二技護理考題分析.html 與 ../site2y/
python check_explain.py     # 檢查解析題數與答案是否和公告答案一致
```

統測網頁在檔案最前面補上 `<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">` 後存成根目錄的 `index.html`，`site/data/` 複製到 `data/`；二技把 `site2y/` 的內容複製到 `erji/`。推送後 GitHub Pages 約一分鐘內更新。

## 每年新增一個學年度

1. 下載測驗中心公告的新年度試題 PDF 放進 `exams/`、`exams2y/`。
2. 執行 `parse.py` 解析題目與公告答案，`crop.py` 裁切截圖。
3. 標記章節（`exams/tags.py`、`exams2y/tags/`），撰寫 `explain/{年}-{科}.json` 解析。
4. 依新簡章更新目標校採計方式（統測寫在 `exams/page_template.html` 的 `SCHOOLS`，二技寫在 `exams2y/make_template.py`，並同步記到 `schools.json`），並把年份清單加上新年度。
5. 重建網頁並推送。
