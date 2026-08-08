#!/usr/bin/env python3
"""Notify via ntfy when PremierWIFFLE goes live or PLW posts something new.

Checks:
  1) Twitch live status for twitch.tv/premierwiffle
  2) New posts from https://premierleaguewiffle.com/feed/

Pushes to ntfy topic (default: WiffleBall).

Examples:
  python3 scripts/plw_notify.py --seed          # remember current posts, no alerts
  python3 scripts/plw_notify.py                 # check + notify on changes
  python3 scripts/plw_notify.py --dry-run       # print what would be sent
  python3 scripts/plw_notify.py --test          # send a one-off test ping
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.header import Header
from pathlib import Path

TWITCH_LOGIN = "premierwiffle"
TWITCH_URL = f"https://www.twitch.tv/{TWITCH_LOGIN}"
FEED_URL = "https://premierleaguewiffle.com/feed/"
DEFAULT_TOPIC = "WiffleBall"
DEFAULT_SERVER = "https://ntfy.sh"
STATE_PATH = Path(__file__).resolve().parent / "data" / "plw_notify_state.json"
USER_AGENT = "plw-notify/1.0 (+https://github.com/thebrianteahannan/wiffle)"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def http_get(url: str, headers: dict[str, str] | None = None, timeout: int = 30) -> str:
    req_headers = {"User-Agent": USER_AGENT}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, headers=req_headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def http_post(
    url: str,
    body: bytes,
    headers: dict[str, str] | None = None,
    timeout: int = 30,
) -> str:
    req_headers = {"User-Agent": USER_AGENT}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, data=body, headers=req_headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def load_state(path: Path) -> dict:
    if not path.exists():
        return {
            "seeded": False,
            "twitch_live": False,
            "seen_post_ids": [],
            "last_run": None,
        }
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("seeded", False)
    data.setdefault("twitch_live", False)
    data.setdefault("seen_post_ids", [])
    data.setdefault("last_run", None)
    return data


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    state["last_run"] = utc_now()
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, sort_keys=True)
        f.write("\n")
    tmp.replace(path)


def ntfy_publish(
    title: str,
    message: str,
    *,
    topic: str,
    server: str,
    priority: str = "default",
    tags: str = "",
    click: str = "",
    dry_run: bool = False,
) -> None:
    url = f"{server.rstrip('/')}/{topic}"
    # ntfy header values should be ASCII-safe; use RFC 2047 for non-ASCII titles.
    headers = {
        "Title": str(Header(title, "utf-8")) if any(ord(c) > 127 for c in title) else title,
        "Priority": priority,
    }
    if tags:
        headers["Tags"] = tags
    if click:
        headers["Click"] = click
    token = os.environ.get("NTFY_TOKEN") or os.environ.get("NTFY_PASSWORD")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    print(f"[ntfy] {title}: {message}")
    if dry_run:
        print(f"  (dry-run) would POST {url}")
        return
    http_post(url, message.encode("utf-8"), headers=headers)


def twitch_is_live_decapi() -> tuple[bool, str]:
    """Return (is_live, title) using DecAPI (no Twitch app credentials needed)."""
    uptime = http_get(f"https://decapi.me/twitch/uptime/{TWITCH_LOGIN}").strip()
    title = http_get(f"https://decapi.me/twitch/title/{TWITCH_LOGIN}").strip()
    offline = "is offline" in uptime.lower() or uptime.lower() == "offline"
    return (not offline), title


def twitch_is_live_helix(client_id: str, client_secret: str) -> tuple[bool, str]:
    token_body = urllib.parse.urlencode(
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        }
    ).encode()
    token_raw = http_post(
        "https://id.twitch.tv/oauth2/token",
        token_body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    access_token = json.loads(token_raw)["access_token"]
    streams_raw = http_get(
        f"https://api.twitch.tv/helix/streams?user_login={TWITCH_LOGIN}",
        headers={
            "Client-ID": client_id,
            "Authorization": f"Bearer {access_token}",
        },
    )
    data = json.loads(streams_raw).get("data") or []
    if not data:
        return False, ""
    return True, data[0].get("title") or ""


def check_twitch() -> tuple[bool, str]:
    client_id = os.environ.get("TWITCH_CLIENT_ID", "").strip()
    client_secret = os.environ.get("TWITCH_CLIENT_SECRET", "").strip()
    if client_id and client_secret:
        return twitch_is_live_helix(client_id, client_secret)
    return twitch_is_live_decapi()


def fetch_feed_posts(limit: int = 20) -> list[dict]:
    xml_text = http_get(FEED_URL)
    root = ET.fromstring(xml_text)
    posts: list[dict] = []
    for item in root.findall("./channel/item")[:limit]:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        guid = (item.findtext("guid") or link or title).strip()
        # Unescape a few common HTML entities from WordPress titles.
        title = (
            title.replace("&#8211;", "–")
            .replace("&#8212;", "—")
            .replace("&amp;", "&")
            .replace("&#038;", "&")
        )
        posts.append({"id": guid, "title": title, "link": link})
    return posts


def check_and_notify(
    *,
    seed: bool = False,
    dry_run: bool = False,
    topic: str = DEFAULT_TOPIC,
    server: str = DEFAULT_SERVER,
    state_path: Path = STATE_PATH,
) -> int:
    state = load_state(state_path)
    errors: list[str] = []

    # --- Website posts ---
    try:
        posts = fetch_feed_posts()
        seen = set(state.get("seen_post_ids") or [])
        if seed or not state.get("seeded"):
            for post in posts:
                seen.add(post["id"])
            state["seen_post_ids"] = sorted(seen)
            state["seeded"] = True
            print(f"[feed] seeded {len(posts)} current posts (no alerts)")
        else:
            new_posts = [p for p in posts if p["id"] not in seen]
            # Notify oldest-new first so push order matches publish order.
            for post in reversed(new_posts):
                ntfy_publish(
                    title="PLW website update",
                    message=post["title"] or "New post on premierleaguewiffle.com",
                    topic=topic,
                    server=server,
                    priority="default",
                    tags="newspaper,plw",
                    click=post["link"] or "https://premierleaguewiffle.com/",
                    dry_run=dry_run,
                )
                seen.add(post["id"])
            if new_posts:
                print(f"[feed] {len(new_posts)} new post(s)")
            else:
                print("[feed] no new posts")
            # Keep state bounded.
            known_order = [p["id"] for p in posts] + [i for i in seen if i not in {p["id"] for p in posts}]
            state["seen_post_ids"] = known_order[:100]
    except Exception as exc:  # noqa: BLE001 - keep cron resilient
        errors.append(f"feed: {exc}")
        print(f"[feed] ERROR: {exc}", file=sys.stderr)

    # --- Twitch live ---
    try:
        live, title = check_twitch()
        was_live = bool(state.get("twitch_live"))
        print(f"[twitch] live={live} title={title!r} was_live={was_live}")
        if live and not was_live:
            msg = title.strip() if title else "PremierWIFFLE is live"
            ntfy_publish(
                title="PLW is LIVE on Twitch",
                message=msg,
                topic=topic,
                server=server,
                priority="high",
                tags="rotating_light,twitch,plw",
                click=TWITCH_URL,
                dry_run=dry_run,
            )
        state["twitch_live"] = live
        if title:
            state["twitch_title"] = title
    except Exception as exc:  # noqa: BLE001
        errors.append(f"twitch: {exc}")
        print(f"[twitch] ERROR: {exc}", file=sys.stderr)

    if not dry_run:
        save_state(state_path, state)
    else:
        print(f"[state] dry-run; not writing {state_path}")

    if errors:
        print("Completed with errors:", "; ".join(errors), file=sys.stderr)
        return 1
    return 0


def send_test(topic: str, server: str, dry_run: bool) -> int:
    ntfy_publish(
        title="WiffleBall notify OK",
        message="PLW Twitch + website notifier is wired up.",
        topic=topic,
        server=server,
        tags="white_check_mark,plw",
        click="https://www.twitch.tv/premierwiffle",
        dry_run=dry_run,
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", action="store_true", help="Seed current posts without notifying")
    parser.add_argument("--dry-run", action="store_true", help="Do not send or write state")
    parser.add_argument("--test", action="store_true", help="Send a test notification and exit")
    parser.add_argument("--topic", default=os.environ.get("NTFY_TOPIC", DEFAULT_TOPIC))
    parser.add_argument("--server", default=os.environ.get("NTFY_SERVER", DEFAULT_SERVER))
    parser.add_argument("--state", type=Path, default=STATE_PATH)
    args = parser.parse_args(argv)

    if args.test:
        return send_test(args.topic, args.server, args.dry_run)
    return check_and_notify(
        seed=args.seed,
        dry_run=args.dry_run,
        topic=args.topic,
        server=args.server,
        state_path=args.state,
    )


if __name__ == "__main__":
    raise SystemExit(main())
