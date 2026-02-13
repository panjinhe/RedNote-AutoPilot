from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Launch Chromium with a persistent profile for one-time manual login, "
            "then save storage state for later automation runs."
        )
    )
    parser.add_argument(
        "--url",
        default="https://ark.xiaohongshu.com/app-item/list/shelf",
        help="Target URL to open for manual login.",
    )
    parser.add_argument(
        "--user-data-dir",
        default=".browser/xhs-profile",
        help="Directory to persist browser profile data.",
    )
    parser.add_argument(
        "--state-path",
        default=".browser/storage_state.json",
        help="Path to write Playwright storage state.",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        default=True,
        help="Launch in headed mode (default true).",
    )
    return parser.parse_args()


def main() -> None:
    from playwright.sync_api import sync_playwright

    args = parse_args()
    user_data_dir = Path(args.user_data_dir)
    state_path = Path(args.state_path)

    user_data_dir.mkdir(parents=True, exist_ok=True)
    state_path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(user_data_dir),
            headless=not args.headed,
            viewport={"width": 1600, "height": 1000},
        )
        page = context.new_page()
        page.goto(args.url, wait_until="domcontentloaded")

        print("\n[login_once] Browser opened.")
        print("[login_once] Please finish login manually in this window.")
        input("[login_once] After successful login, press Enter here to save state...\n")

        context.storage_state(path=str(state_path))
        print(f"[login_once] Saved storage state => {state_path}")

        context.close()


if __name__ == "__main__":
    main()
