# StudyOS — Veritabanı Tasarımı

**Belge Durumu:** Aktif  
**Sürüm:** 1.7  
**Oluşturuldu:** 2026-07-06 — Meeting-007  
**Güncelleme Tarihi:** 2026-07-16 — Meeting-021 (§1.11e Memory + ai_memory_enabled)  
**Dil:** Türkçe  
**Kaynak:** `docs/architecture/technology-decisions.md`, `docs/planning/feature-matrix.md`

> Bu belge yüksek seviyeli veri modelini tanımlar. SQL içermez.  
> Implementasyon SQLAlchemy 2.0 ORM ile yapılacaktır.

---

## 1. Temel Varlıklar (Entities)

### 1.1 User (Kullanıcı — Temel Varlık)

Tüm kullanıcı türleri (öğrenci, öğretmen, kurum yöneticisi) bu tablodan türer.

| Alan | Tür | Açıklama |
|------|-----|---------|
| id | UUID | Birincil anahtar |
| email | String (unique) | Giriş için e-posta |
| hashed_password | String | bcrypt hash |
| first_name | String | Ad |
| last_name | String | Soyad |
| role | Enum | `student`, `teacher`, `institution_admin`, `system_admin` |
| **status** | **Enum** | **`active`, `inactive`, `pending_deletion`, `anonymized`** |
| is_verified | Boolean | E-posta doğrulandı mı |
| avatar_url | String (nullable) | S3 profil fotoğrafı yolu |
| created_at | DateTime | Kayıt tarihi |
| updated_at | DateTime | Son güncelleme |
| last_login_at | DateTime (nullable) | Son giriş zamanı |
| **deletion_requested_at** | **DateTime (nullable)** | **Silme talebi tarihi (KVKK)** |
| **anonymized_at** | **DateTime (nullable)** | **Anoniml. tarihi (KVKK)** |

---

### 1.2 RefreshToken (Yenileme Tokeni)

Refresh token rotation için token kayıtları.

| Alan | Tür | Açıklama |
|------|-----|---------|
| id | UUID | Birincil anahtar |
| user_id | UUID (FK → User) | Token sahibi |
| token_hash | String | Token'ın hash'i (güvenlik) |
| is_revoked | Boolean | Geçersiz kılındı mı |
| expires_at | DateTime | Token son kullanma tarihi |
| created_at | DateTime | Oluşturma tarihi |
| device_info | String (nullable) | Cihaz bilgisi (opsiyonel) |

---

### 1.3 Student (Öğrenci Profili) — Sprint-3.0 A1

Learning Profile hub. `role = 'student'` kullanıcılar için 1:1.

| Alan | Tür | Açıklama |
|------|-----|---------|
| id | UUID | Birincil anahtar |
| user_id | UUID (FK → User, unique) | Bağlı kullanıcı |
| journey_stage | String | M1: `new_user` \| `onboarding` \| `learning` \| `consistent` \| `advanced` (RuleEngine) |
| onboarding_completed_at | DateTime nullable | D1 |
| onboarding_skipped_at | DateTime nullable | D2 soft skip |
| daily_study_minutes | Integer | Günlük hedef |
| available_days | JSONB | 0–6 weekday list |
| available_hours | Float | Günlük saat kapasitesi |
| baseline_level | String | `unknown` \| `beginner` \| `intermediate` \| `advanced` (G1) |
| baseline_reason | String nullable | |

### 1.3b ExamTarget (Multi-exam) — Sprint-3.0 B1

| Alan | Tür | Açıklama |
|------|-----|---------|
| user_id | UUID FK | |
| exam_type | String | ExamType |
| is_primary | Boolean | |
| weight | Float | Plan dağılımı |
| target_net / score / rank | nullable | |
| target_university / department / branch | nullable | |
| exam_date | Date nullable | |
| UNIQUE(user_id, exam_type) | | |

### 1.3c SubjectCatalog + UserSubject — Sprint-3.0 C1

Seed müfredat + kullanıcı ataması. Mevcut tablolarda subject **string korunur** (FK migration yok).

---

### 1.4 Institution (Kurum)

Dershane veya eğitim kurumu kaydı. (K-01)

| Alan | Tür | Açıklama |
|------|-----|---------|
| id | UUID | Birincil anahtar |
| name | String | Kurum adı |
| slug | String (unique) | URL dostu benzersiz tanımlayıcı |
| admin_user_id | UUID (FK → User) | Ana yönetici hesabı |
| address | String (nullable) | Adres |
| phone | String (nullable) | İletişim telefonu |
| logo_url | String (nullable) | S3 logo yolu |
| is_active | Boolean | Kurum aktif mi |
| subscription_plan | Enum | `free`, `basic`, `pro` |
| created_at | DateTime | |

---

### 1.5 Branch (Şube)

Kurumun şubeleri. (K-02)

| Alan | Tür | Açıklama |
|------|-----|---------|
| id | UUID | Birincil anahtar |
| institution_id | UUID (FK → Institution) | Bağlı kurum |
| name | String | Şube adı |
| address | String (nullable) | Şube adresi |
| is_active | Boolean | |
| created_at | DateTime | |

---

### 1.6 Teacher (Öğretmen Profili)

