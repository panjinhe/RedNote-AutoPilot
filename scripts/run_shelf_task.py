from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run shelf page automation with a persisted Playwright browser profile/session."
    )
    parser.add_argument(
        "--url",
        default="https://ark.xiaohongshu.com/app-item/list/shelf",
        help="Shelf page URL.",
    )
    parser.add_argument(
        "--user-data-dir",
        default=".browser/xhs-profile",
        help="Persistent profile directory used in login_once.py.",
    )
    parser.add_argument(
        "--state-path",
        default=".browser/storage_state.json",
        help="Optional storage state exported by login_once.py.",
    )
    parser.add_argument(
        "--artifact-dir",
        default="artifacts/browser",
        help="Directory to write screenshot and captured API data.",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        default=True,
        help="Launch in headed mode (default true).",
    )
    parser.add_argument(
        "--capture-api-substring",
        default="shelf",
        help="Capture first API response URL containing this substring.",
    )
    parser.add_argument(
        "--browser",
        default="msedge",
        choices=["msedge", "chrome", "chromium"],
        help="Browser channel to use (default msedge).",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Enable interactive mode: keep browser open for manual navigation, press Enter to save and exit.",
    )
    parser.add_argument(
        "--wait-for-new-tab",
        action="store_true",
        help="In interactive mode, wait for a new tab to open and switch to it.",
    )
    return parser.parse_args()


def utc_stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def main() -> None:
    from playwright.sync_api import sync_playwright

    args = parse_args()

    artifact_dir = Path(args.artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)

    user_data_dir = Path(args.user_data_dir)
    user_data_dir.mkdir(parents=True, exist_ok=True)

    state_path = Path(args.state_path)

    captured: dict[str, object] = {"target": args.url, "captured_at": datetime.now(UTC).isoformat()}

    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(user_data_dir),
            headless=not args.headed,
            viewport={"width": 1600, "height": 1000},
            channel=args.browser,
        )

        if state_path.exists():
            cookies = json.loads(state_path.read_text(encoding="utf-8")).get("cookies", [])
            if cookies:
                context.add_cookies(cookies)

        page = context.new_page()

        def on_response(response) -> None:  # type: ignore[no-untyped-def]
            if args.capture_api_substring not in response.url:
                return
            if "api" not in response.url and "gateway" not in response.url:
                return
            if "api_sample" in captured:
                return
            try:
                payload = response.json()
            except Exception:
                return
            captured["api_sample"] = {
                "url": response.url,
                "status": response.status,
                "payload": payload,
            }

        page.on("response", on_response)

        page.goto(args.url, wait_until="domcontentloaded")

        if args.interactive:
            # Interactive mode: let user manually navigate, press Enter to save and exit
            print("\n[run_shelf_task] Interactive mode - you can now click links in the browser")
            
            if args.wait_for_new_tab:
                print("[run_shelf_task] Waiting for new tab to open...")
                # Wait for new tab (max 30 seconds)
                context.wait_for_event("page", timeout=30000)
                # Get all pages and switch to the newest one
                all_pages = context.pages
                if len(all_pages) > 1:
                    page = all_pages[-1]
                    print(f"[run_shelf_task] Switched to new tab (now have {len(all_pages)} tabs)")
                print("[run_shelf_task] New tab detected! You can now interact with it.")
            
            print("[run_shelf_task] After completing your navigation, press Enter here to save state...")
            input()
        else:
            page.wait_for_timeout(5000)

        screenshot_path = artifact_dir / f"shelf_{utc_stamp()}.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        print(f"[run_shelf_task] Saved screenshot => {screenshot_path}")

        state_export = artifact_dir / f"storage_state_{utc_stamp()}.json"
        context.storage_state(path=str(state_export))
        print(f"[run_shelf_task] Exported current storage state => {state_export}")

        sample_path = artifact_dir / f"api_sample_{utc_stamp()}.json"
        sample_path.write_text(
            json.dumps(captured, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"[run_shelf_task] Saved API sample => {sample_path}")

        context.close()


if __name__ == "__main__":
    main()
