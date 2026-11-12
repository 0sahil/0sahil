"""Refresh the 'Recently shipped' list in README.md: the newest release of
each of my public, non-fork repos (one line per repo, no dates). Runs daily from .github/workflows/update.yml.
Stdlib only; reads GITHUB_TOKEN from the environment."""
import json, os, re, urllib.request

USER, LIMIT, README = "0sahil", 5, "README.md"
QUERY = """query($login:String!){user(login:$login){repositories(first:100,privacy:PUBLIC,isFork:false,
orderBy:{field:PUSHED_AT,direction:DESC}){nodes{name url primaryLanguage{name}
releases(first:5,orderBy:{field:CREATED_AT,direction:DESC}){nodes{name tagName url publishedAt isDraft isPrerelease}}}}}}"""

req = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
    headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"},
)
repos = json.load(urllib.request.urlopen(req))["data"]["user"]["repositories"]["nodes"]
latest = []
for repo in repos:
    if repo["name"] == USER:
        continue
    for r in repo["releases"]["nodes"]:
        if r["publishedAt"] and not r["isDraft"] and not r["isPrerelease"]:
            lang = (repo.get("primaryLanguage") or {}).get("name")
            latest.append((r["publishedAt"], repo["name"], r["tagName"], r["url"], lang))
            break  # newest published release of this repo only
latest = sorted(latest, reverse=True)[:LIMIT]

def title(name):
    return name.replace("-", " ").title()

lines = "\n".join(
    f"- **[{title(name)} {tag}]({url})**" + (f" · {lang}" if lang else "")
    for _, name, tag, url, lang in latest
) or "- Nothing yet."
readme = open(README).read()
new = re.sub(r"(<!-- releases:start -->\n).*?(\n<!-- releases:end -->)", lambda m: m.group(1) + lines + m.group(2), readme, flags=re.S)
if new != readme:
    open(README, "w").write(new)
    print("README updated")
else:
    print("no change")
