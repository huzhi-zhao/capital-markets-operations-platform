"""抽取 ISO 20022 External Code Sets 与银行交易码组合表，产出计数 manifest 与判定用词表。

只用标准库。电子表格按单元格坐标取列，不按出现顺序：空单元格在文件里直接缺席，
按顺序读会把整行左移（验证规范 §2C 记录过这个坑）。

用法：
    python3 tools/iso20022-codesets/extract.py --src ~/Downloads [--out DIR] [--manifest PATH]

--src 下需要 ExternalCodeSets_XLSX.zip、ExternalCodeSets_JSON.zip、BTC_Codification_30Nov2025.xlsx。
--out 给出时写两份 TSV 词表；它们是注册机构发布内容的派生物，再分发条款未确认前不入库。
"""
import argparse
import hashlib
import io
import json
import re
import sys
import zipfile
from collections import Counter
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

M = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
SOURCES = {
    "xlsx_zip": "ExternalCodeSets_XLSX.zip",
    "json_zip": "ExternalCodeSets_JSON.zip",
    "btc_xlsx": "BTC_Codification_30Nov2025.xlsx",
}
CMOP_DOMAINS = ("PMNT", "SECU")
CMOP_COMBINATIONS = (("PMNT", "ICDT", "FICT"), ("PMNT", "RCDT", "FICT"), ("SECU", "SETT", "TRAD"))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def single_member(zip_path):
    z = zipfile.ZipFile(zip_path)
    names = z.namelist()
    if len(names) != 1:
        sys.exit(f"{zip_path.name}: expected one member, found {names}")
    return names[0], z.read(names[0])


def sheets(xlsx_bytes):
    """返回 {工作表名: [(行号, {列字母: 值})]}，按坐标取列。"""
    z = zipfile.ZipFile(io.BytesIO(xlsx_bytes))
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall(f"{{{M}}}si"):
            shared.append("".join(t.text or "" for t in si.iter(f"{{{M}}}t")))
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    out = {}
    for s in ET.fromstring(z.read("xl/workbook.xml")).find(f"{{{M}}}sheets"):
        target = rels[s.get(f"{{{R}}}id")].lstrip("/")
        path = target if target.startswith("xl/") else "xl/" + target
        rows = []
        for row in ET.fromstring(z.read(path)).iter(f"{{{M}}}row"):
            cells = {}
            for c in row.findall(f"{{{M}}}c"):
                col = re.match(r"[A-Z]+", c.get("r")).group()
                kind, v = c.get("t"), c.find(f"{{{M}}}v")
                if kind == "inlineStr":
                    cells[col] = "".join(t.text or "" for t in c.iter(f"{{{M}}}t"))
                elif v is not None:
                    cells[col] = shared[int(v.text)] if kind == "s" else v.text
            rows.append((int(row.get("r")), cells))
        out[s.get("name")] = rows
    return out


def header_index(rows, required):
    """找到含全部必需列名的表头行，返回 (表头行号, {列名: 列字母})。"""
    for n, cells in rows:
        names = {v.strip(): k for k, v in cells.items()}
        if all(r in names for r in required):
            return n, {r: names[r] for r in required}
    sys.exit(f"header with {required} not found")


def code_sets(sheet):
    hdr, col = header_index(sheet, ("Code Set", "Code Value", "Status"))
    return [(c.get(col["Code Set"], ""), c.get(col["Code Value"], ""), c.get(col["Status"], ""))
            for n, c in sheet if n > hdr and c.get(col["Code Set"])]


def btc_rows(sheet):
    # 表头单元格带换行，形如 "Domain Code\nExternalBankTransactionDomain1Code"，按首行匹配
    for n, cells in sheet:
        first = {v.split("\n")[0].strip(): k for k, v in cells.items()}
        if {"Domain Code", "Family Code", "SubFamily Code", "Status"} <= first.keys():
            d, f, s, st = (first[k] for k in ("Domain Code", "Family Code", "SubFamily Code", "Status"))
            return [(c.get(d, ""), c.get(f, ""), c.get(s, ""), c.get(st, ""))
                    for m, c in sheet if m > n and c.get(d)]
    sys.exit("BTC header not found")


