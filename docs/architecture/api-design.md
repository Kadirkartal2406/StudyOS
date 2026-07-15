# StudyOS — API Tasarımı

**Belge Durumu:** Aktif  
**Sürüm:** 1.0  
**Oluşturuldu:** 2026-07-06 — Meeting-007  
**Dil:** Türkçe  
**Kaynak:** `docs/architecture/software-architecture.md`, `docs/architecture/database-design.md`

> Bu belge API yapısını ve prensiplerini tanımlar.  
> Endpoint implementasyonu içermez; yalnızca sözleşme (contract) tasarımını kapsar.

---

## 1. REST Prensipleri

StudyOS API'si aşağıdaki REST prensiplerini uygular:

### 1.1 Temel Kurallar

| Prensip | Uygulama |
|---------|---------|
| **Kaynak odaklı URL** | `/students`, `/study-plans` — fiil değil isim |
| **HTTP metodlarla eylem** | GET okuma, POST oluşturma, PUT tam güncelleme, PATCH kısmi güncelleme, DELETE silme |
| **Durumsuz (Stateless)** | Her istek kendi içinde tam; sunucu oturum tutmaz |
| **Versiyonlama** | Tüm endpoint'ler `/api/v1/` öneki taşır |
| **Tutarlı yanıt formatı** | Başarı ve hata yanıtları aynı zarfı (envelope) kullanır |
| **HTTP durum kodları** | Anlamlı durum kodu her yanıtta bulunur |

### 1.2 URL Yapısı

```
https://api.studyos.com/api/v1/{kaynak}/{id}/{alt-kaynak}

Örnekler:
  GET  /api/v1/students                      → Tüm öğrenciler
  GET  /api/v1/students/{id}                 → Tek öğrenci
  GET  /api/v1/students/{id}/study-plans     → Öğrencinin planları
  POST /api/v1/institutions/{id}/classes     → Kuruma sınıf ekle
```

### 1.3 Standart Yanıt Zarfı (Response Envelope)

**Başarı yanıtı:**
```json
{
  "success": true,
  "data": { ... },
  "message": "İşlem başarılı"
}
```

**Sayfalı liste yanıtı:**
```json
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 150,
    "total_pages": 8
  }
}
```

