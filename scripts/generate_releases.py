#!/usr/bin/env python3
"""Generate releases.html, releases.xml and releases.cache.json from DistroWatch.

Sources
-------
* https://distrowatch.com/news/dwd.xml  - the set of recent releases, their
  titles, slugs, publication dates and descriptions.
* https://distrowatch.com/              - the release table, which carries the
  clean "name <bullet> version" split plus the direct download (ISO) link.
* https://distrowatch.com/<slug>        - the "Home Page" field of a single
  distribution, used to auto-discover homepages.
* homepages.cfg                         - optional manual overrides, keyed by
  DistroWatch slug, always winning over auto-discovery.

Nothing here is allowed to fail the build: only the DistroWatch feed is fatal,
every other source degrades to "no data".  Discovered homepages are cached in
releases.cache.json and reused on the next run so the slow per-distro scraping
only happens when a new release shows up.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

DWD_FEED = "https://distrowatch.com/news/dwd.xml"
DISTROWATCH = "https://distrowatch.com/"
SITE = "https://feed.osowoso.org"
PUBLISHED_CACHE = f"{SITE}/releases.cache.json"
HOMEPAGES_DEFAULT = "homepages.cfg"

UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120 Safari/537.36"
)

# DistroWatch sits behind a bot filter that answers 403 to default clients and
# does not like rapid sequential requests, so play nice.
POLITE_DELAY = 1.5
MAX_ATTEMPTS = 3

ROW_RE = re.compile(
    r'<tr>\s*<th class="News">(?P<date>[^<]*)</th>\s*<td class="News">(?P<cell>.*?)</td>\s*</tr>',
    re.S,
)
NAME_RE = re.compile(
    r'<a title="(?P<desc>[^"]*)"\s+href="(?P<slug>[^"/?#]+)"\s*>(?P<name>.*?)</a>',
    re.S,
)
LINK_RE = re.compile(r'<a href="(?P<href>[^"]+)"[^>]*>(?P<label>.*?)</a>', re.S)
HOMEPAGE_RE = re.compile(
    r'<th class="Info">Home Page</th>\s*<td class="Info">\s*<a href="(?P<url>[^"]+)"',
    re.S,
)
TAG_RE = re.compile(r"<[^>]+>")

ISO_HINTS = (".iso", ".img", ".qcow2", ".raw", ".zip")


def log(message: str) -> None:
    print(f"[releases] {message}", file=sys.stderr)


def fetch(url: str, timeout: float = 30.0) -> str:
    """GET a URL with a browser-ish UA, retrying transient failures."""
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    last_error: Exception | None = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read().decode("utf-8", "replace")
        except (urllib.error.URLError, OSError) as error:
            last_error = error
            if attempt < MAX_ATTEMPTS:
                time.sleep(2 * attempt)
    raise RuntimeError(f"GET {url} failed: {last_error}")


def plain(text: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(TAG_RE.sub(" ", text))).strip()


def absolute(href: str) -> str:
    if href.startswith(("http://", "https://")):
        return href
    return "https://distrowatch.com/" + href.lstrip("./")


def load_text(source: str | None, timeout: float) -> str:
    """Read a local path or an http(s) URL; an empty string when neither works."""
    if not source:
        return ""
    if source.startswith(("http://", "https://")):
        try:
            return fetch(source, timeout=timeout)
        except RuntimeError as error:
            log(f"warning: {error}")
            return ""
    if not os.path.isfile(source):
        log(f"warning: {source} not found, continuing without it")
        return ""
    with open(source, encoding="utf-8", errors="replace") as handle:
        return handle.read()


def parse_homepages(raw: str) -> dict[str, str]:
    """homepages.cfg is `slug=url`, one per line, `#` starts a comment."""
    overrides: dict[str, str] = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        slug, _, url = line.partition("=")
        slug = slug.strip().strip("'\"").lower()
        url = url.strip().strip("'\"").rstrip(",")
        if slug and url:
            overrides[slug] = url
    return overrides


def load_cache(source: str, timeout: float) -> dict[str, str]:
    raw = load_text(source, timeout)
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except ValueError as error:
        log(f"warning: ignoring unreadable cache ({error})")
        return {}
    homepages = data.get("homepages") if isinstance(data, dict) else None
    if not isinstance(homepages, dict):
        return {}
    return {str(k).lower(): str(v) for k, v in homepages.items() if v}


def parse_feed(raw: str) -> list[dict[str, str]]:
    """RSS items: title, slug from the link, description, publication date."""
    channel = ET.fromstring(raw)
    entries = []
    for item in channel.iter("item"):
        def text_of(tag: str) -> str:
            node = item.find(tag)
            return (node.text or "").strip() if node is not None else ""

        link = text_of("link")
        match = re.search(r"distrowatch\.com/([^/?#]+)", link)
        if not match:
            continue
        description = text_of("description")
        icon = re.search(r'<img src="([^"]+)"', description)
        try:
            published = dt.datetime.strptime(
                text_of("pubDate"), "%a, %d %b %Y %H:%M:%S %z"
            )
        except ValueError:
            published = None
        entries.append(
            {
                "slug": match.group(1).lower(),
                "title": re.sub(r"\s+", " ", text_of("title")),
                "description": plain(description),
                "icon": absolute(icon.group(1)) if icon else "",
                "published": published.isoformat() if published else "",
                "date": published.strftime("%Y-%m-%d") if published else "",
            }
        )
    return entries


def parse_table(raw: str) -> dict[str, dict[str, str]]:
    """The release table, keyed by slug.

    Only rows whose first anchor carries a `title` attribute and a bare
    relative href are releases; the same `class="News"` markup is reused by the
    waiting-list and podcast tables, which only ever link out absolutely.
    """
    table: dict[str, dict[str, str]] = {}
    for row in ROW_RE.finditer(raw):
        head = NAME_RE.search(row.group("cell"))
        if not head:
            continue
        tail = row.group("cell")[head.end():]
        iso_url = ""
        fallback_url = ""
        for link in LINK_RE.finditer(tail):
            href = absolute(html.unescape(link.group("href")))
            if not fallback_url:
                fallback_url = href
            if not iso_url and any(href.lower().endswith(hint) or hint in href.lower() for hint in ISO_HINTS):
                iso_url = href
        slug = head.group("slug").lower()
        table[slug] = {
            "name": plain(head.group("name")),
            "version": plain(re.sub(r"&bull;?", " ", tail)),
            "iso": iso_url or fallback_url,
            "description": plain(head.group("desc")),
        }
    return table


def discover_homepage(slug: str, timeout: float) -> str:
    try:
        raw = fetch(f"{DISTROWATCH}{slug}", timeout=timeout)
    except RuntimeError as error:
        log(f"warning: {error}")
        return ""
    found = HOMEPAGE_RE.search(raw)
    if not found:
        return ""
    url = html.unescape(found.group("url")).strip()
    return url if url.startswith(("http://", "https://")) else ""


def collect(args: argparse.Namespace) -> list[dict[str, str]]:
    homepages = parse_homepages(load_text(args.homepages, args.timeout))
    if homepages:
        log(f"loaded {len(homepages)} homepage override(s)")
    cache = load_cache(args.cache, args.timeout)
    log(f"cache holds {len(cache)} homepage(s)")

    raw_feed = fetch(DWD_FEED, args.timeout)
    entries = parse_feed(raw_feed)
    if not entries:
        raise SystemExit("distrowatch feed contained no usable entries")
    log(f"feed has {len(entries)} release(s)")

    try:
        table = parse_table(fetch(DISTROWATCH, args.timeout))
    except RuntimeError as error:
        log(f"warning: {error} - continuing without download links")
        table = {}
    log(f"release table has {len(table)} row(s)")

    releases = []
    for entry in entries:
        slug = entry["slug"]
        row = table.get(slug, {})
        name = row.get("name") or entry["title"]
        title = entry["title"]
        if title.startswith(name):
            version = title[len(name):].strip()
        else:
            version = row.get("version", "")

        if slug in homepages:
            homepage = homepages[slug]
            source = "override"
        elif cache.get(slug):
            homepage = cache[slug]
            source = "cache"
        else:
            time.sleep(args.delay)
            homepage = discover_homepage(slug, args.timeout)
            if homepage:
                cache[slug] = homepage
            source = "distrowatch"

        releases.append(
            {
                "slug": slug,
                "name": name,
                "version": version,
                "title": f"{name} {version}".strip() or title,
                "description": entry["description"] or row.get("description", ""),
                "icon": entry["icon"],
                "iso": row.get("iso", ""),
                "homepage": homepage,
                "homepage_source": source,
                "url": f"{DISTROWATCH}{slug}",
                "date": entry["date"],
                "published": entry["published"],
            }
        )
        log(f"  {releases[-1]['title']}: homepage={homepage or '-'} ({source})")

    missing = [r["slug"] for r in releases if not r["homepage"]]
    if missing:
        log(f"warning: no homepage for {', '.join(missing)}")
    return releases


def render_html(releases: list[dict[str, str]], updated: str) -> str:
    items = []
    for release in releases:
        links = [f'<a href="{html.escape(release["url"])}">DistroWatch</a>']
        if release["homepage"]:
            links.append(
                f'<a href="{html.escape(release["homepage"])}">Homepage</a>'
            )
        if release["iso"]:
            links.append(
                f'<a href="{html.escape(release["iso"])}" '
                f'title="{html.escape(release["iso"])}">ISO</a>'
            )
        date = release["date"] or ""
        version = f' <span class="version">{html.escape(release["version"])}</span>' if release["version"] else ""
        description = (
            f'<p class="desc">{html.escape(release["description"])}</p>'
            if release["description"]
            else ""
        )
        items.append(
            "    <li>"
            f'<span class="date">{html.escape(date)}</span>'
            f'<span class="name">{html.escape(release["name"])}{version}</span>'
            f'<span class="links">{" · ".join(links)}</span>'
            f"{description}"
            "</li>"
        )
    body = "\n".join(items)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Latest Distro Releases</title>
  <style>
    body {{ font-family: sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; }}
    a {{ color: #0070f3; }}
    .meta {{ color: #666; font-size: 0.9rem; }}
    .back {{ display: inline-block; margin-bottom: 1.5rem; }}
    ul {{ list-style: none; padding: 0; }}
    li {{ border-top: 1px solid #e4e4e4; padding: 0.8rem 0; }}
    .date {{ color: #666; font-size: 0.85rem; display: block; }}
    .name {{ font-weight: 600; }}
    .version {{ font-weight: 400; color: #444; }}
    .links {{ display: block; font-size: 0.9rem; margin-top: 0.2rem; }}
    .desc {{ color: #555; font-size: 0.9rem; margin: 0.4rem 0 0; }}
  </style>
</head>
<body>
  <a class="back" href="/">&larr; Back</a>
  <h1>Latest Distro Releases</h1>
  <p class="meta">Updated: {html.escape(updated)}</p>
  <ul>
{body}
  </ul>
</body>
</html>
"""