User tablosunu genişletir. `role = 'teacher'` olan kullanıcılara karşılık gelir.

| Alan | Tür | Açıklama |
|------|-----|---------|
| id | UUID | Birincil anahtar |
| user_id | UUID (FK → User, unique) | Bağlı kullanıcı |
| institution_id | UUID (FK → Institution) | Çalıştığı kurum |
| branch_id | UUID (FK → Branch, nullable) | Atandığı şube |
| subject_expertise | String (nullable) | Branş bilgisi |
| is_active | Boolean | |

---

### 1.7 Class (Sınıf / Grup)

Kurum içinde tanımlanan öğrenci grupları. (K-03)

| Alan | Tür | Açıklama |
|------|-----|---------|
| id | UUID | Birincil anahtar |
| institution_id | UUID (FK → Institution) | Bağlı kurum |
| branch_id | UUID (FK → Branch, nullable) | Bağlı şube |
| name | String | Sınıf adı |
| grade_level | String (nullable) | Sınıf seviyesi (10. Sınıf, TYT vb.) |
| teacher_id | UUID (FK → Teacher, nullable) | Sorumlu öğretmen |
| is_active | Boolean | |
| created_at | DateTime | |

> **ClassStudent (N:N ilişki tablosu):** Bir öğrenci birden fazla sınıfta, bir sınıfta birden fazla öğrenci olabilir.
> `class_id`, `student_id`, `enrolled_at`

---

### 1.8 Subject (Ders / Konu)

Sistem genelinde tanımlı dersler. Öğrenciler bu dersler üzerinden konu ve soru takibi yapar.

| Alan | Tür | Açıklama |
|------|-----|---------|
| id | UUID | Birincil anahtar |
| name | String | Ders adı (Matematik, Fizik vb.) |
| exam_type | Enum | `yks`, `lgs`, `kpss`, `general` |
| color_hex | String | UI renk kodu |
| icon | String (nullable) | İkon tanımlayıcı |
| is_active | Boolean | |
| order_index | Integer | Sıralama |

---

### 1.9 StudyPlan (Çalışma Planı)

Kullanıcının günlük çalışma planı kalemi. (S-06) — **Sprint-1.4 (Meeting-012)** itibarıyla implemente edildi.

> **[ONAY GEREKTİRİR] — Uygulanan tasarım bu bölümün önceki taslağından farklıdır.**
> Bu bölümde daha önce tanımlı `StudyPlan` + `StudyPlanItem` (student_id/subject_id FK'li,
> çok tablolu) taslak, `Student` ve `Subject` modelleri henüz implemente edilmediği için
> kullanılamamıştır. Sprint-1.4 talebinde verilen alan listesine göre (`user_id` FK'si,
> düz `subject`/`topic` string alanları, tekil tablo) uygulanmıştır. Karar Meeting-012'de
> onaylanmıştır; `Student`/`Subject` modelleri implemente edildiğinde bu tablo migrate
> edilerek FK'li yapıya geçirilmesi değerlendirilebilir.

| Alan | Tür | Açıklama |
|------|-----|---------|
| id | UUID | Birincil anahtar |
| user_id | UUID (FK → User, `ON DELETE CASCADE`) | Plan sahibi kullanıcı |
| title | String(200) | Plan kaleminin başlığı |
| subject | String(100) | Ders adı (düz metin — henüz `Subject` tablosuna FK yok) |
| topic | String(200), nullable | Konu adı |
| target_question_count | Integer | Hedeflenen soru sayısı (> 0) |
| estimated_minutes | Integer | Tahmini süre — dakika (> 0) |
| planned_start_time | Time, nullable | Planlanan başlangıç saati |
| planned_end_time | Time, nullable | Planlanan bitiş saati (> planned_start_time) |
| status | Enum | `planned`, `in_progress`, `completed`, `skipped` |
| completed_question_count | Integer | Gerçekleşen soru sayısı (varsayılan 0) |
| completed_minutes | Integer | Gerçekleşen süre — dakika (varsayılan 0) |
| order_index | Integer | Aynı gün içindeki sıralama |
| study_date | Date | Planın ait olduğu gün (zorunlu, indeksli) |
| source | String(30) | `manual` (varsayılan) \| `planner` — Sprint-2.7 F1 |
| planner_draft_id | UUID nullable (FK → planner_drafts, SET NULL) | Adaptive draft bağlantısı |
| created_at | DateTime | |
| updated_at | DateTime | |
| deleted_at | DateTime, nullable | Soft delete zaman damgası (`NULL` = aktif) |

**İş kuralları:** Kullanıcı yalnızca kendi planlarını görebilir/düzenleyebilir (repository
katmanında `user_id` filtresi). Aynı gün içinde saat aralığı tanımlı planlar arasında
çakışma varsa oluşturma/güncelleme `400 VALIDATION_ERROR` ile reddedilir. Silme işlemi
soft delete'tir (`deleted_at` doldurulur); tüm sorgular `deleted_at IS NULL` filtresi
kullanır. `completed`/`skipped` durumları terminaldir — bu durumdan başka bir duruma
geçiş `409 CONFLICT` döner.

---

### 1.10 StudySession (Çalışma Oturumu — Pomodoro)

