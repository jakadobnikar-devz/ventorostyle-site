from pathlib import Path
import json
import shutil
from html import escape

ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / "public"
SITE = "https://ventorostyle.com"

STATIC_PAGES = [
    "index.html",
    "style.html",
    "grooming.html",
    "health-fitness.html",
    "gear-tech.html",
    "money-career.html",
    "life.html",
    "start-here.html",
    "aboutus.html",
    "editorial-policy.html",
    "terms-privacy.html",
]

SITEMAP_STATIC = [
    ("/", None),
    ("/style.html", None),
    ("/grooming.html", None),
    ("/health-fitness.html", None),
    ("/gear-tech.html", None),
    ("/money-career.html", None),
    ("/life.html", None),
    ("/start-here.html", None),
    ("/aboutus.html", None),
    ("/editorial-policy.html", None),
]


def require(path: Path):
    if not path.is_file():
        raise FileNotFoundError(f"Required file missing: {path.relative_to(ROOT)}")


def copy_file(src: Path, dst: Path):
    require(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def make_404():
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex, follow">
  <title>Page Not Found | Ventoro Style</title>
  <style>
    :root{--paper:#f4f1ea;--surface:#fff;--ink:#171716;--muted:#6e6a63;--accent:#8b4a34;--line:#d8d1c5;--serif:Georgia,"Times New Roman",serif;--sans:Arial,Helvetica,sans-serif}
    *{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);line-height:1.6}.shell{width:min(calc(100% - 40px),820px);margin:0 auto;padding:10vh 0}.card{background:var(--surface);border:1px solid var(--line);padding:clamp(32px,6vw,72px);box-shadow:0 18px 50px rgba(23,23,22,.08)}.eyebrow{margin:0 0 18px;color:var(--accent);font-size:.78rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase}h1{margin:0;font-family:var(--serif);font-size:clamp(3rem,8vw,6.5rem);font-weight:400;line-height:.95;letter-spacing:-.05em}p{color:var(--muted);font-size:1.05rem}.links{display:flex;gap:12px;flex-wrap:wrap;margin-top:30px}.links a{display:inline-block;padding:11px 16px;border:1px solid var(--ink);color:var(--ink);text-decoration:none;font-size:.78rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase}.links a:first-child{background:var(--ink);color:var(--surface)}
  </style>
</head>
<body><main class="shell"><section class="card"><p class="eyebrow">Ventoro Style</p><h1>404</h1><p>The page you were looking for could not be found. Continue with the latest stories or browse a topic.</p><nav class="links" aria-label="404 navigation"><a href="/">Latest stories</a><a href="/start-here.html">Start here</a></nav></section></main></body>
</html>"""


def make_sitemap(posts):
    urls = list(SITEMAP_STATIC)
    for post in posts:
        urls.append((f"/blogs/{post['slug']}.html", post.get("date")))
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, lastmod in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{escape(SITE + path)}</loc>")
        if lastmod:
            lines.append(f"    <lastmod>{escape(lastmod)}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def main():
    posts_path = ROOT / "data" / "posts.json"
    require(posts_path)
    posts = json.loads(posts_path.read_text(encoding="utf-8"))

    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)
    (PUBLIC / "blogs").mkdir(parents=True)
    (PUBLIC / "images").mkdir(parents=True)

    for name in STATIC_PAGES:
        copy_file(ROOT / name, PUBLIC / name)

    copy_file(ROOT / "images" / "ventorostyle-logo.png", PUBLIC / "images" / "ventorostyle-logo.png")

    for post in posts:
        slug = post.get("slug")
        image = post.get("image")
        if not slug or not image:
            raise ValueError(f"Invalid post entry in data/posts.json: {post}")
        copy_file(ROOT / "blogs" / f"{slug}.html", PUBLIC / "blogs" / f"{slug}.html")
        copy_file(ROOT / "images" / image, PUBLIC / "images" / image)

    (PUBLIC / ".nojekyll").touch()
    (PUBLIC / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: https://ventorostyle.com/sitemap.xml\n",
        encoding="utf-8",
    )
    (PUBLIC / "sitemap.xml").write_text(make_sitemap(posts), encoding="utf-8")
    (PUBLIC / "404.html").write_text(make_404(), encoding="utf-8")

    for required in ["index.html", "robots.txt", "sitemap.xml", "404.html"]:
        require(PUBLIC / required)

    unexpected = [p for p in PUBLIC.rglob("*") if p.is_file() and p.suffix.lower() in {".psd", ".py", ".json", ".dat", ".bak", ".zip"}]
    if unexpected:
        raise RuntimeError("Unexpected source files in public/: " + ", ".join(str(p.relative_to(PUBLIC)) for p in unexpected))

    print(f"✅ Prepared public/ with {len(posts)} live posts and {len(posts)} live post images.")


if __name__ == "__main__":
    main()
