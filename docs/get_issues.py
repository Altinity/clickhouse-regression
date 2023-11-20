import json
import requests

r = requests.get(
    "https://api.github.com/repos/ClickHouse/ClickHouse/issues?labels=v23.8-affected"
)

for issue in r.json():
    print("* " + issue["title"] + "  ")
    print("  " + issue["html_url"])