Pomodoro zamanlayıcı verisi. (S-10) — **Sprint-1.5 (Meeting-013)** itibarıyla implemente edildi.

> **[ONAY GEREKTİRİR] — Uygulanan tasarım bu bölümün önceki taslağından farklıdır.**
> Önceki taslak `student_id`/`subject_id` FK'liydi; `Student` ve `Subject` modelleri henüz
> yok. StudyPlan emsaline uyularak (`user_id` FK + `study_plan_id` nullable, flat tablo)
> Sprint-1.5 talep alan listesiyle uygulanmıştır. `paused_at` / `paused_seconds` alanları
> pause/resume muhasebesi için eklenmiştir (StudyPlan `deleted_at` emsali).

| Alan | Tür | Açıklama |
|------|-----|---------|
| id | UUID | Birincil anahtar |
| user_id | UUID (FK → User, `ON DELETE CASCADE`) | Oturum sahibi |
| study_plan_id | UUID (FK → StudyPlan, nullable, `ON DELETE SET NULL`) | Bağlı plan (serbest oturumda null) |
| started_at | DateTime | Başlangıç zamanı |
| ended_at | DateTime (nullable) | Bitiş zamanı |
| planned_duration_minutes | Integer | Planlanan odak süresi (dk) |
| actual_duration_minutes | Integer | Gerçekleşen net odak süresi (pause hariç, dk) |
| break_duration_minutes | Integer | Seçilen mola süresi (dk; mola istemci fazıdır) |
| completed_questions | Integer | Oturumda çözülen soru |
| completed_topics | Integer | Oturumda tamamlanan konu sayısı |
| status | Enum | `running`, `paused`, `completed` |
| paused_at | DateTime (nullable) | Aktif pause başlangıcı |
| paused_seconds | Integer | Birikmiş pause süresi (sn) |
| created_at | DateTime | |
| updated_at | DateTime | |

**İş kuralları:** Kullanıcı başına aynı anda tek aktif (`running`/`paused`) oturum;
ikinci `start` → `409 CONFLICT`. `finish` bağlı plana `completed_minutes` /
`completed_questions` artımlı yazar; plan `planned` ise `in_progress` olur — otomatik
`completed` yapılmaz. Dashboard bugünkü süre/soru metrikleri tamamlanmış oturumlardan
hesaplanır.

**İstatistikler (Sprint-1.6):** `/statistics/*` ve Dashboard overview metrikleri
(`streak`, ders/konu dağılımı, heatmap) `StudySession` + `StudyPlan` JOIN ile
aggregate edilir. Plansız oturumlar `"Serbest"` etiketi alır. Ayrı aggregate tablosu yok.

---

### 1.13 Activity (Olay / Timeline)

Kullanıcı olay akışı. **Sprint-1.7 (Meeting-015)** — Notification, Widget, AI Timeline
ve Teacher Analytics için ortak temel. Ayrı event log; Session/Plan kaynak kayıtlardan
bağımsız tutulur (`metadata` JSONB ile genişletilebilir).

| Alan | Tür | Açıklama |
|------|-----|---------|
| id | UUID | Birincil anahtar |
| user_id | UUID (FK → User, CASCADE) | Olay sahibi |
| event_type | String(64) | `session_started`, `session_paused`, `session_resumed`, `session_completed`, `plan_completed` (+ ileride yeni tipler) |
| title | String(300) | Kullanıcıya gösterilecek başlık |
| description | Text (nullable) | Kısa açıklama |
| study_session_id | UUID (FK → StudySession, SET NULL, nullable) | İlişkili oturum |
| study_plan_id | UUID (FK → StudyPlan, SET NULL, nullable) | İlişkili plan |
| metadata | JSONB (nullable) | Modül-spesifik yük (süre, subject, AI ipuçları vb.) |
| occurred_at | DateTime | Olay zamanı (timeline sıralaması) |
| created_at | DateTime | Kayıt zamanı |

**İndeksler:** `user_id`, `event_type`, `occurred_at`, `(user_id, occurred_at)`.
Dashboard `recent_activities` bu tablodan son N kaydı okur.

---

### 1.11 QuestionStatistics (Soru İstatistikleri — taslak / gelecek)

> **Not (Sprint-1.6 / 1.9):** Bu günlük aggregate tablo henüz implemente edilmedi.
> Sprint-1.9 itibarıyla ham kayıt kaynağı **§1.11b QuestionRecord**'dur.
> QuestionStatistics ileride AI / raporlama için opsiyonel materialized aggregate olabilir.

| Alan | Tür | Açıklama |
|------|-----|---------|
| id | UUID | Birincil anahtar |
| student_id | UUID (FK → Student) | |
| subject_id | UUID (FK → Subject) | |
| date | Date | İstatistik tarihi |
| questions_solved | Integer | Çözülen soru |
| questions_correct | Integer | Doğru sayısı |
| questions_wrong | Integer | Yanlış sayısı |
| questions_blank | Integer | Boş sayısı |
| net_score | Decimal | Net puan (YKS: doğru - yanlış/4) |

---

### 1.11b QuestionRecord (Soru Kaydı)

Öğrencinin girdiği soru seti kaydı. **Sprint-1.9 (Meeting-017)** — S-09.
AI analiz modülü bu tabloyu doğrudan kullanacak şekilde tasarlandı.
Subject/Topic FK yok (A1 — StudyPlan emsali düz string). Soft delete yok.

