"""Quick verification that offline .eae bundles contain dense polygon paths."""
from __future__ import annotations

import json
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3] / "mobile" / "assets" / "geography"


def main() -> int:
    files = sorted(ROOT.glob("*.eae"))
    assert len(files) == 12, f"expected 12 eae, got {len(files)}"
    for f in files:
        data = json.loads(zlib.decompress(f.read_bytes()))
        svg = data["svg_content"]
        path_count = svg.count("<path ")
        long_segments = svg.count(" L")
        assert f.stat().st_size >= 10_000, f"{f.name} too small"
        assert path_count >= 50, f"{f.name} path_count={path_count}"
        assert long_segments >= 200, f"{f.name} L-count={long_segments}"
        print(f"OK {f.name}: {f.stat().st_size}B paths={path_count} L={long_segments}")
    print("all offline bundles contain real polygon geometry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
