# ADR-002 — KVKK Hesap Silme ve Veri Anonimleştirme Stratejisi

**Tarih:** 2026-07-06  
**Durum:** Kabul Edildi  
**Karar Veren:** Proje Sahibi  
**Oturum:** Meeting-007 (açık soru kapandı)  
**Etkilenen Belge:** `docs/architecture/database-design.md`

---

## Bağlam

Meeting-007'de veritabanı tasarımında `is_active = false` ile pasifleştirme yöntemi önerilmişti. Kişisel verilerin fiziksel olarak veritabanında kalması KVKK madde 7 ve madde 11 kapsamında kullanıcının "silinme" ve "anonim hale getirme" haklarını tam olarak karşılamayabilir.

---

## Değerlendirilen Seçenekler

### Seçenek A — Yalnızca `is_active = false`

- ✅ Basit implementasyon.
- ❌ Kişisel veriler veritabanında tutulmaya devam eder.
- ❌ KVKK madde 7 kapsamında "silme" yükümlülüğünü karşılamaz.
- ❌ Kullanıcı verisi üçüncü taraf erişimi veya sızıntısında risk oluşturur.

### Seçenek B — 30 Günlük Bekleme + Anonimleştirme

- ✅ KVKK ve GDPR uyumlu.
- ✅ Kullanıcıya geri alma süresi tanınır (iyi kullanıcı deneyimi).
- ✅ Finansal kayıtlar mevzuat gerektirdiği ölçüde korunabilir.
- ✅ Tarihsel istatistik bütünlüğü anonimleştirme ile korunur.
- ❌ Implementasyon daha karmaşık (zamanlanmış görev, state makinesi).

---

## Alınan Karar

**Seçenek B — 30 Günlük Bekleme + Anonimleştirme** uygulanacaktır.

---

## Silme Akışı

```
Kullanıcı hesap silme talebi
        ↓
User.deletion_requested_at = NOW()
User.status = 'pending_deletion'
        ↓
    [30 gün bekle]
        ↓
Kullanıcı geri aldı mı?
    Evet → User.status = 'active', deletion_requested_at = NULL
    Hayır → Anonimleştirme işlemi başlat
        ↓
Kişisel veriler anonimleştirilir:
  - email → "deleted_{uuid}@anonymized.studyos"
  - first_name, last_name → "Silinmiş Kullanıcı"
  - avatar_url → NULL
  - hashed_password → geçersiz hash
  - fcm_token → NULL
        ↓
User.status = 'anonymized'
User.anonymized_at = NOW()
        ↓
Finansal kayıtlar (Subscription, ödeme referansları):
  Yasal saklama süresi boyunca korunur,
  kişisel veri alanları anonimleştirilir.
```

---

## Veritabanı Değişiklikleri

`User` tablosuna eklenmesi gereken alanlar:

| Alan | Tür | Açıklama |
|------|-----|---------|
| `status` | Enum | `active`, `inactive`, `pending_deletion`, `anonymized` |
| `deletion_requested_at` | DateTime (nullable) | Silme talebi tarihi |
| `anonymized_at` | DateTime (nullable) | Anonimleştirme tarihi |

> `is_active` alanı kaldırılır; yerine `status` Enum alanı kullanılır.

---

## Sonuçlar

**Kabul Edilen Trade-off'lar:**
- Anonimleştirme işlemi bir arka plan görevi (background task) gerektirir. MVP'de zamanlanmış görev basit bir FastAPI startup event veya harici bir cron job ile yönetilir.
- Celery entegrasyonu ölçek aşamasına bırakılır.

**Mimari Etki:**
- `User` modeli güncellenir (is_active → status Enum).
- `AccountDeletionService` servisi oluşturulur.
- `/api/v1/users/me/delete-account` endpoint'i eklenir.
- KVKK sayfasında silme hakkı ve süreci açıklanır.
