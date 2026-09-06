from __future__ import annotations
import json, os, urllib.request
from collections import Counter
from pathlib import Path

USER = os.getenv("PROFILE_USER", "gtmdev-br")
TOKEN = os.getenv("GITHUB_TOKEN", "")
OUT = Path("assets/metrics.svg")
OUT.parent.mkdir(parents=True, exist_ok=True)

def get(url):
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "gtmdev-profile-metrics",
        **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {})
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

user = get(f"https://api.github.com/users/{USER}")
repos = []
page = 1
while True:
    chunk = get(f"https://api.github.com/users/{USER}/repos?per_page=100&page={page}&sort=updated")
    if not chunk:
        break
    repos.extend(chunk)
    if len(chunk) < 100:
        break
    page += 1

owned = [r for r in repos if not r.get("fork") and not r.get("archived")]
stars = sum(int(r.get("stargazers_count", 0)) for r in owned)
forks = sum(int(r.get("forks_count", 0)) for r in owned)
langs = Counter(r.get("language") for r in owned if r.get("language"))
top_langs = " · ".join(x for x, _ in langs.most_common(4)) or "Building"

vals = {
    "repos": user.get("public_repos", 0),
    "stars": stars,
    "forks": forks,
    "followers": user.get("followers", 0),
    "langs": top_langs,
}

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="250" viewBox="0 0 1100 250">
<defs>
  <linearGradient id="bg" x1="0" x2="1"><stop stop-color="#0d1117"/><stop offset="1" stop-color="#120d20"/></linearGradient>
  <linearGradient id="n" x1="0" x2="1"><stop stop-color="#00e5ff"/><stop offset=".5" stop-color="#7c3aed"/><stop offset="1" stop-color="#00e5ff"/></linearGradient>
  <filter id="g"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="1100" height="250" rx="22" fill="url(#bg)" stroke="#263244"/>
<rect x="0" y="0" width="1100" height="3" fill="url(#n)"/>
<text x="42" y="48" fill="#8b949e" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="13" letter-spacing="1.5">PUBLIC GITHUB TELEMETRY / AUTO-UPDATED</text>
<circle cx="1028" cy="42" r="5" fill="#00e5ff" filter="url(#g)"><animate attributeName="opacity" values="1;.25;1" dur="1.6s" repeatCount="indefinite"/></circle>
<g font-family="ui-monospace,SFMono-Regular,Menlo,monospace">
  <g transform="translate(42,84)">
    <rect width="230" height="98" rx="14" fill="#0a111a" stroke="#164e63"/>
    <text x="20" y="30" fill="#64748b" font-size="12">PUBLIC REPOS</text>
    <text x="20" y="72" fill="#f8fafc" font-size="34" font-weight="700">{vals["repos"]}</text>
  </g>
  <g transform="translate(288,84)">
    <rect width="230" height="98" rx="14" fill="#100d1d" stroke="#4c1d95"/>
    <text x="20" y="30" fill="#64748b" font-size="12">TOTAL STARS</text>
    <text x="20" y="72" fill="#f8fafc" font-size="34" font-weight="700">{vals["stars"]}</text>
  </g>
  <g transform="translate(534,84)">
    <rect width="230" height="98" rx="14" fill="#0a111a" stroke="#164e63"/>
    <text x="20" y="30" fill="#64748b" font-size="12">FORKS</text>
    <text x="20" y="72" fill="#f8fafc" font-size="34" font-weight="700">{vals["forks"]}</text>
  </g>
  <g transform="translate(780,84)">
    <rect width="278" height="98" rx="14" fill="#100d1d" stroke="#4c1d95"/>
    <text x="20" y="30" fill="#64748b" font-size="12">FOLLOWERS</text>
    <text x="20" y="72" fill="#f8fafc" font-size="34" font-weight="700">{vals["followers"]}</text>
  </g>
  <text x="42" y="222" fill="#94a3b8" font-size="13">TOP LANGUAGES  /  {vals["langs"]}</text>
</g>
<rect x="-180" y="0" width="150" height="250" fill="#00e5ff" opacity=".025">
  <animate attributeName="x" values="-180;1130" dur="5s" repeatCount="indefinite"/>
</rect>
</svg>'''
OUT.write_text(svg)
print(f"wrote {OUT}")