def extract(src):
    src = Path(src).expanduser()
    files = {k: src / v for k, v in SOURCES.items()}
    missing = [str(p) for p in files.values() if not p.exists()]
    if missing:
        raise FileNotFoundError(", ".join(missing))

    xlsx_name, xlsx_bytes = single_member(files["xlsx_zip"])
    json_name, json_bytes = single_member(files["json_zip"])
    book = sheets(xlsx_bytes)
    codes = code_sets(book["AllCodeSets"])
    intro = {c.get("A", "").strip(): c.get("B", "") for _, c in book["Intro&History"]}

    status = Counter(st for _, _, st in codes)
    registered = {}
    obsolete_by_set = Counter()
    for cs, cv, st in codes:
        registered.setdefault(cs, set())
        if st == "Registered":
            registered[cs].add(cv)
        elif st == "Obsolete":
            obsolete_by_set[cs] += 1

    schema = json.loads(json_bytes)
    enumerated = {k: set(v["enum"]) for k, v in schema["definitions"].items() if "enum" in v}
    mismatched = sorted(k for k, v in enumerated.items() if v != registered.get(k, set()))

    btc = btc_rows(sheets(files["btc_xlsx"].read_bytes())["BTC_Codification"])
    per_domain = Counter(d for d, _, _, _ in btc)
    combos = {(d, f, s) for d, f, s, _ in btc}

    manifest = {
        "extracted_on": date.today().isoformat(),
        "extractor": "tools/iso20022-codesets/extract.py",
        "sources": {k: {"file": p.name, "sha256": sha256(p)} for k, p in files.items()},
        "external_code_sets": {
            "xlsx_member": xlsx_name,
            "json_member": json_name,
            "publication_date_in_workbook": intro.get("Publication date"),
            "codes_total": len(codes),
            "code_sets_in_xlsx": len(registered),
            "codes_by_status": dict(sorted(status.items())),
            "obsolete_by_code_set": dict(sorted(obsolete_by_set.items())),
            "json_enumerated_code_sets": len(enumerated),
            "json_codes_total": sum(len(v) for v in enumerated.values()),
            "json_sets_differing_from_xlsx_registered": mismatched,
        },
        "bank_transaction_codes": {
            "combinations_total": len(btc),
            "distinct_combinations": len(combos),
            "combinations_by_status": dict(sorted(Counter(st for *_, st in btc).items())),
            "combinations_by_domain": dict(sorted(per_domain.items())),
            "cmop_domains": list(CMOP_DOMAINS),
            "cmop_domain_combinations": sum(per_domain[d] for d in CMOP_DOMAINS),
            "cmop_combinations_present": {"/".join(c): c in combos for c in CMOP_COMBINATIONS},
        },
    }
    return manifest, codes, btc


def write_tsv(path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(header) + "\n")
        for r in sorted(rows):
            f.write("\t".join(r) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--manifest", default=str(Path(__file__).resolve().parents[2]
                                              / "data/reference/iso20022/manifest.json"))
    ap.add_argument("--out")
    a = ap.parse_args()
    manifest, codes, btc = extract(a.src)
    Path(a.manifest).parent.mkdir(parents=True, exist_ok=True)
    Path(a.manifest).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if a.out:
        out = Path(a.out)
        write_tsv(out / "external-code-sets.tsv", ("code_set", "code_value", "status"), codes)
        write_tsv(out / "bank-transaction-codes.tsv", ("domain", "family", "subfamily", "status"), btc)
    print(json.dumps(manifest["external_code_sets"] | manifest["bank_transaction_codes"], indent=1))


if __name__ == "__main__":
    main()
