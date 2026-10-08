"""章節字典與逐題章節標註（初標，待任課老師覆核）。輸出 questions_tagged.csv。"""
import csv, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))

CHAPTERS = {
    "專業一": {
        "B01": "生命現象與生物分子", "B02": "細胞構造與觀察", "B03": "代謝、酵素與光合作用",
        "B04": "細胞分裂", "B05": "遺傳法則與人類遺傳", "B06": "DNA 與基因表現",
        "B07": "生物技術", "B08": "生命起源與演化", "B09": "分類、病毒與微生物",
        "B10": "動植物類群", "B11": "植物構造與生理", "B12": "植物生殖",
        "B13": "消化與營養", "B14": "循環與血液", "B15": "免疫",
        "B16": "呼吸", "B17": "排泄", "B18": "神經、肌肉與骨骼",
        "B19": "內分泌", "B20": "人類生殖與發育", "B21": "族群、群集與生態系",
        "B22": "生物多樣性、保育與環境",
    },
    "專業二": {
        "H01": "健康概念與健康促進", "H02": "體位、營養與飲食", "H03": "心理健康與壓力",
        "H04": "親密關係、性別與性平", "H05": "生殖保健、避孕與人工流產", "H06": "懷孕、產前產後與哺乳",
        "H07": "性傳染病與愛滋", "H08": "傳染病防治", "H09": "慢性病、代謝症候群與健檢",
        "H10": "視力、口腔與姿勢保健", "H11": "物質濫用與用藥安全", "H12": "事故傷害與急救",
        "H13": "老化、長照與安寧", "H14": "健康消費與食品安全", "H15": "環境與職業健康",
    },
    # 國文依題型分類（統測國文以閱讀題組為主，不按課次）
    "國文": {
        "C01": "字形", "C02": "字詞義與虛詞", "C03": "詞語填空", "C04": "語法、修辭與表達手法",
        "C05": "文句排序", "C06": "國學與文學常識", "C07": "應用文",
        "C08": "古典文本閱讀", "C09": "白話文學閱讀", "C10": "知識性與圖表資訊閱讀",
    },
}
COUNT = {"專業一": 50, "專業二": 50, "國文": 38, "數學": 25}

CHAPTERS["數學"] = {
    "M01": "數與式、絕對值與複數", "M02": "多項式、函數與方程式", "M03": "直線與二元一次不等式",
    "M04": "圓與圓錐曲線", "M05": "三角函數與三角形", "M06": "平面與空間向量",
    "M07": "指數與對數", "M08": "數列與級數", "M09": "排列組合與機率",
    "M10": "統計", "M11": "矩陣與聯立方程式", "M12": "微積分",
}

# 英文依試題本標示的大題分類：(大題代碼, 起題, 迄題)
CHAPTERS["英文"] = {"E01": "字彙題", "E02": "對話題", "E03": "綜合測驗", "E04": "閱讀測驗"}
EN_SECTIONS = {
    110: [("E01", 1, 11), ("E02", 12, 21), ("E03", 22, 31), ("E04", 32, 41)],
    111: [("E01", 1, 10), ("E02", 11, 20), ("E03", 21, 30), ("E04", 31, 42)],
    112: [("E01", 1, 10), ("E02", 11, 20), ("E03", 21, 30), ("E04", 31, 42)],
    113: [("E01", 1, 10), ("E02", 11, 20), ("E03", 21, 28), ("E04", 29, 42)],
    114: [("E01", 1, 10), ("E02", 11, 20), ("E03", 21, 28), ("E04", 29, 42)],
    115: [("E01", 1, 10), ("E02", 11, 20), ("E03", 21, 28), ("E04", 29, 42)],
}