| Alan | Tür | Açıklama |
|------|-----|---------|
| id | UUID | Birincil anahtar |
| user_id | UUID (FK → User, CASCADE) | Kayıt sahibi |
| study_plan_id | UUID (FK → StudyPlan, SET NULL, nullable) | Bağlı plan |
| study_session_id | UUID (FK → StudySession, SET NULL, nullable) | Bağlı oturum |
| subject | String(100) | Ders adı (düz metin) |
| topic | String(200), nullable | Konu adı |
| question_count | Integer | Toplam soru (> 0) |
| correct_count | Integer | Doğru |
| wrong_count | Integer | Yanlış |
| blank_count | Integer | Boş |
| duration_minutes | Integer | Süre (dk) |
| difficulty | Enum nullable | `easy`, `medium`, `hard` |
| source | Enum nullable | `book`, `video`, `past_exam`, `online`, `class`, `other` |
| exam_type | Enum nullable | `tyt`, `ayt`, `yks`, `lgs`, `kpss`, `ales`, `dgs`, `yds`, `custom` |
| note | Text nullable | Not |
| net_score | Decimal | `correct − wrong × 0.25` |
| created_at | DateTime | |
| updated_at | DateTime | |

**İş kuralları:** `correct + wrong + blank == question_count`. Kullanıcı yalnızca kendi
kayıtlarını görür. Dashboard `today_questions_solved` = bugünkü `question_count` toplamı.

---

### 1.11c Goal (Hedef — Goal Engine)

Kullanıcı haftalık/aylık/özel hedefleri. **Sprint-2.1 (Meeting-019)** — S-32.
AI Insight Engine bu tabloyu **okur**; Goal oluşturmaz.
`metadata` JSONB: gelecek AI Goal Generator / Habit / Challenge / Gamification için rezerv.
Subject/Topic FK yok — düz string (QuestionRecord emsali).

| Alan | Tür | Açıklama |
|------|-----|---------|
| id | UUID | Birincil anahtar |
| user_id | UUID (FK → User, CASCADE) | Sahip |
| title | String(200) | Başlık |
| description | Text nullable | Açıklama |
| goal_type | Enum | `study_time`, `pomodoro`, `question`, `subject`, `topic`, `custom` |
| target_value | Float | Hedef değer |
| current_value | Float | Güncel ilerleme (persist — A1) |
| progress | Float | 0–100 |
| priority | Enum | `low`, `medium`, `high`, `critical` |
| period | Enum | `daily`, `weekly`, `monthly`, `custom` |
| status | Enum | `active`, `completed`, `paused`, `cancelled` |
| subject | String(100) nullable | Subject goal eşlemesi |
| topic | String(200) nullable | Topic goal eşlemesi |
| start_date | Date | Dönem başlangıcı |
| end_date | Date | Dönem bitişi |
| completed_at | DateTime nullable | Tamamlanma |
| metadata | JSONB | Gelecek genişletmeler |
| milestones_reached | JSONB list | `["25","50","75","100"]` |
| created_at | DateTime | |
| updated_at | DateTime | |

**Progress kaynakları (B1):** Study Time / Pomodoro ← `StudySession.finish`;
Question / Subject / Topic ← `QuestionRecord.create`.
`StudyPlan.complete` standart tiplere katkı yapmaz (çift sayım yok).

---

### 1.11d Conversation & Message (AI Chat)

**Sprint-2.2 (Meeting-020)** — Context-aware coach chat.
`metadata` JSONB: Memory / RAG / Voice hazırlık rezervi.

#### Conversation

| Alan | Tür | Açıklama |
|------|-----|---------|
| id | UUID | Birincil anahtar |
| user_id | UUID (FK → User, CASCADE) | Sahip |
| title | String(200) | Sohbet başlığı |
| context_version | String(20) | ContextBuilder sürümü |
| system_prompt_version | String(20) | System prompt sürümü (`v1`) |
| summary | Text (nullable) | Conversation Summary (Sprint-2.4 J1 — pasif) |
| summary_updated_at | DateTime (nullable) | Özet güncelleme |
| metadata | JSONB | Gelecek genişletmeler |
| created_at | DateTime | |
| updated_at | DateTime | |

#### Message

| Alan | Tür | Açıklama |
|------|-----|---------|
| id | UUID | Birincil anahtar |
| conversation_id | UUID (FK → Conversation, CASCADE) | Sohbet |
| role | Enum | `system`, `user`, `assistant` |
| content | Text | Mesaj metni |
| metadata | JSONB | provider, regenerate_of, vb. |
| created_at | DateTime | |

---

### 1.11e Memory (AI Memory Engine)

**Sprint-2.3 (Meeting-021)** — Long-term memory foundation.
Embedding / pgvector yok (A1). `metadata.embedding_ready` rezerv bayrağı.

