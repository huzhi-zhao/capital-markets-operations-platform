"""已提交的 manifest 必须给出文档引用的数字；源文件在场时，重跑抽取必须得到同一份计数。

源文件目录由 CMOP_ISO20022_SRC 指定，默认 ~/Downloads。源文件不在场时只检查已提交的 manifest。
"""
import importlib.util
import json
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "data/reference/iso20022/manifest.json"
SRC = Path(os.environ.get("CMOP_ISO20022_SRC", "~/Downloads")).expanduser()

spec = importlib.util.spec_from_file_location("extract", ROOT / "tools/iso20022-codesets/extract.py")
extract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extract)

HAVE_SOURCES = all((SRC / name).exists() for name in extract.SOURCES.values())


@pytest.fixture(scope="module")
def committed():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_code_set_counts(committed):
    ecs = committed["external_code_sets"]
    assert ecs["codes_total"] == 3347
    assert ecs["codes_by_status"] == {"Obsolete": 33, "Registered": 3314}
    assert ecs["obsolete_by_code_set"] == {
        "ExternalCashClearingSystem1Code": 1,
        "ExternalClearingSystemIdentification1Code": 4,
        "ExternalLocalInstrument1Code": 25,
        "ExternalUndertakingDocumentType2Code": 3,
    }


def test_json_is_exactly_xlsx_registered(committed):
    ecs = committed["external_code_sets"]
    assert ecs["json_enumerated_code_sets"] == 140
    assert ecs["json_codes_total"] == 3314
    assert ecs["json_sets_differing_from_xlsx_registered"] == []


def test_bank_transaction_code_counts(committed):
    btc = committed["bank_transaction_codes"]
    assert btc["combinations_total"] == 1567
    assert btc["cmop_domain_combinations"] == 829
    assert btc["combinations_by_domain"]["PMNT"] == 433
    assert btc["combinations_by_domain"]["SECU"] == 396
    assert all(btc["cmop_combinations_present"].values())


@pytest.mark.skipif(not HAVE_SOURCES, reason=f"ISO 20022 source files not found in {SRC}")
def test_rerun_reproduces_committed_manifest(committed):
    fresh, _, _ = extract.extract(SRC)
    fresh.pop("extracted_on")
    expected = dict(committed)
    expected.pop("extracted_on")
    assert fresh == expected
