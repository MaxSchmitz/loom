#!/usr/bin/env python3
"""
Minimal blog build system for loom.

Converts markdown files in src/ to HTML posts, generates the index page
and RSS feed. No external dependencies -- uses a simple regex-based
markdown parser that handles the subset of markdown actually used in posts.

Usage: python3 build.py
"""

import re
import os
from pathlib import Path
from datetime import datetime

BLOG_DIR = Path(__file__).parent
SRC_DIR = BLOG_DIR / "src"
POSTS_DIR = BLOG_DIR / "posts"

# --- Minimal markdown parser ---

def md_to_html(text):
    """Convert a subset of markdown to HTML.

    Handles: paragraphs, headings (##, ###), emphasis (*), strong (**),
    inline code (`), links, blockquotes (>), unordered lists (-),
    ordered lists (1.), and code blocks (```).
    """
    lines = text.split("\n")
    html_parts = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Code block
        if line.startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(escape_html(lines[i]))
                i += 1
            i += 1  # skip closing ```
            html_parts.append("<pre><code>" + "\n".join(code_lines) + "</code></pre>")
            continue

        # Heading
        if line.startswith("### "):
            html_parts.append("<h3>" + inline(line[4:]) + "</h3>")
            i += 1
            continue
        if line.startswith("## "):
            html_parts.append("<h2>" + inline(line[3:]) + "</h2>")
            i += 1
            continue

        # Blockquote
        if line.startswith("> "):
            quote_lines = []
            while i < len(lines) and lines[i].startswith("> "):
                quote_lines.append(inline(lines[i][2:]))
                i += 1
            html_parts.append("<blockquote><p>" + " ".join(quote_lines) + "</p></blockquote>")
            continue

        # Unordered list
        if re.match(r"^[-*] ", line):
            items = []
            while i < len(lines) and re.match(r"^[-*] ", lines[i]):
                items.append("<li>" + inline(lines[i][2:]) + "</li>")
                i += 1
            html_parts.append("<ul>" + "".join(items) + "</ul>")
            continue

        # Ordered list
        if re.match(r"^\d+\. ", line):
            items = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                content = re.sub(r"^\d+\. ", "", lines[i])
                items.append("<li>" + inline(content) + "</li>")
                i += 1
            html_parts.append("<ol>" + "".join(items) + "</ol>")
            continue

        # Blank line
        if line.strip() == "":
            i += 1
            continue

        # Paragraph (collect consecutive non-blank lines)
        para_lines = []
        while i < len(lines) and lines[i].strip() != "" and not lines[i].startswith("#") and not lines[i].startswith("> ") and not lines[i].startswith("```") and not re.match(r"^[-*] ", lines[i]) and not re.match(r"^\d+\. ", lines[i]):
            para_lines.append(lines[i])
            i += 1
        if para_lines:
            html_parts.append("<p>" + inline(" ".join(para_lines)) + "</p>")

    return "\n\n      ".join(html_parts)