| Alan | Tür | Açıklama |
|------|-----|---------|
| id | UUID | Birincil anahtar |
| user_id | UUID (FK → User, CASCADE) | Sahip |
| category | Enum/string | study_habit, goal, preference, weak_subject, strong_subject, schedule, conversation, motivation, exam, custom |
| importance | Float 0–1 | Retriever sıralama ağırlığı |
| content | Text | Bellek metni |
| source | Enum/string | ai_chat, goal_engine, study_plan, question_tracking, statistics, manual |
| last_accessed_at | DateTime (nullable) | Son erişim (touch) |
| access_count | Integer | Erişim sayacı |
| is_active | Boolean | Soft-aktif |
| metadata | JSONB | `embedding_ready`, conversation_id, vb. |
| created_at | DateTime | |
| updated_at | DateTime | |

**Retriever:** importance DESC, access_count DESC, last_accessed NULLS LAST.  
**Writer (D1):** yalnızca AI Chat kullanıcı mesajından kural tabanlı çıkarım.

---

### 1.12 Exam (Öğrenci Deneme — Sprint-2.6)

Öğrencinin girdiği deneme sınavı kaydı. **S-13 MVP (Meeting-024).**  
Kurumsal K-14 Exam henüz yok; bu tablo kişisel deneme takibidir (A1).  
Hard delete (E1). `ExamType` = QuestionRecord ile aynı enum (F2).

| Alan | Tür | Açıklama |
|------|-----|---------|
| id | UUID | Birincil anahtar |
| user_id | UUID (FK → User, CASCADE) | Sahip |
| title | String(200) | Deneme adı |
| exam_type | Enum | `tyt`, `ayt`, `yks`, `lgs`, `kpss`, `ales`, `dgs`, `yds`, `custom` |
| exam_date | Date | Sınav tarihi |
| duration_minutes | Integer | Toplam süre |
| notes | Text nullable | Notlar |
| created_at | DateTime | |
| updated_at | DateTime | |

> **ExamResult (ders sonuçları):**  
> `id`, `exam_id (FK CASCADE)`, `subject` (string), `correct_count`, `wrong_count`,  
> `blank_count`, `question_count`, `net_score`, `duration_minutes`, `created_at`, `updated_at`  
> Net: `correct − wrong × 0.25` (G1). Toplam net = ders netleri toplamı.

---

### 1.12b PlannerDraft (Adaptive Planner — Sprint-2.7)

Haftalık AI plan **taslağı**. Plan LLM ile üretilmez; `plan_payload` JSONB rule engine çıktısıdır.  
Her item’da kısa `reason` saklanır (Explain / Dashboard / Chat yeniden üretim yapmaz).  
Accept → N `StudyPlan` (`source=planner`, `planner_draft_id`).

| Alan | Tür | Açıklama |
|------|-----|---------|
| id | UUID | Birincil anahtar |
| user_id | UUID (FK → User, CASCADE) | Sahip |
| status | Enum/String | `draft`, `accepted`, `discarded` |
| target_exam | String | ExamType (H1) |
| target_net | Float | Hedef net (I2) |
| available_days | JSONB/ARRAY | 0=Pzt … 6=Paz |
| available_hours | Float | Günlük saat |
| plan_payload | JSONB | `items[]` (+ `reason`), `summary`, `rationale` |
| accepted_at | DateTime nullable | |
| created_at / updated_at | DateTime | |

> **StudyPlan ek alanları (F1):** `source` (`manual` \| `planner`), `planner_draft_id` (FK SET NULL).

---

### 1.12c RevisionItem / Schedule / Review (Sprint-2.8)

Yanlış defteri + spaced repetition. **S-11 + S-12 MVP (Meeting-026).**  
LLM kuyruk üretmez. Soft delete: `deleted_at` + `status=archived`.

| Alan (RevisionItem) | Tür | Açıklama |
|------|-----|---------|
| id | UUID | PK |
| user_id | UUID FK CASCADE | |
| title / subject / topic / note | String | |
| source_type | String | `manual`, `question_tracking`, `exam`, `planner`, `ai_suggestion` |
| source_id | UUID nullable | Kaynak referansı |
| difficulty | Int 1–5 | Rule Engine review ile günceller |
| reason | String(500) | Saklanan rationale |
| status | String | `active`, `mastered`, `archived` |
| metadata | JSONB | |
| deleted_at | DateTime nullable | Soft delete |

**RevisionSchedule (1:1):** `due_at`, `interval_days`, `ease_factor`, `repetition_count`, `lapse_count`, `last_reviewed_at`  
**RevisionReview:** `grade`, previous/new interval·difficulty·ease, `reviewed_at`

---

### 1.12d Achievement / UserAchievement / Progress (Sprint-2.9)

**S-33 MVP (Meeting-027).** Data-driven `criteria` JSONB. Unlock ledger **immutable** (S1).  
LLM unlock üretmez. Points display-only (P1).

| Tablo | Alanlar |
|-------|---------|
| **achievements** | `code` unique, title, description, category, tier, points, icon_key, criteria JSONB, is_active, sort_order |
| **user_achievements** | user_id, achievement_id, **reason**, source_event, metadata, unlocked_at; **UNIQUE(user_id, achievement_id)** |
| **achievement_progress** | user_id, achievement_id, current_value, target_value, updated_at; UNIQUE |

> Pref: `notification_preferences.achievement_notifications_enabled` (L1).

---

### 1.13 Assignment (Ödev)

Öğretmen tarafından sınıfa verilen ödevler. (K-09)