**Hata yanıtı:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Geçersiz e-posta formatı",
    "details": { "field": "email", "issue": "invalid_format" }
  }
}
```

### 1.4 HTTP Durum Kodları

| Kod | Anlam | Kullanım |
|-----|-------|---------|
| 200 | OK | Başarılı GET, PUT, PATCH |
| 201 | Created | Başarılı POST (kaynak oluşturuldu) |
| 204 | No Content | Başarılı DELETE |
| 400 | Bad Request | Doğrulama hatası |
| 401 | Unauthorized | Token yok veya geçersiz |
| 403 | Forbidden | Yetki yetersiz (token geçerli ama rol uyumsuz) |
| 404 | Not Found | Kaynak bulunamadı |
| 409 | Conflict | Kayıt zaten var (duplicate email vb.) |
| 422 | Unprocessable Entity | İş kuralı ihlali |
| 429 | Too Many Requests | Rate limit aşıldı |
| 500 | Internal Server Error | Sunucu hatası |

### 1.5 Sorgu Parametreleri (Query Parameters)

| Parametre | Örnek | Açıklama |
|-----------|-------|---------|
| `page` | `?page=2` | Sayfa numarası |
| `page_size` | `?page_size=20` | Sayfa başı kayıt (max: 100) |
| `sort` | `?sort=created_at` | Sıralama alanı |
| `order` | `?order=desc` | `asc` veya `desc` |
| `search` | `?search=matematik` | Metin arama |
| `date_from` | `?date_from=2026-01-01` | Tarih filtresi başlangıcı |
| `date_to` | `?date_to=2026-12-31` | Tarih filtresi sonu |

---

## 2. Endpoint Grupları

### 2.1 `/api/v1/auth` — Kimlik Doğrulama

Tüm endpoint'ler herkese açıktır (auth gerektirmez).

| Metod | Endpoint | Açıklama | İstek Gövdesi |
|-------|----------|---------|--------------|
| `POST` | `/auth/register` | Yeni kullanıcı kaydı | `{email, password, first_name, last_name, role}` |
| `POST` | `/auth/login` | Giriş — token çifti döner | `{email, password}` |
| `POST` | `/auth/refresh` | Access token yenileme | `{refresh_token}` |
| `POST` | `/auth/logout` | Refresh token iptal et | `{refresh_token}` |
| `POST` | `/auth/forgot-password` | Şifre sıfırlama e-postası gönder | `{email}` |
| `POST` | `/auth/reset-password` | Yeni şifre belirle | `{token, new_password}` |
| `POST` | `/auth/verify-email` | E-posta doğrulama | `{token}` |

---

### 2.2 `/api/v1/users` — Kullanıcı Yönetimi

| Metod | Endpoint | Açıklama | Yetki |
|-------|----------|---------|-------|
| `GET` | `/users/me` | Giriş yapan kullanıcı bilgisi | Tüm roller |
| `PATCH` | `/users/me` | Profil güncelleme | Tüm roller |
| `PATCH` | `/users/me/password` | Şifre değiştirme | Tüm roller |
| `GET` | `/users/{id}` | Kullanıcı detayı | system_admin |
| `GET` | `/users` | Kullanıcı listesi | system_admin |
| `DELETE` | `/users/{id}` | Kullanıcı devre dışı | system_admin |

---

### 2.3 `/api/v1/students` — Öğrenci İşlemleri

| Metod | Endpoint | Açıklama | Yetki |
|-------|----------|---------|-------|
| `GET` | `/students/me` | Kendi öğrenci profili | student |
| `PATCH` | `/students/me` | Profil güncelleme | student |
| `PATCH` | `/students/me/fcm-token` | FCM token güncelleme | student |
| `GET` | `/students/{id}` | Öğrenci profil detayı | teacher, institution_admin |
| `GET` | `/students/{id}/statistics` | Öğrenci istatistik özeti | teacher, institution_admin, student (kendi) |
| `GET` | `/students/{id}/exam-results` | Sınav sonuçları | teacher, institution_admin, student (kendi) |

---

### 2.4 `/api/v1/institutions` — Kurum Yönetimi

| Metod | Endpoint | Açıklama | Yetki |
|-------|----------|---------|-------|
| `POST` | `/institutions` | Yeni kurum kaydı | system_admin |
| `GET` | `/institutions/{id}` | Kurum detayı | institution_admin, system_admin |
| `PATCH` | `/institutions/{id}` | Kurum bilgisi güncelleme | institution_admin |
| `GET` | `/institutions/{id}/branches` | Şube listesi | institution_admin |
| `POST` | `/institutions/{id}/branches` | Şube ekleme | institution_admin |
| `GET` | `/institutions/{id}/teachers` | Öğretmen listesi | institution_admin |
| `POST` | `/institutions/{id}/teachers/invite` | Öğretmen davet et | institution_admin |
| `GET` | `/institutions/{id}/classes` | Sınıf listesi | institution_admin, teacher |
| `POST` | `/institutions/{id}/classes` | Sınıf oluştur | institution_admin |
| `GET` | `/institutions/{id}/students` | Kurum öğrenci listesi | institution_admin |
| `POST` | `/institutions/{id}/students/invite` | Öğrenci davet et | institution_admin, teacher |
| `GET` | `/institutions/{id}/statistics` | Kurum istatistikleri | institution_admin |

---

### 2.5 `/api/v1/classes` — Sınıf İşlemleri

| Metod | Endpoint | Açıklama | Yetki |
|-------|----------|---------|-------|
| `GET` | `/classes/{id}` | Sınıf detayı | teacher, institution_admin |
| `PATCH` | `/classes/{id}` | Sınıf güncelleme | institution_admin |
| `DELETE` | `/classes/{id}` | Sınıf devre dışı bırakma | institution_admin |
| `GET` | `/classes/{id}/students` | Sınıf öğrenci listesi | teacher, institution_admin |
| `POST` | `/classes/{id}/students/{student_id}` | Öğrenci sınıfa ekle | institution_admin |
| `DELETE` | `/classes/{id}/students/{student_id}` | Öğrenciyi sınıftan çıkar | institution_admin |
| `GET` | `/classes/{id}/statistics` | Sınıf istatistikleri | teacher, institution_admin |
| `GET` | `/classes/{id}/attendance` | Yoklama kayıtları | teacher, institution_admin |
| `POST` | `/classes/{id}/attendance` | Yoklama kaydet | teacher |

---

### 2.6 `/api/v1/study-plans` — Çalışma Planları

| Metod | Endpoint | Açıklama | Yetki |
|-------|----------|---------|-------|
| `GET` | `/study-plans/today` | Bugünün planı | student |
| `GET` | `/study-plans` | Tarih aralıklı plan listesi | student |
| `POST` | `/study-plans` | Yeni plan oluştur | student |
| `GET` | `/study-plans/{id}` | Plan detayı | student |
| `PATCH` | `/study-plans/{id}` | Plan güncelle | student |
| `DELETE` | `/study-plans/{id}` | Plan sil | student |
| `POST` | `/study-plans/{id}/items` | Plan kalemine konu ekle | student |
| `PATCH` | `/study-plans/{id}/items/{item_id}` | Kalem güncelle (süre, tamamlandı) | student |
| `DELETE` | `/study-plans/{id}/items/{item_id}` | Kalem sil | student |

---

### 2.7 `/api/v1/sessions` — Çalışma Oturumları (Pomodoro)

| Metod | Endpoint | Açıklama | Yetki |
|-------|----------|---------|-------|
| `POST` | `/sessions/start` | Oturum başlat | student |
| `PATCH` | `/sessions/{id}/end` | Oturum bitir | student |
| `GET` | `/sessions` | Oturum geçmişi | student |

---

### 2.8 `/api/v1/subjects` — Ders/Konu Listesi

| Metod | Endpoint | Açıklama | Yetki |
|-------|----------|---------|-------|
| `GET` | `/subjects` | Tüm dersler (exam_type filtresi ile) | Tüm roller |
| `GET` | `/subjects/{id}` | Ders detayı | Tüm roller |
| `POST` | `/subjects` | Yeni ders ekle | system_admin |
| `PATCH` | `/subjects/{id}` | Ders güncelle | system_admin |

---

### 2.9 `/api/v1/statistics` — İstatistikler

| Metod | Endpoint | Açıklama | Yetki |
|-------|----------|---------|-------|
| `GET` | `/statistics/me/daily` | Günlük kişisel istatistik | student |
| `GET` | `/statistics/me/weekly` | Haftalık özet | student |
| `GET` | `/statistics/me/monthly` | Aylık özet | student |
| `GET` | `/statistics/me/subjects` | Konu bazlı başarı | student |
| `POST` | `/statistics/me/questions` | Soru girişi kaydet | student |
| `GET` | `/statistics/students/{id}` | Öğrenci istatistikleri | teacher, institution_admin |

---

### 2.10 `/api/v1/exams` — Sınavlar

| Metod | Endpoint | Açıklama | Yetki |
|-------|----------|---------|-------|
| `GET` | `/exams` | Sınav listesi (kurum veya öğrenci) | student, teacher, institution_admin |
| `POST` | `/exams` | Sınav oluştur | teacher, institution_admin |
| `GET` | `/exams/{id}` | Sınav detayı | ilgili roller |
| `PATCH` | `/exams/{id}` | Sınav güncelle | teacher, institution_admin |
| `DELETE` | `/exams/{id}` | Sınav sil | institution_admin |
| `POST` | `/exams/{id}/results` | Sınav sonucu gir | student, teacher |
| `GET` | `/exams/{id}/results` | Sınav sonuçları | teacher, institution_admin |
| `GET` | `/exams/{id}/analysis` | Konu bazlı analiz | teacher, institution_admin |

---

### 2.11 `/api/v1/assignments` — Ödevler

| Metod | Endpoint | Açıklama | Yetki |
|-------|----------|---------|-------|
| `GET` | `/assignments` | Ödev listesi | student, teacher |
| `POST` | `/assignments` | Ödev oluştur | teacher |
| `GET` | `/assignments/{id}` | Ödev detayı | ilgili roller |
| `PATCH` | `/assignments/{id}` | Ödev güncelle | teacher |
| `DELETE` | `/assignments/{id}` | Ödev sil | teacher |
| `POST` | `/assignments/{id}/submit` | Ödev teslim et | student |
| `GET` | `/assignments/{id}/submissions` | Teslim listesi | teacher |

---

### 2.12 `/api/v1/notifications` — Bildirimler

| Metod | Endpoint | Açıklama | Yetki |
|-------|----------|---------|-------|
| `GET` | `/notifications` | Bildirim listesi | Tüm roller |
| `GET` | `/notifications/unread-count` | Okunmamış sayısı | Tüm roller |
| `PATCH` | `/notifications/{id}/read` | Okundu olarak işaretle | Tüm roller |
| `PATCH` | `/notifications/read-all` | Tümünü okundu yap | Tüm roller |
| `DELETE` | `/notifications/{id}` | Bildirimi sil | Tüm roller |
| `POST` | `/notifications/broadcast` | Toplu bildirim gönder | institution_admin, system_admin |

---

### 2.13 `/api/v1/files` — Dosya İşlemleri

| Metod | Endpoint | Açıklama | Yetki |
|-------|----------|---------|-------|
| `POST` | `/files/upload-url` | Presigned URL üret | Tüm roller |
| `POST` | `/files/confirm` | Yükleme tamamlandı bildir | Tüm roller |
| `DELETE` | `/files/{file_key}` | Dosya sil | Sahip kullanıcı, admin |

---

### 2.14 `/api/v1/ai` — Yapay Zeka İşlemleri

| Metod | Endpoint | Açıklama | Yetki |
|-------|----------|---------|-------|
| `POST` | `/ai/study-coach` | Çalışma koçu mesajı | student (premium) |
| `POST` | `/ai/generate-plan` | AI haftalık plan üret | student (premium) |
| `GET` | `/ai/usage` | AI kullanım istatistiği | student |

---

### 2.15 `/api/v1/subscriptions` — Abonelik

| Metod | Endpoint | Açıklama | Yetki |
|-------|----------|---------|-------|
| `GET` | `/subscriptions/me` | Aktif abonelik bilgisi | student |
| `POST` | `/subscriptions` | Abonelik başlat | student |
| `DELETE` | `/subscriptions/me` | Abonelik iptal et | student |

---

## 3. Yetki Matrisi Özeti

| Endpoint Grubu | student | teacher | institution_admin | system_admin |
|---------------|---------|---------|------------------|--------------|
| `/auth/*` | ✅ | ✅ | ✅ | ✅ |
| `/users/me` | ✅ | ✅ | ✅ | ✅ |
| `/students/me` | ✅ | — | — | — |
| `/students/{id}` | — | ✅ (kendi) | ✅ (kendi) | ✅ |
| `/institutions` | — | — | ✅ (kendi) | ✅ |
| `/classes` | — | ✅ (kendi) | ✅ (kendi) | ✅ |
| `/study-plans` | ✅ (kendi) | — | — | ✅ |
| `/sessions` | ✅ (kendi) | — | — | ✅ |
| `/subjects` | ✅ (okuma) | ✅ (okuma) | ✅ (okuma) | ✅ |
| `/statistics/me` | ✅ | — | — | — |
| `/statistics/students/{id}` | — | ✅ | ✅ | ✅ |
| `/exams` | ✅ (okuma) | ✅ | ✅ | ✅ |
| `/assignments` | ✅ (okuma/teslim) | ✅ | — | ✅ |
| `/notifications` | ✅ (kendi) | ✅ (kendi) | ✅ (kendi) | ✅ |
| `/files` | ✅ | ✅ | ✅ | ✅ |
| `/ai` | ✅ (premium) | — | — | ✅ |
| `/subscriptions/me` | ✅ | — | — | — |

---

## 4. Sayfalama ve Filtreleme Standartları

### Sayfalama

Tüm liste endpoint'leri sayfalamayı destekler. Varsayılan `page_size` değeri 20, maksimum 100'dür.

### Filtreleme Örnekleri

```
GET /api/v1/subjects?exam_type=yks                   → YKS dersleri
GET /api/v1/study-plans?date_from=2026-07-01&date_to=2026-07-31  → Temmuz planları
GET /api/v1/notifications?is_read=false              → Okunmamışlar
GET /api/v1/exams?class_id=uuid&is_published=true    → Yayında sınavlar
```

---

## 5. API Versiyonlama Stratejisi

- Mevcut versiyon: `/api/v1/`
- Kırıcı değişiklik gerektiren güncelleme: `/api/v2/` başlatılır.
- Eski versiyon minimum 6 ay aktif tutulur.
- Kullanıcılar `Deprecation` ve `Sunset` HTTP header'ları ile bilgilendirilir.

---

## Sürüm Geçmişi

| Sürüm | Tarih | Değişiklik |
|-------|-------|-----------|
| 1.0 | 2026-07-06 | İlk sürüm — Meeting-007 |
