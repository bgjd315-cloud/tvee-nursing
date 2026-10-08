// 逐題講義：每科一份 Word，依年度列出題目截圖、公告答案與解析。
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, ImageRun, HeadingLevel, AlignmentType,
  Footer, PageNumber, BorderStyle, Bookmark, InternalHyperlink,
} = require('docx');

const HERE = __dirname;
const OUTDIR = path.join(HERE, '..', '講義');
fs.mkdirSync(OUTDIR, { recursive: true });
const M = JSON.parse(fs.readFileSync(path.join(HERE, 'handout_manifest.json'), 'utf8'));
const NOTES = JSON.parse(fs.readFileSync(path.join(HERE, 'notes.json'), 'utf8'));
const CHAPTERS = JSON.parse(fs.readFileSync(path.join(HERE, 'chapters.json'), 'utf8'));
const EXTRA = { '國文': { C99: '寫作測驗' }, '英文': { E99: '非選擇題（填充、句子重組、中譯英）' } };
const LABEL = { '國文': '國文', '英文': '英文', '數學': '數學C', '專業一': '專業科目(一) 生物', '專業二': '專業科目(二) 健康與護理' };
const FONT = { ascii: 'Times New Roman', hAnsi: 'Times New Roman', eastAsia: 'Microsoft JhengHei' };
const DPI = 130;
const MAXW = 6.3 * 96;   // A4 扣邊界後的可用寬度（px @96dpi）

function image([file, w, h], keepNext = false) {
  let width = w * 96 / DPI, height = h * 96 / DPI;
  if (width > MAXW) { height *= MAXW / width; width = MAXW; }
  return new Paragraph({
    spacing: { after: 80 }, keepNext,
    children: [new ImageRun({ type: 'png', data: fs.readFileSync(file), transformation: { width: Math.round(width), height: Math.round(height) } })],
  });
}

// 章節重點筆記：每章一段「必讀重點」與「常見陷阱」
function notesSection(subj) {
  const chs = { ...CHAPTERS[subj], ...(EXTRA[subj] || {}) };
  const out = [
    new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [new Bookmark({ id: 'notes', children: [new TextRun('章節重點筆記')] })] }),
    new Paragraph({ spacing: { after: 160 }, children: [new TextRun({ text: '由 Claude 依 110–115 年歷屆題目與解析整理，請搭配課本與任課老師的講義使用。', size: 20, color: '555555' })] }),
  ];
  for (const [code, name] of Object.entries(chs)) {
    const n = NOTES[code];
    if (!n) continue;
    out.push(new Paragraph({ keepNext: true, spacing: { before: 240, after: 80 }, children: [new TextRun({ text: `${code}　${name}`, bold: true, size: 26 })] }));
    out.push(new Paragraph({ keepNext: true, spacing: { after: 40 }, children: [new TextRun({ text: '必讀重點', bold: true, size: 20, color: '555555' })] }));
    for (const t of n.key) out.push(new Paragraph({ bullet: { level: 0 }, spacing: { after: 40 }, children: [new TextRun(t)] }));
    if (n.trap && n.trap.length) {
      out.push(new Paragraph({ keepNext: true, spacing: { before: 80, after: 40 }, children: [new TextRun({ text: '常見陷阱', bold: true, size: 20, color: 'BE3B34' })] }));
      for (const t of n.trap) out.push(new Paragraph({ bullet: { level: 0 }, spacing: { after: 40 }, children: [new TextRun(t)] }));
    }
  }
  return out;
}