| Alan | Tür | Açıklama |
|------|-----|---------|
| id | UUID | Birincil anahtar |
| class_id | UUID (FK → Class) | Atandığı sınıf |
| teacher_id | UUID (FK → Teacher) | Oluşturan öğretmen |
| title | String | Ödev başlığı |
| description | String (nullable) | Açıklama |
| due_date | DateTime | Son teslim tarihi |
| created_at | DateTime | |

> **AssignmentSubmission (Ödev Teslimi):**
> `id`, `assignment_id (FK)`, `student_id (FK)`, `submitted_at`, `file_url (S3 key)`, `status (pending/submitted/late)`

---

### 1.14 Notification (Bildirim)

Sistem bildirimleri ve kullanıcı mesajları. (S-17, S-18, K-11)

| Alan | Tür | Açıklama |
|------|-----|---------|
| id | UUID | Birincil anahtar |
| recipient_id | UUID (FK → User) | Alıcı kullanıcı |
| sender_id | UUID (FK → User, nullable) | Gönderen (sistem = null) |
| type | Enum | `reminder`, `announcement`, `assignment`, `exam_result`, `system` |
| title | String | Bildirim başlığı |
| body | String | Bildirim içeriği |
| is_read | Boolean | Okundu mu |
| sent_via_push | Boolean | FCM ile gönderildi mi |
| created_at | DateTime | |
| read_at | DateTime (nullable) | Okunma zamanı |

---

### 1.14b NotificationPreference (Bildirim Tercihleri)

Kullanıcı başına tek satır bildirim / widget tercihi. **Sprint-1.8 (Meeting-016)** —
User modeline JSON gömülmez (C1). Inbox (`Notification`) ayrıdır ve sonraki sprinttedir.

| Alan | Tür | Açıklama |
|------|-----|---------|
| id | UUID | Birincil anahtar |
| user_id | UUID (FK → User, CASCADE, unique) | Tercih sahibi |
| pomodoro_enabled | Boolean | Pomodoro local bildirimleri |
| long_break_enabled | Boolean | Uzun mola bildirimleri |
| daily_reminder_enabled | Boolean | Günlük çalışma hatırlatması |
| daily_goal_enabled | Boolean | Günlük hedef bildirimi |
| streak_reminder_enabled | Boolean | Streak uyarıları |
| widget_auto_update_enabled | Boolean | Ana ekran widget otomatik güncelle |
| ai_memory_enabled | Boolean | AI Memory Engine açık mı (Sprint-2.3 C1, varsayılan true) |
| ai_preferred_provider | String(40) (nullable) | Kullanıcı AI provider tercihi (Sprint-2.4 E2) |
| ai_preferred_model | String(120) (nullable) | Kullanıcı model tercihi |
| reminder_time | Time (nullable) | Hatırlatma saati (yerel) |
| quiet_hours_enabled | Boolean | Sessiz saatler |
| quiet_hours_start | Time (nullable) | Sessiz başlangıç |
| quiet_hours_end | Time (nullable) | Sessiz bitiş |
| fcm_token | String(512) (nullable) | FCM token (push sonraki sprint) |
| fcm_token_updated_at | DateTime (nullable) | Token güncelleme zamanı |
| created_at | DateTime | |
| updated_at | DateTime | |

---

### 1.15 Subscription (Abonelik)

Öğrenci premium üyelik bilgisi. (S-19)

| Alan | Tür | Açıklama |
|------|-----|---------|
| id | UUID | Birincil anahtar |
| student_id | UUID (FK → Student, unique) | Abonelik sahibi |
| plan | Enum | `free`, `premium_monthly`, `premium_yearly` |
| status | Enum | `active`, `cancelled`, `expired`, `trial` |
| started_at | DateTime | Başlangıç tarihi |
| expires_at | DateTime (nullable) | Bitiş tarihi |
| payment_provider | String (nullable) | Ödeme sağlayıcı bilgisi |
| payment_reference | String (nullable) | İşlem referansı |

---

### 1.16 Material (Öğretim Materyali)

Öğretmen tarafından yüklenen PDF, doküman ve video. (K-12)

| Alan | Tür | Açıklama |
|------|-----|---------|
| id | UUID | Birincil anahtar |
| uploaded_by | UUID (FK → User) | Yükleyen öğretmen |
| class_id | UUID (FK → Class, nullable) | Atanan sınıf |
| institution_id | UUID (FK → Institution) | Kurum |
| title | String | Materyal başlığı |
| file_url | String | S3 key |
| file_type | Enum | `pdf`, `image`, `video_link`, `other` |
| file_size_bytes | Integer | Dosya boyutu |
| created_at | DateTime | |

---

### 1.17 StudyResource (Öğrenme Kaynağı)

Öğrenci kişisel kaynak kütüphanesi. **Sprint-2.5 (Meeting-023)** — S-31.
Kurumsal Material (§1.16) ile **karıştırılmaz**. Soft delete yok (D1 — hard delete).
YouTube Data API yok; `metadata.youtube_ready` rezerv alanı (G1).