# 每年 50 題的章節代碼，依題號排列
TAGS = {
    ("專業一", 110): "B04 B08 B01 B02 B02 B03 B09 B09 B11 B12 B03 B11 B12 B11 B12 B13 B18 B19 B16 B16 B17 B18 B18 B20 B20 B15 B15 B05 B19 B14 B13 B05 B06 B06 B06 B05 B05 B07 B07 B07 B21 B21 B21 B21 B22 B22 B22 B22 B22 B22",
    ("專業一", 111): "B01 B13 B13 B14 B14 B17 B18 B19 B19 B02 B01 B03 B04 B04 B02 B11 B11 B11 B08 B09 B09 B10 B21 B09 B09 B08 B09 B10 B06 B06 B05 B07 B07 B07 B20 B20 B21 B21 B21 B22 B22 B21 B22 B22 B15 B15 B05 B05 B21 B21",
    ("專業一", 112): "B11 B13 B14 B16 B16 B16 B15 B18 B19 B04 B04 B02 B02 B03 B11 B02 B08 B08 B08 B22 B09 B09 B09 B09 B09 B10 B20 B20 B12 B07 B21 B21 B22 B21 B21 B07 B07 B07 B07 B05 B22 B22 B21 B21 B06 B06 B05 B05 B13 B13",
    ("專業一", 113): "B01 B02 B02 B02 B11 B11 B13 B14 B16 B17 B15 B15 B18 B19 B12 B07 B05 B05 B06 B09 B22 B09 B10 B10 B10 B09 B09 B09 B08 B21 B21 B21 B21 B21 B07 B07 B07 B22 B22 B04 B04 B04 B20 B20 B05 B05 B15 B09 B22 B22",
    ("專業一", 114): "B03 B11 B11 B11 B11 B13 B14 B14 B16 B17 B18 B19 B02 B19 B02 B02 B04 B02 B09 B15 B12 B22 B09 B08 B06 B06 B07 B07 B09 B16 B10 B21 B21 B21 B21 B21 B22 B22 B05 B07 B07 B07 B10 B10 B20 B20 B05 B05 B22 B22",
    ("專業一", 115): "B01 B02 B01 B01 B04 B04 B14 B11 B11 B14 B14 B16 B17 B18 B19 B15 B20 B20 B13 B07 B05 B05 B06 B08 B09 B10 B10 B10 B08 B10 B22 B21 B21 B21 B21 B22 B22 B07 B07 B07 B07 B22 B02 B02 B11 B11 B05 B05 B21 B21",
    ("數學", 110): "M02 M05 M05 M09 M12 M08 M02 M04 M04 M11 M11 M09 M03 M05 M02 M06 M12 M05 M01 M02 M09 M12 M12 M10 M07",
    ("數學", 111): "M07 M08 M01 M05 M02 M03 M03 M02 M04 M02 M11 M05 M06 M06 M09 M06 M11 M12 M12 M12 M07 M05 M05 M04 M12",
    ("數學", 112): "M02 M01 M05 M06 M03 M05 M11 M01 M06 M11 M01 M02 M07 M02 M12 M04 M08 M05 M07 M09 M04 M05 M12 M12 M05",
    ("數學", 113): "M02 M03 M05 M04 M11 M05 M09 M02 M11 M02 M12 M01 M04 M12 M12 M07 M05 M01 M06 M08 M03 M07 M12 M06 M06",
    ("數學", 114): "M01 M06 M12 M05 M01 M07 M08 M05 M02 M03 M04 M12 M11 M09 M11 M07 M04 M06 M05 M05 M03 M06 M12 M06 M12",
    ("數學", 115): "M02 M08 M06 M01 M11 M12 M12 M03 M02 M07 M07 M02 M09 M05 M05 M03 M04 M12 M04 M05 M04 M12 M06 M11 M05",
    ("國文", 110): "C01 C02 C02 C04 C06 C04 C05 C06 C03 C04 C10 C10 C08 C08 C08 C08 C08 C08 C08 C08 C08 C10 C10 C10 C10 C10 C10 C10 C10 C10 C10 C09 C09 C09 C09 C10 C10 C10",
    ("國文", 111): "C01 C02 C03 C05 C04 C07 C04 C06 C07 C02 C10 C10 C10 C08 C08 C10 C10 C10 C10 C10 C10 C08 C08 C08 C10 C10 C10 C08 C08 C08 C08 C08 C10 C10 C09 C09 C09 C09",
    ("國文", 112): "C01 C02 C02 C02 C04 C04 C03 C04 C05 C06 C09 C09 C09 C09 C10 C10 C10 C10 C08 C08 C08 C08 C08 C08 C08 C08 C08 C08 C10 C10 C10 C10 C10 C10 C10 C10 C09 C09",
    ("國文", 113): "C01 C02 C04 C03 C04 C07 C05 C02 C06 C08 C10 C10 C08 C08 C10 C10 C10 C10 C10 C10 C10 C10 C08 C08 C08 C08 C10 C10 C10 C08 C08 C08 C08 C09 C09 C09 C10 C10",
    ("國文", 114): "C01 C04 C02 C04 C05 C04 C06 C03 C08 C08 C09 C09 C09 C09 C09 C10 C10 C10 C10 C08 C08 C08 C08 C08 C08 C08 C08 C10 C10 C10 C10 C10 C10 C10 C08 C10 C10 C10",
    ("國文", 115): "C01 C02 C03 C04 C02 C06 C04 C06 C05 C06 C09 C09 C09 C09 C09 C08 C08 C08 C08 C08 C10 C10 C10 C10 C10 C10 C10 C08 C10 C10 C10 C10 C10 C10 C10 C10 C10 C10",
    ("專業二", 110): "H01 H02 H02 H09 H08 H08 H08 H13 H13 H13 H13 H13 H13 H12 H12 H12 H12 H12 H12 H12 H12 H12 H12 H14 H14 H14 H02 H14 H03 H03 H03 H03 H03 H03 H11 H11 H04 H04 H04 H04 H05 H05 H05 H07 H04 H06 H09 H04 H04 H04",
    ("專業二", 111): "H15 H12 H12 H12 H12 H12 H12 H11 H11 H11 H01 H09 H09 H08 H08 H03 H01 H03 H01 H02 H02 H14 H14 H14 H02 H10 H02 H03 H04 H04 H06 H06 H05 H07 H04 H03 H04 H06 H13 H13 H13 H13 H13 H05 H06 H05 H15 H15 H03 H03",
    ("專業二", 112): "H13 H13 H13 H06 H06 H05 H06 H15 H12 H12 H12 H12 H12 H11 H11 H11 H12 H15 H15 H01 H04 H04 H03 H04 H05 H05 H05 H07 H07 H04 H10 H01 H10 H09 H02 H02 H14 H14 H10 H03 H03 H12 H09 H09 H02 H02 H02 H03 H03 H08",
    ("專業二", 113): "H13 H13 H13 H13 H05 H06 H06 H06 H06 H06 H15 H12 H12 H12 H12 H12 H11 H11 H11 H11 H15 H04 H04 H04 H07 H07 H05 H05 H07 H05 H04 H10 H10 H09 H09 H02 H02 H14 H14 H14 H15 H03 H03 H03 H09 H09 H08 H08 H08 H08",
    ("專業二", 114): "H02 H06 H06 H13 H13 H13 H13 H06 H12 H12 H12 H12 H11 H11 H15 H12 H11 H11 H15 H04 H04 H05 H05 H05 H07 H07 H07 H07 H04 H02 H01 H02 H02 H10 H09 H14 H10 H03 H03 H03 H01 H09 H09 H09 H08 H08 H14 H02 H06 H06",
    ("專業二", 115): "H15 H03 H03 H05 H06 H06 H05 H06 H06 H13 H13 H13 H15 H12 H12 H12 H12 H12 H11 H11 H11 H11 H02 H02 H04 H04 H04 H04 H05 H05 H05 H07 H07 H04 H01 H10 H14 H14 H09 H09 H09 H02 H08 H01 H10 H08 H03 H10 H02 H09",
}

