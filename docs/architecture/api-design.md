# StudyOS — API Tasarımı

**Belge Durumu:** Aktif  
**Sürüm:** 1.7  
**Oluşturuldu:** 2026-07-06 — Meeting-007  
**Güncelleme Tarihi:** 2026-07-16 — Meeting-017 (questions CRUD + question statistics)  
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

**Sprint-1.4 (Meeting-012) itibarıyla implemente edildi.** Aşağıdaki endpoint listesi,
bu bölümde önceden tanımlı ancak implemente edilmemiş taslağın (`/study-plans/today`,
plan kalemi alt-kaynağı `/items`) yerine geçer — bkz. database-design.md §1.9
"[ONAY GEREKTİRİR]" notu ve Meeting-012.

| Metod | Endpoint | Açıklama | Yetki |
|-------|----------|---------|-------|
| `GET` | `/study-plans?study_date=YYYY-MM-DD` | Kullanıcının planlarını listeler (tarih filtresi opsiyonel, `order_index` sıralı) | student |
| `GET` | `/study-plans/{id}` | Plan detayı | student (kendi) |
| `POST` | `/study-plans` | Yeni plan oluştur | student |
| `PUT` | `/study-plans/{id}` | Plan güncelle (tüm alanlar; sıralama için `order_index` de gönderilir) | student (kendi) |
| `DELETE` | `/study-plans/{id}` | Plan sil (soft delete, `204`) | student (kendi) |
| `PATCH` | `/study-plans/{id}/start` | Planı `in_progress` durumuna geçirir | student (kendi) |
| `PATCH` | `/study-plans/{id}/complete` | Planı `completed` durumuna geçirir; `completed_question_count`/`completed_minutes` günceller | student (kendi) |
| `PATCH` | `/study-plans/{id}/skip` | Planı `skipped` durumuna geçirir | student (kendi) |
| `GET` | `/study-plans/{id}/resources` | Plana bağlı kaynaklar (Sprint-2.5) | student (kendi) |
| `POST` | `/study-plans/{id}/resources` | Plana kaynak ekle | student (kendi) |

### 2.6b `/api/v1/resources` — Öğrenme Kaynakları (Sprint-2.5)

Öğrenci kişisel kaynak kütüphanesi. Kurumsal Material (§1.16) değildir.

| Metod | Endpoint | Açıklama | Yetki |
|-------|----------|---------|-------|
| `GET` | `/resources` | Liste (`study_plan_id`, `status`, `resource_type` filtre) | student |
| `POST` | `/resources` | Kaynak oluştur | student |
| `GET` | `/resources/statistics` | Tür/tamamlanan/video süresi özeti | student |
| `GET` | `/resources/{id}` | Detay | student |
| `PATCH` | `/resources/{id}` | Güncelle (status, order_index, …) | student |
| `DELETE` | `/resources/{id}` | Hard delete | student |
| `POST` | `/resources/{id}/open` | `last_opened_at` + not_started→in_progress | student |

**Request `body` şeması (POST / PUT study-plans):**

```json
{
  "title": "Matematik Çalışması",
  "subject": "Matematik",
  "topic": "Türev",
  "target_question_count": 20,
  "estimated_minutes": 60,
  "planned_start_time": "09:00:00",
  "planned_end_time": "10:00:00",
  "study_date": "2026-07-16",
  "order_index": 0
}
```

`topic`, `planned_start_time`, `planned_end_time` ve `order_index` opsiyoneldir.
`planned_start_time`/`planned_end_time` birlikte verilmeli veya hiç verilmemelidir;
bitiş saati başlangıçtan büyük olmalıdır (aksi halde `422`). Aynı gün içinde saat
aralığı çakışan başka bir plan varsa istek `400 VALIDATION_ERROR` ile reddedilir.

**Request `body` şeması (PATCH .../complete, opsiyonel):**

```json
{
  "completed_question_count": 18,
  "completed_minutes": 45
}
```