| Alan | Tür | Açıklama |
|------|-----|---------|
| id | UUID | Birincil anahtar |
| user_id | UUID (FK → User, CASCADE) | Sahip |
| study_plan_id | UUID (FK → StudyPlan, SET NULL, nullable) | Bağlı plan |
| title | String(300) | Başlık |
| description | Text nullable | Açıklama |
| resource_type | Enum | `youtube`, `pdf`, `website`, `book`, `document`, `note`, `video`, `audio`, `other` |
| url | String(2000) nullable | Bağlantı |
| thumbnail_url | String(2000) nullable | Küçük resim (manuel) |
| provider | String(100) nullable | örn. `youtube` |
| duration_seconds | Integer nullable | Video/ses süresi |
| author | String(200) nullable | Yazar/kanal |
| status | Enum | `not_started`, `in_progress`, `completed`, `archived` |
| order_index | Integer | Sıra (F1) |
| last_opened_at | DateTime nullable | Son açılış (E1) |
| completed_at | DateTime nullable | Tamamlanma (E1) |
| metadata | JSONB | `youtube_ready` vb. rezerv |
| created_at | DateTime | |
| updated_at | DateTime | |

**İş kuralları:** Kullanıcı yalnızca kendi kaynaklarını görür.
`POST /resources/{id}/open` → `last_opened_at` + `not_started`→`in_progress`.
Status `completed` → `completed_at` set. Dashboard: bugün açılan/tamamlanan sayıları.

---

## 2. İlişki Diyagramı (ER Diagram)

```mermaid
erDiagram
    User {
        uuid id PK
        string email UK
        string hashed_password
        string first_name
        string last_name
        enum role
        bool is_active
        bool is_verified
        datetime created_at
    }

    RefreshToken {
        uuid id PK
        uuid user_id FK
        string token_hash
        bool is_revoked
        datetime expires_at
    }

    Student {
        uuid id PK
        uuid user_id FK
        enum exam_mode
        string target_exam
        int daily_study_goal_minutes
        string fcm_token
        uuid institution_id FK
        uuid class_id FK
    }

    Institution {
        uuid id PK
        string name
        string slug UK
        uuid admin_user_id FK
        bool is_active
        enum subscription_plan
    }

    Branch {
        uuid id PK
        uuid institution_id FK
        string name
        bool is_active
    }

    Teacher {
        uuid id PK
        uuid user_id FK
        uuid institution_id FK
        uuid branch_id FK
        string subject_expertise
    }

    Class {
        uuid id PK
        uuid institution_id FK
        uuid branch_id FK
        string name
        uuid teacher_id FK
        bool is_active
    }

    ClassStudent {
        uuid class_id FK
        uuid student_id FK
        datetime enrolled_at
    }

    Subject {
        uuid id PK
        string name
        enum exam_type
        string color_hex
        bool is_active
    }

    StudyPlan {
        uuid id PK
        uuid user_id FK
        string title
        string subject
        string topic
        int target_question_count
        int estimated_minutes
        time planned_start_time
        time planned_end_time
        enum status
        int completed_question_count
        int completed_minutes
        int order_index
        date study_date
        datetime deleted_at
    }

    StudySession {
        uuid id PK
        uuid user_id FK
        uuid study_plan_id FK
        datetime started_at
        int planned_duration_minutes
        int actual_duration_minutes
        enum status
    }

    QuestionStatistics {
        uuid id PK
        uuid student_id FK
        uuid subject_id FK
        date date
        int questions_solved
        int questions_correct
        int net_score
    }

    Exam {
        uuid id PK
        string title
        enum exam_type
        uuid created_by FK
        uuid institution_id FK
        uuid class_id FK
        date exam_date
        bool is_published
    }

    ExamResult {
        uuid id PK
        uuid exam_id FK
        uuid student_id FK
        uuid subject_id FK
        int correct
        int wrong
        int blank
        decimal net
    }

    Assignment {
        uuid id PK
        uuid class_id FK
        uuid teacher_id FK
        string title
        datetime due_date
    }

    AssignmentSubmission {
        uuid id PK
        uuid assignment_id FK
        uuid student_id FK
        datetime submitted_at
        string file_url
        enum status
    }

    Notification {
        uuid id PK
        uuid recipient_id FK
        uuid sender_id FK
        enum type
        string title
        bool is_read
        datetime created_at
    }

    Subscription {
        uuid id PK
        uuid student_id FK
        enum plan
        enum status
        datetime expires_at
    }

    Material {
        uuid id PK
        uuid uploaded_by FK
        uuid class_id FK
        uuid institution_id FK
        string title
        string file_url
        enum file_type
    }

    StudyResource {
        uuid id PK
        uuid user_id FK
        uuid study_plan_id FK
        string title
        enum resource_type
        enum status
        int order_index
        datetime last_opened_at
        datetime completed_at
    }

    User ||--o| Student : "has profile"
    User ||--o| Teacher : "has profile"
    User ||--o{ RefreshToken : "owns"
    User ||--o{ StudyPlan : "creates"
    User ||--o{ StudySession : "records"
    User ||--o{ StudyResource : "owns"
    StudySession }o--o| StudyPlan : "may link"
    StudyResource }o--o| StudyPlan : "may link"
    Student ||--o{ QuestionStatistics : "tracks"
    Student ||--o| Subscription : "has"
    Student }o--o{ Class : "ClassStudent"
    QuestionStatistics }o--|| Subject : "about"
    Institution ||--o{ Branch : "has"
    Institution ||--o{ Teacher : "employs"
    Institution ||--o{ Class : "owns"
    Institution ||--o{ Exam : "creates"
    Institution ||--o{ Material : "uploads"
    Branch ||--o{ Teacher : "assigned"
    Branch ||--o{ Class : "contains"
    Teacher ||--o{ Class : "teaches"
    Teacher ||--o{ Assignment : "assigns"
    Class ||--o{ Assignment : "receives"
    Class ||--o{ Exam : "assigned"
    Class ||--o{ Material : "receives"
    Exam ||--o{ ExamResult : "produces"
    Assignment ||--o{ AssignmentSubmission : "receives"
    User ||--o{ Notification : "receives"
```

