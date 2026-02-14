from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


class AndroidDeviceClient:
    """ADB client for minimal device interactions used by DeviceAutoChannel."""

    def __init__(self, device_id: str, adb_path: str = "adb", artifact_dir: str = "artifacts/android") -> None:
        self.device_id = device_id
        self.adb_path = adb_path
        self.artifact_dir = Path(artifact_dir)
        self.artifact_dir.mkdir(parents=True, exist_ok=True)

    def _run(self, args: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
        cmd = [self.adb_path, "-s", self.device_id, *args]
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)

    def tap(self, x: int, y: int) -> bool:
        return self._run(["shell", "input", "tap", str(x), str(y)]).returncode == 0

    def input_text(self, text: str) -> bool:
        escaped = text.replace(" ", "%s")
        return self._run(["shell", "input", "text", escaped]).returncode == 0

    def start_app(self, package: str, activity: str) -> bool:
        res = self._run(["shell", "am", "start", "-n", f"{package}/{activity}"])
        return res.returncode == 0

    def screenshot(self, filename: str) -> str:
        remote = "/sdcard/rednote_autopilot_screen.png"
        local = self.artifact_dir / filename
        self._run(["shell", "screencap", "-p", remote])
        self._run(["pull", remote, str(local)])
        self._run(["shell", "rm", "-f", remote])
        return str(local)

    def health(self) -> dict[str, Any]:
        res = self._run(["get-state"])
        return {
            "ok": res.returncode == 0 and "device" in (res.stdout or "").strip(),
            "stdout": res.stdout.strip(),
            "stderr": res.stderr.strip(),
        }