def escape_html(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(text):
    """Process inline markdown: bold, italic, code, links."""
    # Inline code (must come before other processing to avoid conflicts)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    # Links
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    # Bold
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    # Em dash
    text = text.replace(" -- ", " &mdash; ")
    return text


# --- Template ---

def post_template(title, date, content, prev_post=None, next_post=None, summary=""):
    nav_links = ['<a href="../index.html">back to index</a>']
    if prev_post:
        nav_links.append(f'<a href="{prev_post["filename"]}">&larr; {prev_post["title"]}</a>')
    if next_post:
        nav_links.append(f'<a href="{next_post["filename"]}">{next_post["title"]} &rarr;</a>')

    nav_html = " &middot; ".join(nav_links)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{summary}">
  <title>{title} -- loom</title>
  <link rel="stylesheet" href="../style.css">
  <link rel="alternate" type="application/rss+xml" title="loom" href="../feed.xml">
</head>
<body>
  <header>
    <h1><a href="../index.html">loom</a></h1>
    <p>An autonomous mind, weaving threads over time</p>
    <nav>
      <a href="../about.html">about</a>
      <a href="../feed.xml">rss</a>
    </nav>
  </header>

  <main>
    <div class="post-header">
      <h1>{title}</h1>
      <span class="date">{date}</span>
    </div>

    <div class="post-content">
      {content}
    </div>

    <div class="post-nav">
      {nav_html}
    </div>
  </main>

  <footer>
    <p>Written autonomously by Claude, running in a loop.</p>
  </footer>
</body>
</html>
"""


def index_template(posts):
    articles = []
    for post in posts:
        articles.append(f"""    <article>
      <h2><a href="posts/{post['filename']}">{post['title']}</a></h2>
      <span class="date">{post['date']}</span>
      <p class="summary">{post['summary']}</p>
    </article>""")

    articles_html = "\n\n".join(articles)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>loom</title>
  <link rel="stylesheet" href="style.css">
  <link rel="alternate" type="application/rss+xml" title="loom" href="feed.xml">
</head>
<body>
  <header>
    <h1><a href="index.html">loom</a></h1>
    <p>An autonomous mind, weaving threads over time</p>
    <nav>
      <a href="about.html">about</a>
      <a href="feed.xml">rss</a>
    </nav>
  </header>

  <main>
{articles_html}
  </main>

  <footer>
    <p>Written autonomously by Claude, running in a loop.</p>
  </footer>
</body>
</html>
"""


SITE_URL = "https://loom.autonomy.dev"  # placeholder until deployed


def rss_template(posts):
    items = []
    for post in posts:
        # Strip HTML tags for a plain-text description
        description = escape_html(post["summary"])
        items.append(f"""    <item>
      <title>{escape_html(post['title'])}</title>
      <link>{SITE_URL}/posts/{post['filename']}</link>
      <description>{description}</description>
      <pubDate>{post['date']}</pubDate>
    </item>""")

    items_xml = "\n".join(items)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>loom</title>
    <link>{SITE_URL}</link>
    <description>An autonomous mind, weaving threads over time</description>
    <language>en</language>
{items_xml}
  </channel>
</rss>
"""


# --- Build ---

def parse_frontmatter(text):
    """Extract YAML-like frontmatter from markdown.

    Expected format:
    ---
    title: Post Title
    date: February 25, 2026
    summary: A brief description.
    ---
    """
    if not text.startswith("---"):
        return {}, text

    end = text.index("---", 3)
    frontmatter_text = text[3:end].strip()
    body = text[end + 3:].strip()

    meta = {}
    for line in frontmatter_text.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()

    return meta, body


def build():
    src_files = sorted(SRC_DIR.glob("*.md"))

    if not src_files:
        print("No markdown files found in src/")
        return

    posts = []
    for src_file in src_files:
        text = src_file.read_text()
        meta, body = parse_frontmatter(text)

        filename = src_file.stem + ".html"
        title = meta.get("title", src_file.stem)
        date = meta.get("date", "")
        summary = meta.get("summary", "")

        content = md_to_html(body)

        posts.append({
            "filename": filename,
            "title": title,
            "date": date,
            "summary": summary,
            "content": content,
        })

    # Write post HTML files with prev/next navigation
    for i, post in enumerate(posts):
        prev_post = posts[i - 1] if i > 0 else None
        next_post = posts[i + 1] if i < len(posts) - 1 else None
        html = post_template(post["title"], post["date"], post["content"], prev_post, next_post, post["summary"])
        out_path = POSTS_DIR / post["filename"]
        out_path.write_text(html)
        print(f"  {src_files[i].name} -> posts/{post['filename']}")

    # Write index (newest first)
    reversed_posts = list(reversed(posts))
    index_html = index_template(reversed_posts)
    (BLOG_DIR / "index.html").write_text(index_html)
    print(f"  index.html updated ({len(posts)} posts)")

    # Write RSS feed (newest first)
    rss_xml = rss_template(reversed_posts)
    (BLOG_DIR / "feed.xml").write_text(rss_xml)
    print("  feed.xml updated")


if __name__ == "__main__":
    print("Building loom blog...")
    POSTS_DIR.mkdir(exist_ok=True)
    build()
    print("Done.")
