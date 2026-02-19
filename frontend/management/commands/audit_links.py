import json
import re
from collections import deque
from urllib.parse import urlparse

from django.core.management.base import BaseCommand
from django.test import Client


class Command(BaseCommand):
    help = "Audit internal links/buttons/forms using Django test client (no nginx rate-limit noise)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--max-pages",
            type=int,
            default=120,
            help="Maximum HTML pages to crawl (default: 120)",
        )
        parser.add_argument(
            "--max-check",
            type=int,
            default=300,
            help="Maximum discovered paths to check (default: 300)",
        )
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Exit with code 1 if 5xx pages are found.",
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Print machine-readable JSON summary.",
        )

    def handle(self, *args, **options):
        client = Client(HTTP_HOST="localhost")

        seeds = [
            "/",
            "/ru/",
            "/bizneslar/",
            "/kategoriyalar/",
            "/privacy/",
            "/terms/",
            "/guidelines/",
            "/accounts/login/",
            "/admin/login/",
        ]

        href_re = re.compile(r"(?:href|src)=[\"\']([^\"\'#]+)[\"\']", re.I)
        action_re = re.compile(r"action=[\"\']([^\"\']*)[\"\']", re.I)
        formaction_re = re.compile(r"formaction=[\"\']([^\"\']+)[\"\']", re.I)
        onclick_re = re.compile(
            r"location(?:\\.href)?\\s*=\\s*[\"\']([^\"\']+)[\"\']", re.I
        )

        visited = {}
        discovered = set()
        unresolved_dynamic_refs = set()

        queue = deque(seeds)
        max_pages = max(1, int(options["max_pages"]))
        max_check = max(1, int(options["max_check"]))

        while queue and len(visited) < max_pages:
            path = queue.popleft()
            if not path.startswith("/") or path in visited:
                continue

            try:
                response = client.get(path)
                status_code = response.status_code
                content_type = response.get("Content-Type", "")
                html = (
                    response.content.decode("utf-8", "ignore")
                    if "text/html" in content_type
                    else ""
                )
            except Exception as exc:
                visited[path] = {"status": None, "error": str(exc)[:200]}
                continue

            visited[path] = {"status": status_code}
            if not html:
                continue

            for regex in (href_re, action_re, formaction_re, onclick_re):
                for value in regex.findall(html):
                    if not value:
                        continue

                    if "${" in value:
                        unresolved_dynamic_refs.add(value)
                        continue

                    if value.startswith(("mailto:", "tel:", "javascript:", "#")):
                        continue

                    parsed = urlparse(value)
                    if parsed.scheme or parsed.netloc:
                        continue

                    candidate = value if value.startswith("/") else f"/{value}"
                    discovered.add(candidate)

                    if candidate not in visited and len(visited) + len(queue) < (
                        max_pages * 4
                    ):
                        queue.append(candidate)

        checked_paths = sorted(discovered)[:max_check]

        buckets = {"2xx": 0, "3xx": 0, "4xx": 0, "5xx": 0, "err": 0}
        failures = []

        for path in checked_paths:
            try:
                status_code = client.get(path).status_code
            except Exception as exc:
                status_code = None
                failures.append(
                    {
                        "path": path,
                        "status": None,
                        "error": str(exc)[:200],
                    }
                )

            if status_code is None:
                buckets["err"] += 1
                continue

            if 200 <= status_code < 300:
                buckets["2xx"] += 1
            elif 300 <= status_code < 400:
                buckets["3xx"] += 1
            elif 400 <= status_code < 500:
                buckets["4xx"] += 1
                failures.append({"path": path, "status": status_code})
            else:
                buckets["5xx"] += 1
                failures.append({"path": path, "status": status_code})

        summary = {
            "pages_visited": len(visited),
            "paths_discovered": len(discovered),
            "paths_checked": len(checked_paths),
            "buckets": buckets,
            "failures": failures[:100],
            "dynamic_refs": sorted(unresolved_dynamic_refs)[:100],
        }

        if options["json"]:
            self.stdout.write(json.dumps(summary, ensure_ascii=False, indent=2))
        else:
            self.stdout.write(self.style.SUCCESS("Link and button audit completed."))
            self.stdout.write(f"Pages visited: {summary['pages_visited']}")
            self.stdout.write(f"Paths discovered: {summary['paths_discovered']}")
            self.stdout.write(f"Paths checked: {summary['paths_checked']}")
            self.stdout.write(f"Buckets: {summary['buckets']}")

            if summary["dynamic_refs"]:
                self.stdout.write(
                    self.style.WARNING(
                        f"Dynamic placeholder refs found: {len(summary['dynamic_refs'])}"
                    )
                )
                for ref in summary["dynamic_refs"][:10]:
                    self.stdout.write(f"  - {ref}")

            if summary["failures"]:
                self.stdout.write(
                    self.style.WARNING(
                        f"Failing routes found: {len(summary['failures'])}"
                    )
                )
                for item in summary["failures"][:20]:
                    status = item.get("status")
                    path = item.get("path")
                    self.stdout.write(f"  - {status} {path}")
            else:
                self.stdout.write(self.style.SUCCESS("No failing routes in checked set."))

        if options["strict"] and (summary["buckets"]["5xx"] > 0 or summary["buckets"]["err"] > 0):
            raise SystemExit(1)