function build(subj, rows) {
  const children = [
    new Paragraph({ heading: HeadingLevel.TITLE, alignment: AlignmentType.CENTER, children: [new TextRun(`統測護理類 ${LABEL[subj]}`)] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 }, children: [new TextRun({ text: `110–115 學年度逐題解析　共 ${rows.length} 題`, size: 26 })] }),
    new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: '題目截圖取自技專校院入學測驗中心公告的試題本，答案為公告答案。解析由 Claude 撰寫，已逐題比對公告答案並經全面複查，但推理與說明仍可能有誤，使用前請任課老師覆核；標示「建議優先覆核」的題目請優先確認。', size: 20, color: '555555' })] }),
    new Paragraph({ spacing: { before: 240, after: 80 }, children: [new TextRun({ text: '目錄', bold: true, size: 26 })] }),
    new Paragraph({ spacing: { after: 60 }, children: [new InternalHyperlink({ anchor: 'notes', children: [new TextRun({ text: '章節重點筆記', style: 'Hyperlink' })] })] }),
    ...[...new Set(rows.map(r => r.year))].map(y => new Paragraph({
      spacing: { after: 60 },
      children: [new InternalHyperlink({ anchor: `y${y}`, children: [new TextRun({ text: `${y} 學年度（${rows.filter(r => r.year === y).length} 題）`, style: 'Hyperlink' })] })],
    })),
    ...notesSection(subj),
  ];
  let year = null;
  for (const r of rows) {
    if (r.year !== year) {
      year = r.year;
      children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [new Bookmark({ id: `y${year}`, children: [new TextRun(`${year} 學年度`)] })] }));
    }
    // 題組文章只在該題組第一題前印一次
    if (r.group && rows.find(x => x.group && x.group[0] === r.group[0]) === r) {
      children.push(new Paragraph({ spacing: { before: 200, after: 60 }, children: [new TextRun({ text: '【題組文章】', bold: true, color: '555555' })] }));
      children.push(image(r.group));
    }
    children.push(new Paragraph({
      keepNext: true, spacing: { before: 200, after: 60 },
      border: { top: { style: BorderStyle.SINGLE, size: 4, color: 'BBBBBB', space: 6 } },
      children: [new TextRun({ text: `第 ${r.no} 題`, bold: true })],
    }));
    children.push(image(r.img, true));   // 截圖與答案解析同頁
    children.push(new Paragraph({
      spacing: { before: 60, after: 160, line: 320 },
      shading: { type: 'clear', fill: 'F3F3F3', color: 'auto' },
      children: [
        new TextRun({ text: `答案 ${r.ans}`, bold: true }),
        new TextRun({ text: `　${r.text}` }),
      ],
    }));
    if (r.flag) {
      children.push(new Paragraph({
        spacing: { before: 0, after: 160 },
        border: { left: { style: BorderStyle.SINGLE, size: 12, color: 'BE3B34', space: 6 } },
        children: [new TextRun({ text: '建議優先覆核：', bold: true, color: 'BE3B34', size: 20 }), new TextRun({ text: r.flag, color: '555555', size: 20 })],
      }));
    }
  }
  return new Document({
    styles: {
      default: { document: { run: { font: FONT, size: 22 } } },
      paragraphStyles: [
        { id: 'Title', name: 'Title', basedOn: 'Normal', run: { size: 40, bold: true, font: FONT }, paragraph: { spacing: { before: 1200, after: 120 } } },
        { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { size: 32, bold: true, font: FONT }, paragraph: { spacing: { after: 160 }, outlineLevel: 0 } },
      ],
    },
    sections: [{
      properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
      footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: `${LABEL[subj]}　`, size: 18, color: '777777' }), new TextRun({ children: [PageNumber.CURRENT], size: 18, color: '777777' })] })] }) },
      children,
    }],
  });
}

(async () => {
  const order = ['專業二', '專業一', '國文', '英文', '數學'];
  for (const s of order) {
    const buf = await Packer.toBuffer(build(s, M[s]));
    const name = `統測護理_${LABEL[s].replace(/[() ]/g, '')}_逐題解析.docx`;
    fs.writeFileSync(path.join(OUTDIR, name), buf);
    console.log(name, (buf.length / 1e6).toFixed(1), 'MB');
  }
})();