# 情境題：題幹以人物、個案或實際事件起頭（自動判定，供參考）
SCENARIO = re.compile(r"(小[一-龥]|同學|[一-龥](先生|女士|媽媽|爸爸|伯伯|奶奶)|\d+歲|某生|某民|某孕婦|某女性|患者|病人|個案|事件|新聞|調查|實驗|探究|觀察)")
FIGURE = re.compile(r"(圖\s*\(|表\s*\(|下圖|下表|如圖|如表)")


def summary(stem):
    """題幹前 60 字：中文之間的空白去掉，英文單字之間保留一個空白。"""
    s = re.sub(r"\s+", " ", stem).strip()
    s = re.sub(r"(?<=[^ -~]) | (?=[^ -~])", "", s)   # 只去掉靠近非 ASCII 字元的空白
    return s[:60]


def main():
    qs = json.load(open(os.path.join(HERE, "questions.json"), encoding="utf-8"))
    rows = []
    for q in qs:
        if q["subject"] == "英文":
            codes = [c for c, a, b in EN_SECTIONS[q["year"]] for _ in range(a, b + 1)]
            assert len(codes) == max(x["no"] for x in qs if x["subject"] == "英文" and x["year"] == q["year"])
        else:
            codes = TAGS[(q["subject"], q["year"])].split()
            assert len(codes) == COUNT[q["subject"]], (q["subject"], q["year"], len(codes))
        code = codes[q["no"] - 1]
        stem = q["stem"]
        rows.append({
            "題目編號": q["id"], "年度": q["year"], "考科": q["subject"], "題號": q["no"],
            "章節代碼": code, "章節名稱": CHAPTERS[q["subject"]][code],
            "情境題": "是" if SCENARIO.search(stem) else "否",
            "圖表題": "是" if FIGURE.search(stem) or len(q["options"]) < 4 else "否",
            "公告答案": q["answer"], "配分": q["points"],
            "題幹摘要": summary(stem),
        })
    with open(os.path.join(HERE, "questions_tagged.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    json.dump(CHAPTERS, open(os.path.join(HERE, "chapters.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("rows", len(rows))


if __name__ == "__main__":
    main()