Gönderilmezse hedef değerler (`target_question_count`/`estimated_minutes`) esas alınır.
`completed`/`skipped` durumundaki bir plan üzerinde `start`/`complete`/`skip` tekrar
çağrılırsa `409 CONFLICT` döner. Başka bir kullanıcının planına erişim `404` döner
(sahiplik bilgisi client'a sızdırılmaz).

---

### 2.7 `/api/v1/study-sessions` — Çalışma Oturumları (Pomodoro)

**Sprint-1.5 (Meeting-013) itibarıyla implemente edildi.** Önceki taslak `/sessions`
(start/{id}/end/list) yerine sprint talebindeki `/study-sessions/*` sözleşmesi esas alındı.

| Metod | Endpoint | Açıklama | Yetki |
|-------|----------|---------|-------|
| `POST` | `/study-sessions/start` | Oturum başlat (`201`) | student |
| `POST` | `/study-sessions/pause` | Aktif oturumu duraklat | student |
| `POST` | `/study-sessions/resume` | Duraklatılmış oturumu devam ettir | student |
| `POST` | `/study-sessions/finish` | Aktif oturumu tamamla; bağlı plana ilerleme yaz | student |
| `GET` | `/study-sessions/today` | Bugün başlayan oturumlar | student |
| `GET` | `/study-sessions/history` | Sayfalı geçmiş (`page`, `page_size`, `date_from`, `date_to`, `study_plan_id`, `status`, `q`) | student |
| `GET` | `/study-sessions/statistics` | İstatistik özeti (`date_from`, `date_to` opsiyonel) | student |
| `GET` | `/study-sessions/{id}` | Oturum detayı (plan_title / plan_subject ile) | student |

**History filtreleri (Sprint-1.7):** `status` = `running` \| `paused` \| `completed`.
`q` plan başlığında ILIKE arar (JOIN). Yanıtta `plan_title` / `plan_subject` alanları
dönebilir. start/pause/resume/finish Activity event üretir.

**Request `body` (POST /start):**

```json
{
  "planned_duration_minutes": 25,
  "break_duration_minutes": 5,
  "study_plan_id": null
}
```

`planned_duration_minutes` 1–240 arası zorunlu. `break_duration_minutes` 0–60 (varsayılan 0).
Aktif oturum varken yeni `start` → `409 CONFLICT`. Bilinmeyen/başkasının `study_plan_id` → `404`.
Terminal planda (`completed`/`skipped`) oturum başlatılamaz → `409`.

**Request `body` (POST /finish, opsiyonel):**

```json
{
  "completed_questions": 10,
  "completed_topics": 1
}
```

Finish, net odak süresini (`paused_seconds` hariç) `actual_duration_minutes` olarak yazar.
Bağlı plan varsa `completed_minutes` / `completed_question_count` artımlı güncellenir;
plan `planned` ise `in_progress` olur (otomatik `completed` yok).

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

Kaynak: tamamlanmış `StudySession` + bağlı `StudyPlan` (JOIN). Plansız oturumlar
etiketi `"Serbest"`. Ayrı istatistik tablosu yok (Sprint-1.6). Dashboard overview alanları
(`streak_days`, `total_pomodoros`, …) `StatisticsService.get_overview` üzerinden beslenir.

| Metod | Endpoint | Açıklama | Yetki |
|-------|----------|---------|-------|
| `GET` | `/statistics/overview` | Genel özet (süre, streak, pomodoro, en çok çalışılan ders) | student |
| `GET` | `/statistics/daily` | Günlük özet + saatlik bucket (`date` opsiyonel) | student |
| `GET` | `/statistics/weekly` | Haftalık özet + günlük bucket (`anchor` opsiyonel) | student |
| `GET` | `/statistics/monthly` | Aylık özet + günlük bucket (`anchor` opsiyonel) | student |
| `GET` | `/statistics/subjects` | Ders dağılımı (`date_from`, `date_to` opsiyonel) | student |
| `GET` | `/statistics/topics` | Konu dağılımı (`date_from`, `date_to` opsiyonel) | student |
| `GET` | `/statistics/productivity` | En verimli gün/saat içgörüsü | student |
| `GET` | `/statistics/heatmap` | Son 30 gün ısı haritası | student |
| `GET` | `/statistics/streak` | Ardışık çalışma günü | student |

Öğretmen/kurum öğrenci istatistikleri sonraki sprintlere ertelendi.
Soru girişi ve performans istatistikleri: §2.9b `/questions`.

---

### 2.9b `/api/v1/questions` — Soru Takibi (Sprint-1.9)

Kaynak: `question_records` tablosu. Soft delete yok (hard delete).
`subject` / `topic` düz string (Subject tablosu yok — A1).
Dashboard `today_questions_solved` bu kayıtlardan hesaplanır (B1).

| Metod | Endpoint | Açıklama | Yetki |
|-------|----------|---------|-------|
| `GET` | `/questions` | Liste (sayfalama + filtre) | student |
| `GET` | `/questions/{id}` | Detay | student |
| `POST` | `/questions` | Oluştur | student |
| `PUT` | `/questions/{id}` | Güncelle | student |
| `DELETE` | `/questions/{id}` | Sil (hard) | student |
| `GET` | `/questions/statistics` | Özet (toplam/bugün/hafta/ay, net, oranlar) | student |
| `GET` | `/questions/daily` | Günlük bucket (`days` opsiyonel) | student |
| `GET` | `/questions/subjects` | Ders dağılımı | student |
| `GET` | `/questions/topics` | Konu dağılımı | student |
| `GET` | `/questions/exams` | Sınav türü dağılımı | student |

**Liste filtreleri:** `date_from`, `date_to`, `subject`, `topic`, `exam_type`, `source`,
`study_plan_id`, `study_session_id`, `page`, `page_size`.

**Enum'lar:** `exam_type` (tyt/ayt/yks/lgs/kpss/ales/dgs/yds/custom),
`difficulty` (easy/medium/hard), `source` (book/video/past_exam/online/class/other).

**Net:** `correct − wrong × 0.25` (YKS emsali; diğer sınavlar şimdilik aynı).

---

### 2.9c `/api/v1/goals` — Goal Engine (Sprint-2.1)

Kaynak: `goals` tablosu. Auth: student. AI Goal oluşturmaz; Insight Engine okur.
Progress: QuestionRecord / StudySession event hook + create recompute (A1).
Plan complete standart goal tiplerine katkı yapmaz (B1).

| Metod | Endpoint | Açıklama | Yetki |
|-------|----------|---------|-------|
| `GET` | `/goals` | Tüm hedefler | student |
| `POST` | `/goals` | Oluştur | student |
| `GET` | `/goals/active` | Aktif hedefler | student |
| `GET` | `/goals/completed` | Tamamlananlar | student |
| `GET` | `/goals/progress` | İlerleme özeti | student |
| `GET` | `/goals/weekly` | Haftalık period | student |
| `GET` | `/goals/monthly` | Aylık period | student |
| `GET` | `/goals/{id}` | Detay | student |
| `PATCH` | `/goals/{id}` | Güncelle | student |
| `DELETE` | `/goals/{id}` | Sil | student |

**Enum'lar:** `goal_type` (study_time/pomodoro/question/subject/topic/custom),
`period` (daily/weekly/monthly/custom), `priority` (low/medium/high/critical),
`status` (active/completed/paused/cancelled).

---

### 2.10 `/api/v1/exams` — Öğrenci Deneme Takibi (Sprint-2.6)

> **B2:** Öğrenci kişisel deneme API'si `/exams` altında.
> Kurumsal K-14 Exam henüz implemente değil; bu endpoint grubu S-13 içindir.

| Metod | Endpoint | Açıklama | Yetki |
|-------|----------|---------|-------|
| `GET` | `/exams` | Deneme listesi (`exam_type` filtre) | student |
| `POST` | `/exams` | Deneme + nested `results[]` oluştur | student |
| `GET` | `/exams/statistics` | Özet istatistikler | student |
| `GET` | `/exams/trends` | Net zaman / ders / D-Y-B | student |
| `GET` | `/exams/{id}` | Detay + sonuçlar | student |
| `PATCH` | `/exams/{id}` | Meta güncelle (title, notes, …) | student |
| `PUT` | `/exams/{id}/results` | Sonuçları toplu yenile (D1) | student |
| `DELETE` | `/exams/{id}` | Hard delete + CASCADE results (E1) | student |

**POST body:** `{ title, exam_type, exam_date, duration_minutes?, notes?, results?[] }`  
**Net:** Question Tracking formülü (`correct − wrong × 0.25`); G1 strategy hook.

---

### 2.10b `/api/v1/planner` — Adaptive Study Planner (Sprint-2.7)

> **B1:** Haftalık adaptive plan taslağı. LLM plan **üretmez**; rule engine üretir.
> Her madde için saklanan `reason` Explain / Dashboard / Chat tarafından yeniden üretim olmadan okunur.
> LLM yalnızca Explain’de gerekçeyi doğal dile çevirir (P1).

| Metod | Endpoint | Açıklama | Yetki |
|-------|----------|---------|-------|
| `POST` | `/planner/generate` | Rule-based taslak üret (items + reason) | student |
| `GET` | `/planner/{id}` | Taslak detayı | student |
| `POST` | `/planner/{id}/accept` | StudyPlan satırlarına yaz (E1/F1); `force` (G3) | student |
| `POST` | `/planner/{id}/explain` | Saklanan rationale’ı LLM ile açıkla (L1/P1) | student |

**Generate body:** `{ target_exam, target_net, available_days[0–6], available_hours }`  
**Accept body:** `{ force?: false }` — çakışmada 409 + details; `force=true` yanına ekler.  
**Item:** `study_date`, `title`, `subject`, `topic?`, `target_question_count`, `estimated_minutes`, `resource_ids[]`, `reason`.

---

### 2.10c `/api/v1/revisions` — Revision & Spaced Repetition (Sprint-2.8)

> **B1:** Yanlış defteri + SRS. LLM kuyruk/interval **üretmez**; Rule Engine (SM-2 lite) üretir.
> Her kartta `source_type`, `reason`, `difficulty` (1–5) saklanır. Explain yeniden üretim yapmaz.

| Metod | Endpoint | Açıklama | Yetki |
|-------|----------|---------|-------|
| `GET` | `/revisions` | Liste (status/subject/source_type) | student |
| `POST` | `/revisions` | Manuel kart | student |
| `GET` | `/revisions/today` | Bugün due (+ overdue) | student |
| `GET` | `/revisions/week` | Bu hafta due | student |
| `GET` | `/revisions/overdue` | Gecikmiş | student |
| `GET` | `/revisions/statistics` | Özet istatistik | student |
| `GET` | `/revisions/heatmap` | Review heatmap (R2) | student |
| `POST` | `/revisions/generate` | Rule seed (QR + exam) | student |
| `GET` | `/revisions/{id}` | Detay | student |
| `PATCH` | `/revisions/{id}` | Güncelle | student |
| `DELETE` | `/revisions/{id}` | Soft archive | student |
| `POST` | `/revisions/{id}/review` | Grade → interval/difficulty | student |
| `POST` | `/revisions/{id}/skip` | Due kaydır | student |
| `POST` | `/revisions/{id}/postpone` | Ertele | student |
| `POST` | `/revisions/{id}/explain` | Saklanan reason → LLM | student |

**Review body:** `{ grade: again\|hard\|good\|easy, duration_seconds? }`  
**source_type:** `manual`, `question_tracking`, `exam`, `planner`, `ai_suggestion`

---

### 2.10d `/api/v1/achievements` — Achievement Engine (Sprint-2.9)

> **B1 / U1:** Data-driven katalog. LLM unlock **üretmez**; RuleEngine `criteria` JSONB değerlendirir.
> Unlock’ta `reason` saklanır. Explain / Dashboard / Chat yeniden üretim yapmaz.

| Metod | Endpoint | Açıklama | Yetki |
|-------|----------|---------|-------|
| `GET` | `/achievements` | Katalog | student |
| `GET` | `/achievements/unlocked` | Açılan rozetler | student |
| `GET` | `/achievements/progress` | İlerleme | student |
| `POST` | `/achievements/check` | Event/snapshot evaluate (idempotent) | student |
| `GET` | `/achievements/{id}` | Detay + unlock durumu | student |
| `POST` | `/achievements/{id}/explain` | Saklanan reason → LLM | student |

**criteria:** `{ metric, op: gte\|eq\|lte\|contains, value, events? }`  
**UNIQUE:** `(user_id, achievement_id)` — ikinci unlock yok.

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

### 2.12 `/api/v1/notification-settings` — Bildirim Ayarları

> **Sprint-1.8 (Meeting-016):** Ayrı `notification_preferences` tablosu (C1).
> Inbox (`/notifications`) bu sprintte yok (B1). FCM token kaydı altyapı; gerçek push sonraki sprint (A1).

| Metod | Endpoint | Açıklama | Yetki |
|-------|----------|---------|-------|
| `GET` | `/notification-settings` | Tercihleri oku (yoksa varsayılan oluştur) | Authenticated |
| `PUT` | `/notification-settings` | Tercihleri kısmi güncelle | Authenticated |
| `PUT` | `/notification-settings/fcm-token` | FCM token kaydet (stub/gerçek) | Authenticated |

**Okuma alanları:** `pomodoro_enabled`, `long_break_enabled`, `daily_reminder_enabled`,
`daily_goal_enabled`, `streak_reminder_enabled`, `widget_auto_update_enabled`,
`reminder_time`, `quiet_hours_*`, `has_fcm_token` (token değeri dönülmez).

---

### 2.12b `/api/v1/notifications` — Bildirimler (Inbox — sonraki sprint)

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

> **Sprint-2.0 (Meeting-018):** Rule-based Insight Engine. Gerçek LLM yok.
> Yanıtlar Session/Statistics + QuestionRecord aggregate üzerinden canlı hesaplanır
> (persist tablosu yok — A1). Yetki: authenticated student (premium gate yok — B1).
> Doğruluk / soru trendi = QuestionRecord; süre / pomodoro / streak = Session (D1).

#### 2.14a Insight GET API (Sprint-2.0 — implemente)

| Metod | Endpoint | Açıklama | Yetki |
|-------|----------|---------|-------|
| `GET` | `/ai/overview` | Özet metrikler + top recommendation | student |
| `GET` | `/ai/recommendations` | RuleEngine öneri listesi | student |
| `GET` | `/ai/trends` | Haftalık/aylık süre-soru trendleri | student |
| `GET` | `/ai/performance` | Doğruluk, net, ders dağılımı | student |
| `GET` | `/ai/productivity` | Verimli saat/gün, streak, idle | student |

#### 2.14c AI Chat (Sprint-2.2 + 2.4 — gerçek LLM + Null fallback)

Context-aware sohbet. Conversation + Message persist.
`AI_PROVIDER=null|gemini|openai|claude`. Key yoksa / hata → Null fallback (B1).
Yetki: authenticated student (**premium yok — C1**).

| Metod | Endpoint | Açıklama | Yetki |
|-------|----------|---------|-------|
| `POST` | `/ai/chat` | Mesaj gönder (conversation oluştur/devam) | student |
| `POST` | `/ai/chat/stream` | SSE stub — **501** (D1) | student |
| `GET` | `/ai/settings` | Provider/model tercihi + debug | student |
| `PATCH` | `/ai/settings` | Tercih güncelle (key yok) | student |
| `GET` | `/ai/conversations` | Sohbet listesi | student |
| `GET` | `/ai/conversations/{id}` | Sohbet + mesajlar | student |
| `DELETE` | `/ai/conversations/{id}` | Sohbet sil | student |

**POST `/ai/chat` body:** `{ "message": string, "conversation_id"?: uuid }`

Chat sonrası: MemoryWriter (D1, `ai_memory_enabled`).  
Assistant metadata: `provider`, `model`, `used_fallback`.

#### 2.14d Memory Engine (Sprint-2.3 — implemente, rule-based)

Uzun dönem bellek. ILIKE + kategori arama (G1). Embedding kolonu yok; `metadata.embedding_ready`.

| Metod | Endpoint | Açıklama | Yetki |
|-------|----------|---------|-------|
| `GET` | `/memory` | Bellek listesi | student |
| `POST` | `/memory` | Manuel bellek oluştur | student |
| `GET` | `/memory/{id}` | Bellek detay (+ touch) | student |
| `PATCH` | `/memory/{id}` | Bellek güncelle (B1) | student |
| `DELETE` | `/memory/{id}` | Bellek sil | student |
| `POST` | `/memory/search` | ILIKE + kategori filtre | student |
| `GET` | `/memory/settings` | `ai_memory_enabled` | student |
| `PATCH` | `/memory/settings` | Bellek açık/kapalı (C1) | student |
| `GET` | `/memory/export` | Tüm bellekleri dışa aktar | student |
| `DELETE` | `/memory/clear` | Tüm bellekleri sil | student |

#### 2.14b LLM chat / plan (taslak — henüz yok)

| Metod | Endpoint | Açıklama | Yetki |
|-------|----------|---------|-------|
| `POST` | `/ai/study-coach` | Çalışma koçu mesajı (gerçek LLM) | student (premium) |
| `POST` | `/ai/generate-plan` | AI haftalık plan üret (LLM) | student (premium) |
| `GET` | `/ai/usage` | AI kullanım istatistiği | student |

---

### 2.15 `/api/v1/subscriptions` — Abonelik

| Metod | Endpoint | Açıklama | Yetki |
|-------|----------|---------|-------|
| `GET` | `/subscriptions/me` | Aktif abonelik bilgisi | student |
| `POST` | `/subscriptions` | Abonelik başlat | student |
| `DELETE` | `/subscriptions/me` | Abonelik iptal et | student |

---

### 2.16 `/api/v1/dashboard` — Ana Ekran Özeti

> **Not (Sprint-1.3 → Sprint-1.6):** Sprint-1.3'te süre/soru placeholder'dı; Sprint-1.4'te
> `StudyPlan.completed_*` toplamından geliyordu. **Sprint-1.5 (Meeting-013) itibarıyla
> `today_study_minutes` ve `today_questions_solved` tamamlanmış `StudySession`
> kayıtlarından hesaplanır** (plansız Pomodoro dahil). `today_plan_count` /
> `completed_plan_count` / `today_plans` hâlâ `StudyPlan`'dan gelir.
> **Sprint-1.6:** `streak_days`, `total_pomodoros`, `total_study_minutes`,
> `average_session_minutes`, `most_studied_subject`, `week_study_minutes`
> alanları `StatisticsService.get_overview` ile eklenir.
> **Sprint-1.7:** `recent_activities` Activity tablosundan (son N kayıt) gelir.
> **Sprint-1.9:** `today_questions_solved` QuestionRecord günlük aggregate'den gelir.
> **Sprint-2.0:** Additive `today_ai_recommendation` + `today_ai_recommendation_code`
> (RuleEngine top öneri; mevcut süre/soru alanları değişmez — C1).
> **Sprint-2.1:** Additive `weekly_goals` (Bu Haftaki Hedefler özeti — C1).
> DailyGoalCard / `daily_study_goal_minutes` değişmez.
> **Sprint-2.5:** Additive `today_resources_opened`, `today_resources_completed`,
> `recent_resources` (J1).
> **Sprint-2.6:** Additive `last_exam_title`, `last_exam_net`, `last_exam_delta_net`,
> `last_exam_date`, `today_ai_exam_summary` (L1).
> **Sprint-2.7:** Additive `planner_summary` (O1) — `draft_id`, `status`, `target_exam`,
> `target_net`, `item_count`, `overview_reason` (saklanan rationale; yeniden üretim yok).
> **Sprint-2.8:** Additive `revision_summary` (K1) — `due_today`, `overdue`, `due_this_week`,
> `next_due_at`, `next_title`, `overview_reason`.
> **Sprint-2.9:** Additive `achievement_summary` (K1) — `total_unlocked`, `total_points`,
> `recent_title`, `recent_reason`, `recent_unlocked_at`.
> **Sprint-3.0:** Additive `journey_progress` (K1/M1) — today/week/month/overall pct,
> `journey_stage`, `onboarding_required`, `primary_exam_type`, `days_remaining`, `baseline_level`.
> **Sprint-3.1.A:** Additive `active_exam_type`, `primary_exam_type`; `?exam_type=` Active default.
> **Sprint-3.1.B:** Additive `primary_target`, `active_target` (Hero hedef özeti);
> `today_ai_recommendation_reason` (RuleEngine evidence; LLM Explain → 3.1.D).
> **Alignment Sprint-1:** Additive Today Projection SSOT — `next_action` (tek Primary Action),
> `today_context_lines`, `today_journey_line`. Decision sunucuda; Flutter render-only.
> UI = Today OS (Journey Hub demote).

### 2.10e `/api/v1/learning-profile` — Learning Profile (Sprint-3.0)

| Metod | Endpoint | Açıklama |
|-------|----------|---------|
| `GET/PATCH` | `/learning-profile/me` | Profil |
| `GET` | `/learning-profile/onboarding/status` | D2 can_skip |
| `POST` | `/learning-profile/onboarding/complete` | D1 complete + subject seed |
| `POST` | `/learning-profile/onboarding/skip` | D2 |
| `CRUD` | `/learning-profile/exam-targets` | B1 multi-exam |
| `GET` | `/learning-profile/subjects/catalog` | C1 |
| `GET` | `/learning-profile/subjects/me` | Kullanıcı dersleri (`?exam_type=` → Active Exam default) |
| `GET` | `/learning-profile/subjects/{subject_code}` | Subject Hub detay (Sprint-3.1.C) |

> **Sprint-3.1.C:** Hub kimliği yalnızca `subject_code`. Response bölümleri:
> `subject`, `progress`, `today`, `revision`, `plans`, `exam_summary`,
> `resources`, `flashcards`, `ai` (Öneri/Sebep; `explain_available=false` → 3.1.D).
> Migration yok; legacy activity bridge iç serviste `subject_name` ile kalabilir.
>
> **Sprint-3.1.C.x:** Onboarding `exam_targets.branch` — YKS: `sayisal|ea|sozel|dil`;
> KPSS: `lisans|onlisans|ortaogretim`. Seed TYT ortak + AYT branch; KPSS ders kodları.
> Catalog sync runtime (`ensure_catalog_synced`); Alembic yok.
>
> **Sprint-3.2.A:** `topic_catalog` + `GET /learning-profile/subjects/{subject_code}/topics`;
> Hub `topics` section. Identity = `topic_code`. Activity FK yok.
>
> **Product Vision / Sprint-3.2.B (plan):** Topic Hub `GET /learning-profile/topics/{topic_code}`;
> vizyon SSOT `docs/product/product-vision.md`.

**I1:** LLM plan/hedef/ders üretmez. **F1:** `POST /planner/generate` body opsiyonel → profile default.

| Metod | Endpoint | Açıklama | Yetki |
|-------|----------|---------|-------|
| `GET` | `/dashboard` | Giriş yapan kullanıcı için ana ekran özet verisi | student |

**Response `data` şeması:**

```json
{
  "first_name": "Kadir",
  "daily_study_goal_minutes": 100,
  "today_study_minutes": 45,
  "today_questions_solved": 15,
  "today_studied_topic": "Fizik",
  "daily_progress_percentage": 45.0,
  "last_login_at": "2026-07-15T10:00:00Z",
  "today_plan_count": 2,
  "completed_plan_count": 1,
  "today_plans": [
    {
      "id": "8f14e...",
      "user_id": "3ab21...",
      "title": "Matematik Tekrar",
      "subject": "Matematik",
      "topic": "Türev",
      "target_question_count": 20,
      "estimated_minutes": 60,
      "planned_start_time": null,
      "planned_end_time": null,
      "status": "completed",
      "completed_question_count": 15,
      "completed_minutes": 45,
      "order_index": 0,
      "study_date": "2026-07-16",
      "created_at": "2026-07-16T06:00:00Z",
      "updated_at": "2026-07-16T07:00:00Z"
    }
  ],
  "streak_days": 3,
  "total_pomodoros": 12,
  "total_study_minutes": 480,
  "average_session_minutes": 28.5,
  "most_studied_subject": "Matematik",
  "week_study_minutes": 120,
  "today_ai_recommendation": "Ritmini koru — bugün kısa bir Pomodoro ile başla.",
  "today_ai_recommendation_code": "keep_going",
  "weekly_goals": [
    {
      "id": "...",
      "title": "Haftalık 500 soru",
      "progress": 42.0,
      "remaining": 290.0,
      "eta_hint": "Günde ~48.3 soru",
      "goal_type": "question",
      "status": "active"
    }
  ],
  "today_resources_opened": 2,
  "today_resources_completed": 1,
  "recent_resources": [
    {
      "id": "...",
      "title": "TYT Matematik",
      "resource_type": "youtube",
      "status": "in_progress",
      "url": "https://www.youtube.com/watch?v=...",
      "order_index": 0
    }
  ],
  "recent_activities": [
    {
      "id": "...",
      "user_id": "...",
      "event_type": "session_completed",
      "title": "25 dk Pomodoro tamamlandı",
      "description": "Matematik Tekrar",
      "study_session_id": "...",
      "study_plan_id": "...",
      "metadata": {"actual_duration_minutes": 25},
      "occurred_at": "2026-07-16T10:30:00Z",
      "created_at": "2026-07-16T10:30:00Z"
    }
  ]
}
```

`daily_study_goal_minutes`, bugün için tanımlı plan varsa planların `estimated_minutes`
toplamından, tanımlı değilse `DEFAULT_DAILY_STUDY_GOAL_MINUTES` sabitinden (120 dk) hesaplanır.
`today_studied_topic`, devam eden (`in_progress`) bir plan varsa onun konusunu, yoksa en son
tamamlanan planın konusunu döner; hiç plan yoksa `null`'dur.

---

## 3. Yetki Matrisi Özeti

| Endpoint Grubu | student | teacher | institution_admin | system_admin |
|---------------|---------|---------|------------------|--------------|
| `/auth/*` | ✅ | ✅ | ✅ | ✅ |
| `/users/me` | ✅ | ✅ | ✅ | ✅ |
| `/dashboard` | ✅ | — | — | — |
| `/students/me` | ✅ | — | — | — |
| `/students/{id}` | — | ✅ (kendi) | ✅ (kendi) | ✅ |
| `/institutions` | — | — | ✅ (kendi) | ✅ |
| `/classes` | — | ✅ (kendi) | ✅ (kendi) | ✅ |
| `/study-plans` | ✅ (kendi) | — | — | ✅ |
| `/resources` | ✅ (kendi) | — | — | ✅ |
| `/exams` | ✅ (kendi) | — | — | ✅ |
| `/study-sessions` | ✅ (kendi) | — | — | ✅ |
| `/subjects` | ✅ (okuma) | ✅ (okuma) | ✅ (okuma) | ✅ |
| `/statistics/*` | ✅ (kendi) | — | — | ✅ |
| `/statistics/students/{id}` | — | (sonraki sprint) | (sonraki sprint) | — |
| `/exams` | ✅ (okuma) | ✅ | ✅ | ✅ |
| `/assignments` | ✅ (okuma/teslim) | ✅ | — | ✅ |
| `/notifications` | ✅ (kendi) | ✅ (kendi) | ✅ (kendi) | ✅ |
| `/files` | ✅ | ✅ | ✅ | ✅ |
| `/ai` | ✅ (auth; premium gate yok — C1) | — | — | ✅ |
| `/subscriptions/me` | ✅ | — | — | — |

---

## 4. Sayfalama ve Filtreleme Standartları

### Sayfalama

Tüm liste endpoint'leri sayfalamayı destekler. Varsayılan `page_size` değeri 20, maksimum 100'dür.

### Filtreleme Örnekleri

```
GET /api/v1/subjects?exam_type=yks                   → YKS dersleri
GET /api/v1/study-plans?study_date=2026-07-16         → 16 Temmuz planları
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
| 1.1 | 2026-07-15 | `/dashboard` endpoint grubu eklendi — Meeting-011 (Sprint-1.3) |
| 1.2 | 2026-07-16 | `/study-plans` implemente; `/dashboard` StudyPlan verisine geçti — Meeting-012 |
| 1.3 | 2026-07-16 | `/study-sessions` (Pomodoro) implemente; Dashboard süre/soru StudySession'dan — Meeting-013 |
