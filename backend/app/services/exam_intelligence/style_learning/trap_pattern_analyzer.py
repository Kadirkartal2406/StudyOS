"""Trap / distractor pattern catalogs per exam & topic (no stems)."""

from __future__ import annotations

from typing import Any


_EXAM_TRAPS: dict[str, list[str]] = {
    "kpss": [
        "yakin_anlam",
        "abarti",
        "eksik_bilgi",
        "ters_ifade",
        "kapsam_disi",
    ],
    "ales": [
        "yanlis_cikarim",
        "fazla_bilgi",
        "eksik_oncul",
        "matematiksel_hata",
        "ters_iliski",
    ],
    "tyt": [
        "islem_hatasi",
        "birim_hatasi",
        "grafik_okuma",
        "eksik_veri",
        "yaklasik_deger",
    ],
    "ayt": [
        "islem_hatasi",
        "formül_karistirma",
        "sinir_kosulu",
        "yanlis_cikarim",
    ],
    "ydt": ["yakin_anlam", "ters_ifade", "baglam_disi", "kelime_tuzagi"],
    "yds": ["yakin_anlam", "ters_ifade", "baglam_disi", "kelime_tuzagi"],
    "yokdil": ["alan_kelime_tuzagi", "yakin_anlam", "yanlis_cikarim"],
    "dgs": ["islem_hatasi", "yanlis_cikarim", "eksik_oncul"],
    "lgs": ["islem_hatasi", "dikkat_hatasi", "grafik_okuma"],
    "ags": ["yakin_anlam", "eksik_bilgi", "islem_hatasi"],
}

_TOPIC_TRAPS: dict[str, list[str]] = {
    "paragraf": ["yakin_anlam", "abarti", "ters_ifade", "eksik_bilgi"],
    "problemler": ["islem_hatasi", "birim_hatasi", "eksik_veri"],
    "ucgenler": ["sekil_yanilgisi", "ozellik_karistirma"],
    "hareket": ["birim_hatasi", "yon_hatasi", "formül_karistirma"],
    "reading": ["yakin_anlam", "baglam_disi", "kelime_tuzagi"],
    "mol": ["islem_hatasi", "oran_hatasi"],
}


def analyze_trap_patterns(
    *,
    exam_code: str,
    topic_slug: str | None = None,
    skill_type: str | None = None,
    distractor_style: str | None = None,
) -> dict[str, Any]:
    exam = (exam_code or "").lower()
    topic = (topic_slug or "").lower()
    traps: list[str] = []
    traps.extend(_EXAM_TRAPS.get(exam, ["genel_celdirici"]))
    traps.extend(_TOPIC_TRAPS.get(topic, []))

    if skill_type == "inference":
        traps.extend(["yanlis_cikarim", "abarti"])
    if skill_type == "problem_solving":
        traps.extend(["islem_hatasi", "eksik_veri"])

    seen: set[str] = set()
    ordered: list[str] = []
    for t in traps:
        if t not in seen:
            seen.add(t)
            ordered.append(t)

    primary = ordered[:4]
    return {
        "primary": primary,
        "patterns": ordered,
        "distractor_style": distractor_style or "plausible_heuristic",
        "trap_density": "high" if len(primary) >= 4 else "medium",
    }
