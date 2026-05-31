"""汴州往事：棋子（初稿） — 静态站点构建脚本"""
import re
import os
from pathlib import Path

# 尝试使用 markdown 库，没有则用简单转换
try:
    import markdown
    HAS_MD = True
except ImportError:
    HAS_MD = False

ROOT = Path(__file__).parent
CHAPTERS_DIR = ROOT.parent / "07_present"
OUT_DIR = ROOT

# 章节标题
CHAPTER_TITLES = {
    1: '酒肆',
    2: '空',
    3: '错',
    4: '三贯钱',
    5: '灰衣人',
    6: '三天',
    7: '浊',
    8: '眼前人',
    9: '第一条假消息',
    10: '同行',
    11: '周七',
    12: '手法',
    13: '交叉',
    14: '合流',
    15: '源头',
    16: '做局者',
    17: '代价',
    18: '虎牢关',
    19: '何小二',
    20: '常量',
    21: '棋盘',
    22: '教',
    23: '维度',
    24: '观察者',
    25: '第三选择',
    26: '静水',
    27: '刀',
    28: '陈渊走了',
    29: '偃师',
    30: '战场',
    31: '换旗',
    32: '信',
    33: '各走各路',
    34: '酒凉了',
}


def md_to_html(text: str) -> str:
    if HAS_MD:
        return markdown.markdown(text, extensions=["extra"])
    # 简单 fallback：段落转换
    paragraphs = re.split(r'\n{2,}', text.strip())
    parts = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if p == "---":
            parts.append("<hr>")
        else:
            # 处理粗体和斜体
            p = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', p)
            p = re.sub(r'\*(.+?)\*', r'<em>\1</em>', p)
            parts.append(f"<p>{p}</p>")
    return "\n".join(parts)


def get_chapter_title(num: int) -> str:
    return CHAPTER_TITLES.get(num, f"第{num}章")


def build_chapter_html(num: int, total: int, prose_html: str) -> str:
    title = get_chapter_title(num)
    display = f"第{num:02d}章 {title}" if num >= 10 else f"第0{num}章 {title}"

    prev_link = ""
    if num > 1:
        prev_link = f'<a class="nav-link nav-prev" href="ch{num-1:02d}.html">第{num-1:02d}章 {get_chapter_title(num-1)}</a>'
    else:
        prev_link = '<span></span>'

    next_link = ""
    if num < total:
        next_link = f'<a class="nav-link nav-next" href="ch{num+1:02d}.html">第{num+1:02d}章 {get_chapter_title(num+1)}</a>'
    else:
        next_link = '<span></span>'

    # 侧边栏
    sidebar_items = ""
    for i in range(1, total + 1):
        t = get_chapter_title(i)
        dn = f"第{i:02d}章" if i >= 10 else f"第0{i}章"
        active = ' class="active"' if i == num else ""
        sidebar_items += f'      <li class="sidebar-item"{active}><a href="ch{i:02d}.html"><span class="s-num">{dn}</span> {t}</a></li>\n'

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{display} · 汴州往事：棋子</title>
  <link rel="stylesheet" href="../static/style.css">
</head>
<body>
  <nav class="sidebar">
    <div class="sidebar-title">
      汴州往事
      <a href="../index.html">← 目录</a>
    </div>
    <ul class="sidebar-list">
{sidebar_items}    </ul>
  </nav>

  <article class="chapter-page">
    <header class="chapter-header">
      <h1 class="chapter-name">{display}</h1>
    </header>

    <div class="prose">
{prose_html}
    </div>

    <nav class="chapter-nav">
      {prev_link}
      <span></span>
      {next_link}
    </nav>

    <footer class="site-footer">
      <p class="footer-author">老莫是一个保安</p>
      <p class="footer-contact">yihan@viewe.cn</p>
    </footer>
  </article>
</body>
</html>"""


def build_index_html(chapters: list[tuple[int, str]]) -> str:
    items = ""
    for num, title in chapters:
        display = f"第{num:02d}章" if num >= 10 else f"第0{num}章"
        items += f"""      <li class="chapter-item">
        <a class="chapter-link" href="chapters/ch{num:02d}.html">
          <span class="chapter-num">{display}</span>
          <span class="chapter-title">{title}</span>
        </a>
      </li>
"""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>汴州往事：棋子（初稿）</title>
  <link rel="stylesheet" href="static/style.css">
</head>
<body>
  <div class="home">
    <header class="home-header">
      <h1 class="site-title">汴州往事</h1>
      <p class="site-subtitle">棋 子 · 初 稿</p>
      <p class="site-desc">
        隋末汴州，信息掮客顾衡以为自己在收割，<br>
        却不知早已是别人棋盘上的棋子。
      </p>
    </header>

    <ul class="chapter-list">
{items}    </ul>

    <footer class="home-footer">
      <span class="seal">棋 子</span>
      <p class="footer-author">老莫是一个保安</p>
      <p class="footer-contact">yihan@viewe.cn</p>
    </footer>
  </div>
</body>
</html>"""


def main():
    # 收集章节
    chapters = []
    for f in sorted(CHAPTERS_DIR.glob("ch*.md")):
        m = re.match(r'ch(\d+)', f.name)
        if not m:
            continue
        num = int(m.group(1))
        prose = f.read_text(encoding="utf-8").strip()
        chapters.append((num, prose))

    total = len(chapters)
    print(f"找到 {total} 个章节")

    # 生成章节页面
    chapters_dir = OUT_DIR / "chapters"
    chapters_dir.mkdir(exist_ok=True)

    for num, prose in chapters:
        prose_html = md_to_html(prose)
        html = build_chapter_html(num, total, prose_html)
        out = chapters_dir / f"ch{num:02d}.html"
        out.write_text(html, encoding="utf-8")

    # 生成首页
    index_chapters = [(num, get_chapter_title(num)) for num, _ in chapters]
    index_html = build_index_html(index_chapters)
    (OUT_DIR / "index.html").write_text(index_html, encoding="utf-8")

    print(f"构建完成 → {OUT_DIR}")
    print(f"  首页: index.html")
    print(f"  章节: chapters/ch01.html ~ ch{total:02d}.html")


if __name__ == "__main__":
    main()
