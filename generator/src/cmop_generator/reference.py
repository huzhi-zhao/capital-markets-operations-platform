"""读取已钉住的 SEC 参考数据：标的全集与退市日期。"""
import gzip
import json
import re
from datetime import date
from pathlib import Path

FORM25_LINE = re.compile(r"^25(?:-NSE)?\s.*?\s(\d+)\s+(\d{4}-\d{2}-\d{2})\s+edgar/")


def load_universe(sec_dir: Path):
    ciks = [int(x) for x in (sec_dir / "raw" / "universe-ciks.txt").read_text().split()]
    return sorted(ciks)


def load_delistings(sec_dir: Path):
    """每个 CIK 取窗口内最早一次 Form 25 日期。"""
    out = {}
    for f in sorted((sec_dir / "raw" / "idx").glob("form25-*.txt.gz")):
        with gzip.open(f, "rt", encoding="latin-1") as fh:
            for line in fh:
                m = FORM25_LINE.match(line)
                if not m:
                    continue
                cik, d = int(m.group(1)), date.fromisoformat(m.group(2))
                if cik not in out or d < out[cik]:
                    out[cik] = d
    return out


def manifest_extracted_on(sec_dir: Path):
    return json.loads((sec_dir / "manifest.json").read_text())["extracted_on"]
