import os
import requests

TOKEN = os.environ["GITHUB_TOKEN"]
USERNAME = os.environ["GITHUB_USERNAME"]

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

def get_all_repos():
    repos = []
    page = 1
    while True:
        # 'affiliation=owner' gets only YOUR repos (public + private)
        url = f"https://api.github.com/user/repos?per_page=100&page={page}&affiliation=owner"
        res = requests.get(url, headers=headers)
        data = res.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos

def get_languages(repo_full_name):
    url = f"https://api.github.com/repos/{repo_full_name}/languages"
    res = requests.get(url, headers=headers)
    return res.json()  # { "Python": 12345, "JavaScript": 6789 }

# Aggregate language bytes across all repos
all_languages = {}
repos = get_all_repos()

for repo in repos:
    if repo.get("fork"):
        continue  # Skip forked repos (remove this line to include forks)
    langs = get_languages(repo["full_name"])
    for lang, bytes_count in langs.items():
        all_languages[lang] = all_languages.get(lang, 0) + bytes_count

# Sort by usage (most used first)
sorted_langs = sorted(all_languages.items(), key=lambda x: x[1], reverse=True)
total_bytes = sum(b for _, b in sorted_langs)

# Build markdown table
lines = ["| Language | Usage |", "|----------|-------|"]
for lang, bytes_count in sorted_langs:
    percent = (bytes_count / total_bytes) * 100
    bar_filled = int(percent / 5)  # Each block = 5%
    bar = "█" * bar_filled + "░" * (20 - bar_filled)
    lines.append(f"| {lang} | `{bar}` {percent:.1f}% |")

new_section = "\n".join(lines)

# Update README.md
with open("README.md", "r") as f:
    content = f.read()

start_tag = "<!-- LANGUAGE_STATS_START -->"
end_tag = "<!-- LANGUAGE_STATS_END -->"

start_idx = content.find(start_tag) + len(start_tag)
end_idx = content.find(end_tag)

new_content = (
    content[:start_idx]
    + "\n"
    + new_section
    + "\n"
    + content[end_idx:]
)

with open("README.md", "w") as f:
    f.write(new_content)

print(f"✅ Updated README with {len(sorted_langs)} languages from {len(repos)} repos.")