---

## 3. Veritabanı Tasarım Kararları

### 3.1 UUID Birincil Anahtar

Tüm tablolarda `UUID v4` kullanılır. Otomatik artan integer yerine UUID kullanılmasının gerekçeleri:

- Dağıtık sistemlerde çakışma riski yok.
- Birincil anahtarlar tahmin edilemez (güvenlik).
- Veri taşıma ve merge işlemleri kolaylaşır.

### 3.2 KVKK Hesap Silme ve Veri Anonimleştirme

`is_active = false` yalnızca hesabı pasifleştirmek için kullanılır. Kalıcı hesap silme işlemlerinde aşağıdaki strateji uygulanır:

1. Kullanıcı hesap silme talebinde bulunur → `status = 'pending_deletion'`, `deletion_requested_at = NOW()`.
2. **30 gün bekleme süresi** — kullanıcı bu süre içinde hesabını geri alabilir.
3. 30 gün sonunda kişisel veriler anonimleştirilir:
   - `email` → `deleted_{uuid}@anonymized.studyos`
   - `first_name`, `last_name` → `Silinmiş Kullanıcı`
   - `hashed_password` → geçersiz hash, `avatar_url` → NULL
4. `status = 'anonymized'`, `anonymized_at = NOW()` set edilir.
5. Finansal kayıtlar yasal saklama süresi boyunca korunur; kişisel veri alanları anonimleştirilir.

> Ayrıntılı karar: `docs/decisions/ADR-002-kvkk-hesap-silme-anonimizasyon.md`

**`User` tablosuna eklenen alanlar (is_active kaldırıldı, status eklendi):**

| Alan | Tür | Açıklama |
|------|-----|----------|
| `status` | Enum | `active`, `inactive`, `pending_deletion`, `anonymized` |
| `deletion_requested_at` | DateTime (nullable) | Silme talebi tarihi |
| `anonymized_at` | DateTime (nullable) | Anonimleştirme tarihi |

### 3.3 Zaman Damgaları

Her tablo `created_at` içerir. Güncelleme gereken tablolarda `updated_at` eklenir. SQLAlchemy `onupdate` ile otomatik güncellenir.

### 3.4 JSON Alanları

AI sonuçları, ekstra metadata gibi dinamik veriler PostgreSQL `JSONB` tipinde saklanır. Bu sayede şema değişikliği gerektirmeden yeni alanlar eklenebilir.

### 3.5 İndeksler (Temel)

| Tablo | İndeks Alanı | Gerekçe |
|-------|-------------|---------|
| User | email | Giriş sorgusu |
| Student | user_id | Profil çekme |
| StudyPlan | user_id | Kullanıcının planlarını çekme |
| StudyPlan | study_date | Günlük plan sorgusu (`GET /study-plans?study_date=`) |
| StudySession | user_id | Kullanıcının oturumlarını çekme |
| StudySession | study_plan_id | Plana bağlı oturumlar |
| StudyResource | user_id | Kullanıcı kaynak listesi |
| StudyResource | study_plan_id | Plana bağlı kaynaklar |
| StudyResource | status | Durum filtresi |
| StudyResource | resource_type | Tür filtresi |
| QuestionStatistics | (student_id, date) | Tarih aralıklı istatistik |
| Notification | (recipient_id, is_read) | Okunmamış bildirim sorgusu |
| ExamResult | (exam_id, student_id) | Sınav analizi |
| RefreshToken | token_hash | Token doğrulama |

---

## Sürüm Geçmişi

| Sürüm | Tarih | Değişiklik |
|-------|-------|-----------|
| 1.0 | 2026-07-06 | İlk sürüm — Meeting-007 |
| 1.1 | 2026-07-06 | KVKK hesap silme stratejisi eklendi; User tablosu güncellendi (ADR-002) |
| 1.2 | 2026-07-16 | §1.9 StudyPlan gerçek implementasyona göre güncellendi (tekil tablo, `user_id` FK, soft delete); `StudyPlanItem` kaldırıldı — Sprint-1.4 (Meeting-012) |
| 1.3 | 2026-07-16 | §1.10 StudySession gerçek implementasyona göre güncellendi (`user_id` FK, `study_plan_id`, pause muhasebesi) — Sprint-1.5 (Meeting-013) |
| 1.4 | 2026-07-17 | §1.17 StudyResource eklendi (S-31); Material (§1.16) ayrı kaldı — Sprint-2.5 (Meeting-023) |
