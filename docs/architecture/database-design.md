# StudyOS — Veritabanı Tasarımı

**Belge Durumu:** Aktif  
**Sürüm:** 1.1  
**Oluşturuldu:** 2026-07-06 — Meeting-007  
**Güncelleme Tarihi:** 2026-07-06 — Meeting-007 açık sorular kapatıldı  
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

### 1.3 Student (Öğrenci Profili)

User tablosunu genişletir. `role = 'student'` olan kullanıcılara karşılık gelir.

| Alan | Tür | Açıklama |
|------|-----|---------|
| id | UUID | Birincil anahtar |
| user_id | UUID (FK → User, unique) | Bağlı kullanıcı |
| exam_mode | Enum | `yks`, `lgs`, `kpss`, `university` — S-02 |
| target_exam | String (nullable) | Hedef sınav adı |
| target_university | String (nullable) | Hedef üniversite (university modunda) |
| daily_study_goal_minutes | Integer | Günlük hedef çalışma süresi |
| fcm_token | String (nullable) | Firebase push notification token |
| institution_id | UUID (FK → Institution, nullable) | Bağlı kurum (varsa) |
| class_id | UUID (FK → Class, nullable) | Kayıtlı sınıf (varsa) |

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

Öğrencinin günlük çalışma planı. (S-06)

| Alan | Tür | Açıklama |
|------|-----|---------|
| id | UUID | Birincil anahtar |
| student_id | UUID (FK → Student) | Plan sahibi öğrenci |
| date | Date | Planın ait olduğu gün |
| total_planned_minutes | Integer | Toplam planlanan süre |
| total_completed_minutes | Integer | Tamamlanan süre |
| status | Enum | `pending`, `in_progress`, `completed`, `skipped` |
| created_at | DateTime | |
| updated_at | DateTime | |

> **StudyPlanItem (Plan kalemleri):**
> Her plan birden fazla kalemden oluşur.
> `id`, `study_plan_id (FK)`, `subject_id (FK)`, `planned_minutes`, `completed_minutes`, `topic_name`, `question_count_planned`, `question_count_done`, `is_completed`

---

### 1.10 StudySession (Çalışma Oturumu — Pomodoro)

Pomodoro zamanlayıcı verisi. (S-10)

| Alan | Tür | Açıklama |
|------|-----|---------|
| id | UUID | Birincil anahtar |
| student_id | UUID (FK → Student) | |
| subject_id | UUID (FK → Subject, nullable) | Çalışılan ders |
| started_at | DateTime | Başlangıç zamanı |
| ended_at | DateTime (nullable) | Bitiş zamanı |
| duration_minutes | Integer | Süre (dakika) |
| session_type | Enum | `focus`, `short_break`, `long_break` |
| question_count | Integer | O oturumda çözülen soru |

---

### 1.11 QuestionStatistics (Soru İstatistikleri)

Öğrencinin konu bazında soru performansı. (S-09, S-14)

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

### 1.12 Exam (Deneme Sınavı)

Kurum tarafından oluşturulan denemeler veya öğrencinin girdiği denemeler. (K-14, S-13)

| Alan | Tür | Açıklama |
|------|-----|---------|
| id | UUID | Birincil anahtar |
| title | String | Sınav adı |
| exam_type | Enum | `yks_tyt`, `yks_ayt`, `lgs`, `kpss`, `other` |
| created_by | UUID (FK → User) | Oluşturan kullanıcı |
| institution_id | UUID (FK → Institution, nullable) | Kurum denemesi ise |
| class_id | UUID (FK → Class, nullable) | Atanan sınıf |
| exam_date | Date | Sınav tarihi |
| is_published | Boolean | Öğrencilere görünür mü |
| created_at | DateTime | |

> **ExamResult (Sınav Sonuçları):**
> `id`, `exam_id (FK)`, `student_id (FK)`, `subject_id (FK)`, `correct`, `wrong`, `blank`, `net`, `entered_at`

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
        uuid student_id FK
        date date
        int total_planned_minutes
        int total_completed_minutes
        enum status
    }

    StudyPlanItem {
        uuid id PK
        uuid study_plan_id FK
        uuid subject_id FK
        int planned_minutes
        int completed_minutes
        string topic_name
        bool is_completed
    }

    StudySession {
        uuid id PK
        uuid student_id FK
        uuid subject_id FK
        datetime started_at
        int duration_minutes
        enum session_type
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

    User ||--o| Student : "has profile"
    User ||--o| Teacher : "has profile"
    User ||--o{ RefreshToken : "owns"
    Student ||--o{ StudyPlan : "creates"
    Student ||--o{ StudySession : "records"
    Student ||--o{ QuestionStatistics : "tracks"
    Student ||--o| Subscription : "has"
    Student }o--o{ Class : "ClassStudent"
    StudyPlan ||--o{ StudyPlanItem : "contains"
    StudyPlanItem }o--|| Subject : "about"
    StudySession }o--|| Subject : "studies"
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
| StudyPlan | (student_id, date) | Günlük plan sorgusu |
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