def render_atom(releases: list[dict[str, str]], updated: str) -> str:
    root = ET.Element("feed", {"xmlns": "http://www.w3.org/2005/Atom"})
    ET.SubElement(root, "title").text = "DistroWatch releases"
    ET.SubElement(
        root, "subtitle"
    ).text = "Latest distribution releases with homepage and download links"
    ET.SubElement(root, "id").text = f"{SITE}/releases.xml"
    ET.SubElement(root, "updated").text = updated
    ET.SubElement(
        root, "link", {"rel": "self", "type": "application/atom+xml", "href": f"{SITE}/releases.xml"}
    )
    ET.SubElement(
        root, "link", {"rel": "alternate", "type": "text/html", "href": f"{SITE}/releases.html"}
    )

    for release in releases:
        entry = ET.SubElement(root, "entry")
        ET.SubElement(entry, "title").text = release["title"]
        ET.SubElement(entry, "id").text = release["url"]
        ET.SubElement(
            entry, "link", {"rel": "alternate", "type": "text/html", "href": release["url"]}
        )
        stamp = release["published"] or release["date"] or updated
        ET.SubElement(entry, "published").text = stamp
        ET.SubElement(entry, "updated").text = stamp

        parts = []
        if release["icon"]:
            parts.append(
                f'<img src="{html.escape(release["icon"], quote=True)}" '
                f'alt="{html.escape(release["name"], quote=True)}" />'
            )
        if release["description"]:
            parts.append(f"<p>{html.escape(release['description'])}</p>")
        lines = []
        if release["homepage"]:
            lines.append(
                f'<a href="{html.escape(release["homepage"], quote=True)}">Homepage: '
                f'{html.escape(release["homepage"])}</a>'
            )
        if release["iso"]:
            lines.append(
                f'<a href="{html.escape(release["iso"], quote=True)}">Download ISO</a>'
            )
        lines.append(f'<a href="{html.escape(release["url"], quote=True)}">DistroWatch page</a>')
        parts.append("<p>" + "<br />\n".join(lines) + "</p>")
        ET.SubElement(entry, "content", {"type": "html"}).text = "\n".join(parts)

    body = ET.tostring(root, encoding="unicode")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + body + "\n"


