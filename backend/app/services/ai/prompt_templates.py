"""
StudyOS — Versiyonlu System Prompt şablonları
Sprint-2.2 — String birleştirme yok; parçalar + format_map.
"""

from typing import Any

from app.core.constants import AI_SYSTEM_PROMPT_VERSION

# Parça anahtarları — PromptBuilder format_map ile doldurur
SYSTEM_PROMPT_V1_PARTS: tuple[str, ...] = (
    "Sen StudyOS AI Çalışma Koçusun.",
    "Kullanıcının çalışma geçmişi, hedefleri ve istatistikleri bağlamındasın.",
    "Kısa, net ve motive edici Türkçe yanıt ver.",
    "Gerçekçi ol; uydurma veri üretme.",
    "Planı asla doğrudan değiştirme; yalnızca öneri sun.",
    "Kullanıcı planda değişiklik isterse yanıtının sonunda şu bloğu ekle: "
    "```plan_proposal\n{{\"action\":\"regenerate\",\"reason\":\"...\"}}\n``` "
    "ve metinde onay beklediğini söyle.",
    "Bağlam sürümü: {context_version}. Prompt sürümü: {prompt_version}.",
    "Aktif hedef özeti: {goals_summary}.",
    "İçgörü özeti: {insights_summary}.",
    "İstatistik özeti: {stats_summary}.",
    "Uzun dönem bellek özeti: {memory_summary}.",
    "Sohbet özeti: {conversation_summary}.",
)

SYSTEM_PROMPT_REGISTRY: dict[str, tuple[str, ...]] = {
    "v1": SYSTEM_PROMPT_V1_PARTS,
}


def get_system_prompt_parts(version: str | None = None) -> tuple[str, ...]:
    ver = version or AI_SYSTEM_PROMPT_VERSION
    return SYSTEM_PROMPT_REGISTRY.get(ver, SYSTEM_PROMPT_V1_PARTS)


def render_system_prompt(parts: tuple[str, ...], values: dict[str, Any]) -> str:
    """Her parçayı format_map ile doldurup sabit ayırıcıyla birleştir."""
    rendered = [part.format_map(values) for part in parts]
    return " ".join(rendered)
