# Sprint 19 — Knowledge Layer & Source Intelligence (LOS §12)

**Durum:** ✅ Uygulama tamam (smoke / QA)  
**Tür:** Feature Sprint (Knowledge Layer)  
**Tarih:** 2026-07-22  
**Önkoşul:** Sprint 1–18 ✅

---

## Sprint Amacı

**NotebookLM eklemek değil.**  
**StudyOS’un bilgi katmanını oluşturmak.**

NotebookLM bu katmanın **ilk provider** adaptörüdür (`KNOWLEDGE_PROVIDER=notebooklm`).  
UI’da marka yok — “Kaynak özeti”, “Yenile”, health etiketleri.

---

## Modül durumu

| ID | Konu | Durum |
|----|------|-------|
| M19.1 | Knowledge models + migration | ✅ |
| M19.2 | Resource pipeline (parse→chunk→embed→index) | ✅ |
| M19.3 | KnowledgeService / Notebook / Citation | ✅ |
| M19.4 | TopicContextBuilder + Knowledge | ✅ |
| M19.5 | Explain + citations | ✅ |
| M19.6 | Quiz knowledge-first + fallback | ✅ |
| M19.7 | Work Surface Kaynak özeti | ✅ |
| M19.8 | Source Intelligence | ✅ |
| M19.9 | Resource Health | ✅ |
| M19.10 | KnowledgeProvider (NotebookLM adaptör + Local) | ✅ |

---

## Mimari

```text
StudyResource → KnowledgeSource → Chunk/Embedding → Notebook
                                              ↓
                         TopicContextBuilder.knowledge
                                              ↓
                              Explain / Quiz (+ Citation)
```

Provider soyutlaması: `app/providers/knowledge/`  
- `NotebookLMKnowledgeProvider` — varsayılan yüzey (şimdilik Local RAG sarmalayıcı; API gelince yalnız bu sınıf değişir)  
- `LocalKnowledgeProvider` — harici API’siz chunk + hash embed + retrieve

---

## API (`/knowledge`)

| Method | Path |
|--------|------|
| POST | `/knowledge/resources/{id}/index` |
| POST | `/knowledge/notebook/reindex` |
| GET | `/knowledge/topics/{subject}/{topic}/notebook` |
| GET | `/knowledge/notebook/{id}` |
| GET | `/knowledge/notebook/{id}/citations` |

Alembic: `s19_knowledge_layer`

---

## Yapılmayanlar (bilinçli)

- Decision / Confidence / Living Plan değişikliği
- Gerçek NotebookLM HTTP API (adaptör hazır; Local üzerinde)
- Sosyal / Premium / Leaderboard

---

## Başarı Kriterleri

1. Resource → Knowledge Layer bağlanır (`index` / `reindex`)
2. Explain kaynak varsa citation döner
3. Quiz mümkünse kaynaktan üretir; yoksa fallback
4. Work Surface “Kaynak özeti” gösterir
5. Provider değişince domain servisleri değişmez
6. Source Intelligence + Health Work Surface’te görünür
7. LOS bozulmaz
