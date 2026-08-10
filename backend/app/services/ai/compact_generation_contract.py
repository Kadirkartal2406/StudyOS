"""Compact Generation Contract — Phase4B soft guidance for prompts (not hard gates).

Reads Phase4B calibration JSONs only. Does NOT write exam_measurement_model thresholds.
Does NOT invent Phase3B / dirty P10 values.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

CONTRACT_VERSION = "cgc_v1_phase4b"

# repo root: backend/app/services/ai -> parents[4] = StudyOS
_REPO_ROOT = Path(__file__).resolve().parents[4]
_PHASE4B_ROOT = (
    _REPO_ROOT / "data" / "analysis" / "measurement_validation" / "phase4b_recalibration"
)


def family_of(exam_unit: str) -> str:
    if exam_unit.startswith("yks_"):
        return "yks"
    if exam_unit.startswith("yokdil_"):
        return "yokdil"
    return exam_unit.split("_")[0]


def resolve_measurement_unit(exam: str | None, subject_code: str | None = None) -> str | None:
    """Map GenerateContext.exam (+ subject) → Phase4B exam_unit key."""
    e = (exam or "").strip().lower()
    s = (subject_code or "").strip().lower()
    if not e:
        return None

    if e in {
        "ales_sayisal",
        "ales_sozel",
        "dgs_sayisal",
        "dgs_sozel",
        "kpss_lisans",
        "kpss_onlisans",
        "kpss_ortaogretim",
        "lgs_sayisal",
        "lgs_sozel",
        "yds",
        "yks_ayt_ea",
        "yks_ayt_sayisal",
        "yks_ayt_sozel",
        "yks_tyt",
        "yks_ydt_ingilizce",
        "yokdil_fen",
        "yokdil_saglik",
        "yokdil_sosyal",
    }:
        return e

    if e in {"tyt", "yks"} or e.startswith("tyt"):
        return "yks_tyt"
    # Explicit AYT branch codes first — never collapse bare "ayt" to sayisal.
    if e in {"ayt_sayisal"} or e.startswith("ayt_say"):
        return "yks_ayt_sayisal"
    if e in {"ayt_ea"}:
        return "yks_ayt_ea"
    if e in {"ayt_sozel"}:
        return "yks_ayt_sozel"
    if e == "ayt" or e.startswith("ayt"):
        if any(x in s for x in ("matematik", "geometri", "fizik", "kimya", "biyoloji", "fen")):
            return "yks_ayt_sayisal"
        # EA pack subjects (edebiyat / tarih_1 / cografya_1)
        if any(
            x in s
            for x in ("edebiyat", "tarih_1", "cografya_1", "psikoloji", "sosyoloji", "mantik")
        ):
            return "yks_ayt_ea"
        if any(x in s for x in ("tarih", "cografya", "felsefe", "din", "sozel")):
            return "yks_ayt_sozel"
        return "yks_ayt_ea"
    if e.startswith("ydt") or e == "ydt_ingilizce":
        return "yks_ydt_ingilizce"
    if e.startswith("kpss"):
        if "onlisans" in e:
            return "kpss_onlisans"
        if "orta" in e:
            return "kpss_ortaogretim"
        return "kpss_lisans"
    if e.startswith("lgs"):
        if "sozel" in e or any(x in s for x in ("turkce", "inkilap", "din", "yabanci")):
            return "lgs_sozel"
        return "lgs_sayisal"
    if e.startswith("yds"):
        return "yds"
    if e.startswith("ales"):
        return "ales_sayisal" if ("sozel" not in e) else "ales_sozel"
    if e.startswith("dgs"):
        return "dgs_sayisal" if ("sozel" not in e) else "dgs_sozel"
    if e.startswith("yokdil"):
        if "saglik" in e:
            return "yokdil_saglik"
        if "sosyal" in e:
            return "yokdil_sosyal"
        return "yokdil_fen"
    return None


@dataclass
class VisualInterfaceStub:
    status: str  # required | optional | forbidden
    visual_type: str | None = None
    visual_spec: Any | None = None  # generator not implemented
    note: str = "visual_generator_not_bound"


@dataclass
class CompactGenerationContract:
    contract_version: str
    exam_unit: str
    family: str
    readiness: str
    subject_code: str | None = None
    topic_code: str | None = None
    do_not_enforce: bool = False
    soft_stem_band: dict[str, Any] | None = None
    visual: VisualInterfaceStub | None = None
    calculation_burden_hint: str | None = None
    scenario_multi_condition_hint: str | None = None
    archetype_hint: str | None = None
    selected_features: list[str] = field(default_factory=list)
    calibration_ref: str | None = None
    uncertainty_flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        return d

    def to_prompt_block(self) -> str:
        """Short natural-language soft constraints for LLM prompts."""
        if self.do_not_enforce:
            return (
                "MEASUREMENT SOFT CONTRACT (advisory only; do NOT force):\n"
                f"- exam_unit={self.exam_unit} readiness={self.readiness}\n"
                "- Insufficient evidence / do_not_enforce: prefer natural ÖSYM style; "
                "do not invent statistical cutoffs.\n"
                "- Visual generator is NOT available; do not fabricate figures.\n"
            )

        lines = [
            "MEASUREMENT SOFT CONTRACT (guidance only; not a hard reject gate):",
            f"- exam_unit={self.exam_unit}",
            f"- contract_version={self.contract_version}",
        ]
        if self.subject_code:
            lines.append(f"- subject={self.subject_code}")
        if self.topic_code:
            lines.append(f"- topic={self.topic_code}")
        if self.soft_stem_band:
            lo = self.soft_stem_band.get("low")
            hi = self.soft_stem_band.get("high")
            lines.append(
                f"- Prefer stem length roughly in [{lo}, {hi}] words "
                "(soft target from cleaned official distribution; not a hard cutoff)."
            )
        if self.visual:
            lines.append(
                f"- visual_policy={self.visual.status} "
                "(NO pixel/visual generator bound; if required, use textual reference "
                "only — do not invent a missing figure)."
            )
        if self.calculation_burden_hint:
            lines.append(f"- calculation_burden soft hint: {self.calculation_burden_hint}")
        if self.scenario_multi_condition_hint:
            lines.append(
                f"- scenario/multi-condition soft hint: {self.scenario_multi_condition_hint}"
            )
        if self.archetype_hint:
            lines.append(f"- archetype soft hint: {self.archetype_hint}")
        if self.uncertainty_flags:
            lines.append(
                "- uncertainty: " + ", ".join(self.uncertainty_flags)
            )
        lines.append(
            "- Do NOT reverse-engineer StudyOS percentiles or dump full statistical models."
        )
        return "\n".join(lines)


@lru_cache(maxsize=32)
def _load_calibration(exam_unit: str) -> dict[str, Any] | None:
    fam = family_of(exam_unit)
    path = _PHASE4B_ROOT / fam / f"{exam_unit}_calibration.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _stem_band(cal: dict[str, Any]) -> dict[str, Any] | None:
    thr = ((cal.get("selected_thresholds") or {}).get("stem_word_count") or {}).get(
        "threshold"
    ) or {}
    lo, hi = thr.get("low"), thr.get("high")
    if lo is None or hi is None:
        # fallback descriptive cleaned p10/p90 only if present on same feature
        desc = ((cal.get("selected_thresholds") or {}).get("stem_word_count") or {}).get(
            "descriptive"
        ) or {}
        lo, hi = desc.get("p10"), desc.get("p90")
    if lo is None or hi is None:
        return None
    return {
        "low": lo,
        "high": hi,
        "source": "phase4b_cleaned",
        "enforce": False,
    }


def _visual_stub(cal: dict[str, Any]) -> VisualInterfaceStub:
    td = cal.get("target_distribution") or {}
    vis = td.get("visual_usage") or {}
    rate = vis.get("rate")
    if rate is None:
        return VisualInterfaceStub(status="optional", note="visual_rate_unknown_generator_not_bound")
    if rate >= 0.35:
        return VisualInterfaceStub(status="optional", visual_type=None)
    if rate <= 0.05:
        return VisualInterfaceStub(status="forbidden", visual_type=None)
    return VisualInterfaceStub(status="optional", visual_type=None)


def _calc_hint(cal: dict[str, Any]) -> str | None:
    feat = (cal.get("selected_thresholds") or {}).get("calculation_burden") or {}
    if feat.get("status") != "calibrated":
        return None
    return "keep calculation load typical for this exam unit (soft)"


def _scenario_hint(cal: dict[str, Any]) -> str | None:
    st = cal.get("selected_thresholds") or {}
    if (st.get("scenario_density") or {}).get("status") == "calibrated":
        return "scenario density soft-match when natural"
    if (st.get("multi_condition_structure") or {}).get("status") == "calibrated":
        return "multi-condition structure soft-match when natural"
    return None


def _archetype_hint(cal: dict[str, Any]) -> str | None:
    td = (cal.get("target_distribution") or {}).get("archetype") or {}
    dist = td.get("distribution") or {}
    if not dist:
        return None
    top = sorted(dist.items(), key=lambda kv: kv[1], reverse=True)[:3]
    return "prefer common archetypes: " + ", ".join(f"{k}≈{v:.0%}" for k, v in top)


def build_compact_generation_contract(
    *,
    exam: str | None,
    subject_code: str | None = None,
    topic_code: str | None = None,
) -> CompactGenerationContract | None:
    unit = resolve_measurement_unit(exam, subject_code)
    if not unit:
        return None
    cal = _load_calibration(unit)
    if not cal:
        return CompactGenerationContract(
            contract_version=CONTRACT_VERSION,
            exam_unit=unit,
            family=family_of(unit),
            readiness="MISSING_CALIBRATION",
            subject_code=subject_code,
            topic_code=topic_code,
            do_not_enforce=True,
            uncertainty_flags=["calibration_file_missing"],
            calibration_ref=None,
        )

    readiness = str(cal.get("readiness") or "UNKNOWN")
    do_not_enforce = readiness == "INSUFFICIENT_EVIDENCE" or unit.startswith("yokdil_")
    uncertainty: list[str] = []
    if readiness == "NEEDS_REVIEW":
        uncertainty.append("readiness_needs_review_weak_soft")
        do_not_enforce = True  # prefer UNSCORED path in scorer
    if readiness == "INSUFFICIENT_EVIDENCE":
        uncertainty.append("insufficient_evidence")

    selected = [
        f.get("feature")
        for f in (cal.get("selected_features") or [])
        if isinstance(f, dict) and f.get("feature")
    ]

    return CompactGenerationContract(
        contract_version=CONTRACT_VERSION,
        exam_unit=unit,
        family=str(cal.get("family") or family_of(unit)),
        readiness=readiness,
        subject_code=subject_code,
        topic_code=topic_code,
        do_not_enforce=do_not_enforce,
        soft_stem_band=None if do_not_enforce else _stem_band(cal),
        visual=_visual_stub(cal),
        calculation_burden_hint=None if do_not_enforce else _calc_hint(cal),
        scenario_multi_condition_hint=None if do_not_enforce else _scenario_hint(cal),
        archetype_hint=None if do_not_enforce else _archetype_hint(cal),
        selected_features=[str(x) for x in selected if x],
        calibration_ref=f"phase4b_recalibration/{family_of(unit)}/{unit}_calibration.json",
        uncertainty_flags=uncertainty,
    )
