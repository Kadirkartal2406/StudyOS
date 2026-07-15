# Meeting-006 — Teknoloji Kararları

**Tarih:** 2026-07-06  
**Katılımcı AI:** Claude Sonnet 4.6 (Thinking)  
**Oturum Hedefi:** StudyOS MVP ve sonrasına yönelik teknoloji yığınını tanımlamak ve karşılaştırmalı analiz sunmak.  
**Durum:** Tamamlandı — Proje Sahibi Onayladı

---

## Yapılanlar

- `docs/project/ai-rules.md` okundu ve tüm kurallar uygulandı.
- `docs/planning/feature-matrix.md` okundu; MVP kapsamı ve özellik öncelikleri belirlendi.
- `docs/requirements/student-platform-requirements.md` okundu.
- `docs/requirements/institution-platform-requirements.md` okundu.
- 17 teknoloji kategorisi için karşılaştırmalı analiz yapıldı.
- Her kategori için avantaj / dezavantaj ve gerekçeli öneri hazırlandı.
- Maliyet analizi (MVP, 10K, 100K kullanıcı) tamamlandı.
- Risk analizi her seçilen teknoloji için hazırlandı.
- `docs/architecture/technology-decisions.md` oluşturuldu.

---

## Alınan Kararlar

> Proje sahibi aşağıdaki teknolojiyi onayladı. Belge güncellendi (v1.1).

| Kategori | Onaylanan Teknoloji | Not |
|----------|--------------------|----- |
| Mobil Framework | **Flutter** | Android + iOS |
| Backend Framework | **FastAPI** | Python, async |
| Veritabanı | **PostgreSQL** | — |
| ORM | **SQLAlchemy 2.0 + Alembic** | — |
| Authentication | **JWT** (python-jose + passlib) | Firebase Auth reddedildi |
| Bulut Depolama | **AWS S3** | Geliştirmede: **MinIO** |
| Push Notifications | **Firebase Cloud Messaging** | — |
| AI Entegrasyonu | **Gemini 2.5 Flash** | İleride: OpenAI |
| State Management | **Riverpod** | riverpod_generator |
| Yerel Veritabanı | **drift** (SQLite) | Isar reddedildi |
| API Stili | **REST** | /api/v1/ öneki |
| Deploy | **Railway** | — |
| Monitoring | **Sentry** | Backend + Mobil (tek platform) |
| Analytics | **Firebase Analytics** | — |
| CI/CD | **GitHub Actions** | — |
| Testing | **pytest + flutter_test + Playwright** | Her katman için ekosistem standardı |

---

## Oluşturulan / Güncellenen Dosyalar

| Dosya | İşlem |
|-------|-------|
| `docs/architecture/technology-decisions.md` | Yeni oluşturuldu |
| `docs/meeting-notes/Meeting-006.md` | Yeni oluşturuldu |

---

## Açık Sorular

Tüm kararlar proje sahibi tarafından netliğe kavuşturuldu. Açık soru kalmadı.

**Önceki sorular ve sonuçları:**

| Soru | Sonuç |
|------|-------|
| Firebase Auth mı, JWT mi? | **JWT** — vendor bağımsızlığı tercih edildi |
| Supabase Storage mi, AWS S3 mi? | **AWS S3** — geliştirmede MinIO |
| AI tek provider mı, hibrit mi? | **Gemini 2.5 Flash** tek provider; ileride OpenAI |
| Isar mı, drift mi? | **drift** — olgunluk ve topluluk tercih edildi |

---

## Bir Sonraki Adım

**Meeting-007 önerisi:** Mimari diyagramlar — Backend servis mimarisi, veritabanı şeması ve API endpoint yapısının taslağını oluşturmak.

**Önce yapılması gereken:** Bu belgede yer alan teknoloji kararlarının proje sahibi tarafından onaylanması veya revize edilmesi.
