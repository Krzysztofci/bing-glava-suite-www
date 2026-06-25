import urllib.request
import json
import re

GITHUB_USERNAME = "Krzysztofci"
HTML_FILE_PATH = "index.html"
MAX_COMMITS = 5

import os

def fetch_commits():
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos"
    req = urllib.request.Request(url)

    repos = json.loads(urllib.request.urlopen(req).read().decode())

    all_commits = []

    for repo in repos:
        name = repo["name"]
        commits_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{name}/commits"

        try:
            req = urllib.request.Request(commits_url)
            data = json.loads(urllib.request.urlopen(req).read().decode())

            for c in data[:5]:
                date_raw = c["commit"]["author"]["date"]
                dt = date_raw[:16].replace("T", " ")

                all_commits.append({
                    "time": dt,
                    "repo": name,
                    "msg": c["commit"]["message"].split("\n")[0]
                })

        except Exception:
            continue

    # global sort
    all_commits.sort(key=lambda x: x["time"], reverse=True)

    return all_commits[:5]

def generate_html_rows(commits):
    if not commits:
        return '      <div class="status-row"><span class="status-msg">No recent activity found.</span></div>'
        
    html_rows = []
    for c in commits:
        row = f"""      <div class="status-row">
        <span class="status-time">{c['time']}</span>
        <span class="status-repo">{c['repo']}</span>
        <span class="status-msg">{c['msg']}</span>
      </div>"""
        html_rows.append(row)
    return "\n".join(html_rows)

def update_index_html(new_html_content):
    with open(HTML_FILE_PATH, "r", encoding="utf-8") as file:
        content = file.read()
        
    # Bezpieczny regex, który nigdy nie wyjdzie poza wyznaczone komentarze HTML
    pattern = r"(<!-- ACTIVITY_START -->)[\s\S]*?(<!-- ACTIVITY_END -->)"
    
    if not re.search(pattern, content):
        print("Błąd: Nie znaleziono znaczników komentarza <!-- ACTIVITY_START --> w index.html")
        return
        
    # Zastępuje całą starą zawartość nową, gwarantując idempotentność
    modified_content = re.sub(pattern, f"\\1\n{new_html_content}\n\\2", content)
    
    with open(HTML_FILE_PATH, "w", encoding="utf-8") as file:
        file.write(modified_content)

if __name__ == "__main__":
    latest_commits = fetch_commits()

    print("\n=== DEBUG PARSED COMMITS ===")
    print(f"Commits count: {len(latest_commits)}")

    for c in latest_commits:
        print(c)

    html_markup = generate_html_rows(latest_commits)
    update_index_html(html_markup)