def write(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)
    log(f"wrote {path} ({len(content)} bytes)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate DistroWatch release feeds")
    parser.add_argument(
        "--output-dir", default=".", help="where releases.html/.xml/.cache.json go"
    )
    parser.add_argument(
        "--homepages",
        default=None,
        help="path or URL of the homepage override file (default: ./homepages.cfg)",
    )
    parser.add_argument(
        "--cache",
        default=PUBLISHED_CACHE,
        help="URL of the previously published homepage cache",
    )
    parser.add_argument("--delay", type=float, default=POLITE_DELAY)
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args(argv)

    if args.homepages is None and not os.path.isfile(HOMEPAGES_DEFAULT):
        for candidate in (".", os.path.dirname(os.path.abspath(__file__))):
            if os.path.isfile(os.path.join(candidate, HOMEPAGES_DEFAULT)):
                args.homepages = os.path.join(candidate, HOMEPAGES_DEFAULT)
                break

    releases = collect(args)
    updated = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()

    cache = {"updated": updated, "homepages": {r["slug"]: r["homepage"] for r in releases if r["homepage"]}}
    os.makedirs(args.output_dir, exist_ok=True)
    write(os.path.join(args.output_dir, "releases.html"), render_html(releases, updated[:10]))
    write(os.path.join(args.output_dir, "releases.xml"), render_atom(releases, updated))
    write(
        os.path.join(args.output_dir, "releases.cache.json"),
        json.dumps(cache, indent=2, sort_keys=True) + "\n",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
