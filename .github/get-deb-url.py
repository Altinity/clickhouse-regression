import os
import sys
import json

if __name__ == "__main__":
    report_path = os.getenv("REPORT_PATH")

    with open(os.path.join(report_path, "build_urls_package_release.json"), "r", encoding="utf-8") as file_handler:
        build_report = json.load(file_handler)

    for url in build_report["build_urls"]:
        if "clickhouse-common-static" in url and "deb" in url:
            sys.stdout.write(url)
            sys.exit(0)
