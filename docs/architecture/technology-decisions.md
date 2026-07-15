# StudyOS — Teknoloji Kararları

**Belge Durumu:** Kabul Edildi — Proje Sahibi Onayladı  
**Sürüm:** 1.1  
**Oluşturuldu:** 2026-07-06 — Meeting-006  
**Güncelleme Tarihi:** 2026-07-06 — Meeting-006 (Proje sahibi onayı)  
**Dil:** Türkçe  
**Kapsam:** StudyOS MVP ve sonrasına yönelik teknoloji yığını kararları  
**Kaynak Belgeler:** `docs/requirements/`, `docs/planning/feature-matrix.md`

> Bu belge proje sahibi tarafından onaylanmıştır. Değişiklik için yeni bir toplantı ve onay gerekir.

---

## Bağlam

StudyOS iki bağımsız üründen oluşur:

1. **Öğrenci Mobil Uygulaması** — Flutter tabanlı, Android ve iOS.
2. **Kurumsal Web Platformu** — Web tabanlı, dershane yönetim sistemi.

İki ürün ortak bir backend API ve veritabanı altyapısı üzerinden haberleşir. Teknoloji seçimleri aşağıdaki kısıtlara göre yapılmıştır:

- **Ekip büyüklüğü:** 2 kişi.
- **Öncelik:** Geliştirici verimliliği, sürdürülebilirlik, ölçeklenebilirlik.
- **Hedef:** MVP önce, sonra ölçeklenen sistem.
- **Bütçe:** Başlangıçta minimal, büyüme ile orantılı artış.

---

## 1. Mobil Framework

### Karşılaştırma

| Kriter | Flutter | React Native |
|--------|---------|--------------|
| **Dil** | Dart | JavaScript / TypeScript |
| **Performans** | Native'e yakın (Skia/Impeller renderer) | Köprü (bridge) nedeniyle hafif gecikme |
| **UI Tutarlılığı** | Her platformda aynı (kendi render) | Platform native bileşenleri |
| **Ekosistem** | Güçlü, Google destekli | Geniş, Meta destekli |
| **Öğrenme Eğrisi** | Dart — orta düzey | JS bilenlere düşük |
| **Çevrimdışı Destek** | Güçlü | Kütüphane bağımlı |
| **Web / Desktop** | Ek destek mevcut | Web: sınırlı |
| **State Yönetimi** | Riverpod, Bloc, Provider | Redux, Zustand, MobX |

### Avantajlar / Dezavantajlar

**Flutter**
- ✅ Tek kod tabanı ile yüksek kaliteli, tutarlı UI.
- ✅ Dart dilinin katı tür sistemi hata oranını düşürür.
- ✅ Hot reload ile hızlı geliştirme döngüsü.
- ✅ Gereksinim belgesinde Flutter ile geliştirme açıkça belirtilmiş (`institution-platform-requirements.md §4`).
- ❌ Dart ekosistemi JavaScript kadar geniş değil.
- ❌ App Store/Play Store paket boyutu React Native'e göre biraz daha büyük.

**React Native**
- ✅ JS/TS ekibi varsa sıfır öğrenme maliyeti.
- ✅ npm ekosistemi oldukça geniş.
- ❌ Köprü (bridge) mimarisi performans sorununa yol açabilir.
- ❌ UI platform farkları ek test maliyeti yaratır.
- ❌ Projenin mevcut gereksinim belgesiyle uyumsuz.

### Karar: **Flutter**

**Gerekçe:** Gereksinim belgesi Flutter'ı açıkça belirtmekte, iki kişilik ekip için tek kod tabanı kritik avantaj sağlamakta ve Dart'ın tip güvenliği MVP kalitesini artırmaktadır.

---

## 2. Backend Framework

### Karşılaştırma

| Kriter | FastAPI | NestJS | ASP.NET Core |
|--------|---------|--------|--------------|
| **Dil** | Python | TypeScript | C# |
| **Performans** | Çok yüksek (async) | Yüksek | Çok yüksek |
| **Geliştirme Hızı** | Çok hızlı | Orta | Yavaş |
| **AI Entegrasyonu** | Mükemmel (Python ekosistemi) | Orta (HTTP client) | Orta |
| **Dokümantasyon** | Otomatik (Swagger/OpenAPI) | Manuel veya dekoratör | Manuel |
| **Öğrenme Eğrisi** | Düşük | Orta (Angular benzeri) | Yüksek |
| **Ekip Büyüklüğü** | 1–5 kişi idealdir | 3–10 kişi | Kurumsal |
| **Ekosistem** | PyPI (AI kütüphaneleri) | npm | NuGet |

### Avantajlar / Dezavantajlar

**FastAPI**
- ✅ Python AI ekosistemiyle (LangChain, OpenAI SDK, Hugging Face) doğrudan entegrasyon.
- ✅ Pydantic ile otomatik veri doğrulama ve dokümantasyon.
- ✅ Async-first mimari, yüksek eşzamanlılık.
- ✅ Gereksinim belgesinde açıkça belirtilmiş.
- ✅ İki kişilik ekip için düşük öğrenme eğrisi.
- ❌ JavaScript/TypeScript bilen ekip için çift dil yükü (Dart + Python).
- ❌ Büyük monolitik projelerde yapısal disiplin gerektirir.

**NestJS**
- ✅ TypeScript ile güçlü tip güvenliği.
- ✅ Angular benzeri modüler yapı, kurumsal kod düzeni.
- ❌ AI kütüphaneleri Python ekosistemi kadar zengin değil.
- ❌ İki kişilik ekip için aşırı yapı (boilerplate).

**ASP.NET Core**
- ✅ Yüksek performans, Microsoft desteği.
- ❌ C# öğrenme maliyeti, uzun geliştirme süresi.
- ❌ İki kişilik ekip için kurumsal ağırlık orantısız.

### Karar: **FastAPI**

**Gerekçe:** Gereksinim belgesinde açıkça belirtilmiş, Python AI ekosistemiyle entegrasyon kritik avantaj, düşük öğrenme eğrisi ve otomatik API dokümantasyonu iki kişilik ekip verimliliğini maksimize eder.

---

## 3. Veritabanı

### Karşılaştırma

| Kriter | PostgreSQL | MySQL | MongoDB |
|--------|-----------|-------|---------|
| **Tür** | İlişkisel (SQL) | İlişkisel (SQL) | Döküman (NoSQL) |
| **JSON Desteği** | JSONB — mükemmel | JSON — sınırlı | Native |
| **ACID Uyumu** | Tam | Tam | Kısmi (4.0+) |
| **Ölçeklenebilirlik** | Dikey + yatay (pgBouncer) | Dikey ağırlıklı | Yatay — kolay |
| **Karmaşık Sorgular** | Çok güçlü | Orta | Zayıf |
| **Olgunluk** | 30+ yıl | 30+ yıl | 15+ yıl |
| **AI/Vektör Desteği** | pgvector eklentisi | Yok | Atlas Vector Search |
| **Ücretsiz Tier** | Evet (self-hosted) | Evet | 512 MB Atlas |

### Avantajlar / Dezavantajlar

**PostgreSQL**
- ✅ Kullanıcı, kurum, sınıf, ödev gibi ilişkisel veriler için ideal.
- ✅ JSONB ile esnek şema alanları (AI analiz sonuçları vb.).
- ✅ pgvector ile gelecekte yerel vektör arama (AI özellikler).
- ✅ Supabase, Railway, Render gibi managed servislerle kolayca dağıtım.
- ✅ Gereksinim belgesinde açıkça belirtilmiş.
- ❌ Yatay ölçekleme MySQL'e göre daha fazla yapılandırma gerektirir.

**MySQL**
- ✅ Geniş hosting desteği, düşük maliyet.
- ❌ PostgreSQL'e kıyasla daha az özellik (window functions, CTE, JSONB).
- ❌ AI entegrasyon ekosistemi zayıf.

**MongoDB**
- ✅ Esnek şema, hızlı prototipleme.
- ❌ Kurum-öğrenci-sınıf gibi ilişkisel veriler için JOIN eksikliği ciddi sorun.
- ❌ Şema denetimi zayıf, veri tutarlılığı riskli.
- ❌ İki kişilik ekip için veri modeli karmaşıklığı artar.

### Karar: **PostgreSQL**

**Gerekçe:** Gereksinim belgesinde belirtilmiş, ilişkisel veri modeli projeye uygun, JSONB ile esneklik korunuyor, pgvector ile AI özellikler için hazır altyapı.

---

## 4. Kimlik Doğrulama (Authentication)

### Karşılaştırma

| Kriter | Firebase Authentication | JWT + OAuth (Kendi Implementasyonu) |
|--------|------------------------|-------------------------------------|
| **Kurulum Süresi** | < 1 saat | 2–5 gün |
| **Sosyal Giriş** | Hazır (Google, Apple) | Kütüphane ile mümkün |
| **E-posta Doğrulama** | Hazır | Kendisi yazılmalı |
| **Şifre Sıfırlama** | Hazır | Kendisi yazılmalı |
| **Güvenlik** | Google yönetimli | Kendi sorumluluğu |
| **Flutter SDK** | Var (firebase_auth) | Kütüphane ile |
| **Vendor Lock-in** | Firebase bağımlılığı | Yok |
| **Maliyet (10K kullanıcı)** | Ücretsiz (50K MAU'ya kadar) | Sadece sunucu maliyeti |

### Avantajlar / Dezavantajlar

**Firebase Authentication**
- ✅ MVP hızı: Giriş, kayıt, şifre sıfırlama, e-posta doğrulama hazır.
- ✅ Mobil SDK Flutter ile entegre (firebase_auth paketi).
- ✅ 50.000 aylık aktif kullanıcıya kadar ücretsiz.
- ✅ Güvenlik yönetimi Google'a devrediliyor.
- ❌ Firebase ekosistemini bir kez kullanmaya başlayınca ayrılmak maliyetli.
- ❌ Backend JWT doğrulaması için Firebase Admin SDK gerekiyor.

**JWT + OAuth (Kendi Implementasyonu)**
- ✅ Tam kontrol, vendor bağımlılığı yok.
- ✅ FastAPI ile python-jose, passlib gibi kütüphanelerle entegrasyon kolay.
- ✅ Firebase'e kıyasla uzun vadede sıfır vendor bağımlılığı.
- ✅ Supabase, AWS veya herhangi bir altyapıyla serbestçe çalışır.
- ❌ E-posta gönderme, token yenileme, şifre sıfırlama implementasyonu zaman alır.
- ❌ Güvenlik açıkları kendi sorumluluğumuzda.

### Karar: **JWT (python-jose + passlib)**

**Araçlar:** `python-jose`, `passlib[bcrypt]` (FastAPI), `dio` + güvenli depolama (Flutter).

**Gerekçe:** Proje sahibi vendor bağımsızlığını tercih etti. JWT ile tam kontrol sağlanır; Firebase bağımlılığı oluşmaz. E-posta doğrulama için `fastapi-mail`, şifre sıfırlama için token tabanlı akış uygulanacak. Başlangıç geliştirme süresi biraz uzasa da uzun vadede platform bağımsızlığı kazanılır.

**Neden Firebase Authentication seçilmedi:** Vendor lock-in riski ve Firebase Admin SDK bağımlılığı proje sahibi tarafından kabul edilmedi.

---

## 5. Bulut Depolama (Cloud Storage)

### Karşılaştırma

| Kriter | Supabase Storage | Firebase Storage | AWS S3 |
|--------|-----------------|-----------------|--------|
| **Ücretsiz Tier** | 1 GB | 5 GB | 5 GB (12 ay) |
| **Fiyatlandırma** | $0.021/GB | $0.026/GB | $0.023/GB |
| **CDN** | Global | Google CDN | CloudFront (ekstra) |
| **Kurulum Kolaylığı** | Çok kolay | Çok kolay | Orta |
| **Backend Entegrasyonu** | PostgreSQL ile aynı platform | Firebase ekosistemi | Bağımsız |
| **Güvenlik Kuralları** | PostgreSQL RLS ile | Firebase Rules | IAM |
| **Ölçeklenebilirlik** | Orta | Yüksek | Çok yüksek |
| **S3 API Uyumu** | Evet | Hayır | Native |
| **Yerel Geliştirme** | Docker ile Supabase | Emülatör | **MinIO** |

### Avantajlar / Dezavantajlar

**Supabase Storage**
- ✅ PostgreSQL ile aynı platform.
- ✅ S3 uyumlu API — AWS S3'e geçiş kolaylaşır.
- ❌ Startup riski; görece genç platform.

**Firebase Storage**
- ✅ Firebase ekosistemiyle entegrasyon.
- ❌ JWT tabanlı sistemde gereksiz bağımlılık yaratır.
- ❌ S3 API uyumu yok — geçiş maliyetli.

**AWS S3**
- ✅ Sektör standardı, sınırsız ölçeklenebilirlik.
- ✅ IAM ile ince taneli erişim kontrolü.
- ✅ `boto3` ile FastAPI entegrasyonu olgun ve belgelenmiş.
- ✅ **MinIO** ile yerel geliştirmede birebir aynı API — ortam farkı sıfır.
- ❌ IAM yapılandırması başlangıçta öğrenme maliyeti gerektiriyor.

### Karar: **AWS S3 (Geliştirmede: MinIO)**

**Araçlar:** `boto3` (FastAPI), presigned URL ile Flutter doğrudan yükleme, MinIO Docker container (yerel).

**Gerekçe:** Proje sahibi AWS S3'ü seçti. MinIO, S3 API ile birebir uyumlu olduğu için yerel geliştirmede gerçek AWS masrafı oluşmaz; aynı kod üretimde hiçbir değişiklik gerektirmez. Supabase bağımlılığı ortadan kalkar.

**Neden Supabase Storage seçilmedi:** JWT tabanlı auth ile Supabase RLS entegrasyonu gereksiz karmaşıklık yaratır; startup riski göz önüne alındığında AWS S3 daha güvenilir.

**Neden Firebase Storage seçilmedi:** S3 API uyumu yok; sistemde JWT kullanıldığından Firebase ekosistemi anlamsız.

---

## 6. Push Notifications

### Karşılaştırma

| Kriter | Firebase Cloud Messaging (FCM) | OneSignal |
|--------|-------------------------------|-----------|
| **Ücretsiz Tier** | Sınırsız (mesaj başına ücret yok) | 10.000 aboneye kadar ücretsiz |
| **Flutter Desteği** | firebase_messaging paketi | flutter_onesignal paketi |
| **Segmentasyon** | Temel | Gelişmiş (A/B test dahil) |
| **Analitik** | Firebase Analytics ile | Yerleşik |
| **Kurulum Kolaylığı** | Orta (APNs sertifikası vb.) | Kolay |
| **Bağımlılık** | Firebase ekosistemi | Bağımsız |

### Avantajlar / Dezavantajlar

**Firebase Cloud Messaging**
- ✅ Firebase Authentication zaten kullanıldığı için ekosistem entegrasyonu doğal.
- ✅ Android ve iOS için tek API.
- ✅ Tamamen ücretsiz.
- ✅ Google altyapısı — yüksek güvenilirlik.
- ❌ APNs (Apple Push Notification) sertifika konfigürasyonu gerektirir.

**OneSignal**
- ✅ Kullanımı son derece kolay, sürükle-bırak segmentasyon.
- ✅ In-app mesajlar, push + e-posta + SMS tek platformda.
- ❌ 10.000 aboneyi geçince ücretli plan ($9/ay+).
- ❌ Ekstra vendor bağımlılığı.

### Karar: **Firebase Cloud Messaging (FCM)**

**Gerekçe:** Firebase Authentication zaten seçildiğinden FCM ekstra vendor eklemeden çalışır. Ücretsiz tier sınırsız, Flutter SDK mevcut. S-17 (Akıllı Bildirimler) ve S-18 (Günlük Hedef Bildirimi) MVP özellikleri için yeterli.

---

## 7. AI Entegrasyonu

### Karşılaştırma

| Kriter | OpenAI (GPT-4o) | Claude API (Anthropic) | Gemini API (Google) |
|--------|----------------|----------------------|-------------------|
| **Model Kalitesi** | Çok yüksek | Çok yüksek | Yüksek |
| **Bağlam Penceresi** | 128K token | 200K token | 1M token |
| **Fiyat (girdi/1M token)** | $2.50 (gpt-4o-mini: $0.15) | $3 (Haiku: $0.25) | $1.25 (Flash 2.5: $0.075) |
| **Fiyat (çıktı/1M token)** | $10 (gpt-4o-mini: $0.60) | $15 (Haiku: $1.25) | $5 (Flash 2.5: $0.30) |
| **Türkçe Kalitesi** | Çok iyi | Çok iyi | İyi |
| **Python SDK** | openai | anthropic | google-generativeai |
| **Ücretsiz Tier** | $5 kredi (yeni hesap) | Yok | Ücretsiz tier mevcut |
| **Rate Limit (ücretsiz)** | Yok | Yok | 15 req/dk |

### Avantajlar / Dezavantajlar

**OpenAI**
- ✅ En geniş topluluk, en fazla örnek kod.
- ✅ Function calling ile yapılandırılmış AI çıktıları.
- ✅ İleride kolayca eklenilebilir (provider abstraction ile).
- ❌ Ücretsiz tier yok; MVP başlangıcında maliyet oluşur.

**Claude API**
- ✅ Uzun bağlam penceresi (200K) — PDF analizi için ideal.
- ❌ Ücretsiz tier yok.
- ❌ MVP için öncelikli değil.

**Gemini 2.5 Flash**
- ✅ Ücretsiz tier mevcut — MVP maliyetsiz başlar.
- ✅ 1M token bağlam penceresi — en geniş.
- ✅ Gemini 2.5 serisi Türkçe performansı önceki versiyonlara göre belirgin iyileşme.
- ✅ `google-generativeai` Python SDK ile kolay entegrasyon.
- ✅ Soyutlama katmanıyla ileride OpenAI eklenmesi kolay.
- ❌ Ücretsiz tier rate limit (15 req/dk) — production'da pay-as-you-go gerekir.

### Karar: **Gemini 2.5 Flash (başlangıç) → OpenAI (ileriki aşama)**

**Araçlar:** `google-generativeai` SDK, AI Provider soyutlama katmanı (interface pattern).

**Gerekçe:** Gemini 2.5 Flash ücretsiz tieri MVP'yi maliyetsiz başlatır. Soyutlama katmanı ile gelecekte OpenAI veya başka bir provider eklenmesi tek bir adaptör yazımıyla mümkün olur.

**Mimari strateji:** Backend'de `AIProvider` abstract sınıfı tanımlanır. `GeminiProvider` ve ileride `OpenAIProvider` bu sınıfı implemente eder. Hangi provider'ın kullanılacağı ortam değişkeniyle (`AI_PROVIDER`) belirlenir.

**Neden Claude seçilmedi:** Ücretsiz tier yok; MVP için başlangıç maliyeti oluşturur.

---

## 8. State Management (Flutter)

### Karşılaştırma

| Kriter | Riverpod | Bloc | Provider |
|--------|----------|------|----------|
| **Karmaşıklık** | Orta | Yüksek | Düşük |
| **Test Edilebilirlik** | Çok yüksek | Çok yüksek | Orta |
| **Boilerplate** | Az | Çok | Az |
| **Ölçeklenebilirlik** | Yüksek | Yüksek | Düşük |
| **Kod Üretimi** | riverpod_generator | bloc | Yok |
| **Topluluk** | Büyüyen | Büyük | Büyük |
| **pub.dev Puanı** | 140+ beğeni | Yüksek | Yüksek |

### Avantajlar / Dezavantajlar

**Riverpod**
- ✅ Derleme zamanı güvenliği (compile-time safety).
- ✅ Provider'a kıyasla global state sorunları yok.
- ✅ `riverpod_generator` ile kod üretimi.
- ✅ Test yazımı kolay (ProviderContainer).
- ❌ Bloc kadar yapılandırılmış değil — büyük ekiplerde disiplin gerektirir.

**Bloc**
- ✅ Olay/durum ayrımı (Event/State) net mimari sağlar.
- ✅ Kurumsal projelerde standart.
- ❌ Çok fazla dosya: event, state, bloc, cubit — iki kişilik ekip için ağır.

**Provider**
- ✅ Kolay öğrenim.
- ❌ Büyük uygulamalarda performans sorunları.
- ❌ Riverpod Provider'ın gelişmiş halefidir; yeni projelerde önerilmiyor.

### Karar: **Riverpod**

**Gerekçe:** Derleme zamanı güvenliği, az boilerplate ve yüksek test edilebilirlik iki kişilik ekip için en uygun denge. Bloc aşırı yapısal; Provider ölçeklenmiyor.

---

## 9. Yerel Veritabanı (Local Database)

### Karşılaştırma

| Kriter | Hive | Isar | SQLite (drift) |
|--------|------|------|----------------|
| **Performans** | Yüksek | Çok yüksek | Orta–Yüksek |
| **Tip Güvenliği** | Adaptörlerle | Dart native | drift type-safe |
| **Çevrimdışı Destek** | Tam | Tam | Tam |
| **Şema Migrasyonu** | Manuel | Otomatik | drift ile kolayca |
| **Topluluk** | Büyük | Büyüyen | Büyük ve olgun |
| **Kod Üretimi** | hive_generator | isar_generator | drift_dev |
| **SQL Gücü** | Yok | Yok | Tam SQL |
| **Olgunluk** | Yüksek (Hive 4) | Orta | Çok yüksek |
| **Backend Uyum** | — | — | SQLAlchemy ile aynı SQL paradigması |

### Avantajlar / Dezavantajlar

**Hive**
- ✅ Basit key-value veri için hızlı ve kolay.
- ❌ İlişkisel veri desteği yok.
- ❌ Aktif geliştirme yavaşladı.

**Isar**
- ✅ Dart native tip güvenliği, çok hızlı.
- ✅ Otomatik şema migrasyonu.
- ❌ Görece yeni, topluluk küçük.
- ❌ Bazı edge case'lerde beklenmedik davranışlar raporlanıyor.

**SQLite (drift)**
- ✅ En olgun çözüm; SQL gücü.
- ✅ `drift` ile type-safe Dart sorguları — SQL yazmak zorunda değilsin.
- ✅ Şema migrasyonu `drift`'in yerleşik aracıyla kolayca yönetilir.
- ✅ Backend'de SQLAlchemy kullanıldığından SQL paradigması tutarlı kalır.
- ✅ Büyük ve aktif topluluk; uzun vadeli destek güvencesi.
- ❌ Isar'a göre ham performansta biraz geride (pratikte fark göz ardı edilebilir).

### Karar: **drift (SQLite üzeri)**

**Araçlar:** `drift`, `drift_dev`, `sqlite3_flutter_libs`.

**Gerekçe:** Proje sahibi drift'i seçti. Olgunluk, geniş topluluk ve SQLAlchemy ile tutarlı SQL paradigması iki kişilik ekip için en güvenli seçimdir. Pomodoro verileri, yerel çalışma planı ve konu takibi gibi çevrimdışı verilerin yönetimi için yeterli performans ve esneklik sağlar.

**Neden Isar seçilmedi:** Topluluk küçüklüğü ve görece yeni olması uzun vadeli risk oluşturur.

---

## 10. ORM

### Karşılaştırma

| Kriter | SQLAlchemy | Prisma | Tortoise ORM |
|--------|-----------|--------|--------------|
| **Dil** | Python | TypeScript/Node.js | Python (async) |
| **FastAPI Uyumu** | Yüksek (SQLAlchemy 2.0 async) | FastAPI ile çalışmaz (Node.js) | Mükemmel |
| **Olgunluk** | 20+ yıl | 5 yıl | 5 yıl |
| **Tip Güvenliği** | Mypy ile | TypeScript native | Python tipleme |
| **Migration Araçları** | Alembic | Prisma Migrate | Aerich |
| **Topluluk** | Çok büyük | Büyük | Orta |

### Avantajlar / Dezavantajlar

**SQLAlchemy 2.0**
- ✅ En olgun Python ORM, sektör standardı.
- ✅ Async desteği (FastAPI ile mükemmel).
- ✅ Alembic ile güçlü şema migrasyonu.
- ✅ Pydantic + SQLAlchemy + FastAPI — kanıtlanmış kombinasyon.
- ❌ Prisma'ya kıyasla daha fazla boilerplate.

**Prisma**
- ✅ TypeScript için olağanüstü DX.
- ❌ Python/FastAPI ile uyumlu değil (Node.js için).
- ❌ Bu projeye uygulanamaz.

**Tortoise ORM**
- ✅ Django ORM'e benzer sözdizimi, hızlı öğrenim.
- ✅ Async-first.
- ❌ Topluluk küçük, SQLAlchemy kadar olgun değil.

### Karar: **SQLAlchemy 2.0 + Alembic**

**Gerekçe:** FastAPI + PostgreSQL + SQLAlchemy kombinasyonu sektörde kanıtlanmış standarttır. Alembic ile şema migrasyonu yönetilebilir. 20 yıllık ekosistem iki kişilik ekip için en güvenli seçim.

---

## 11. API Stili

### Karşılaştırma

| Kriter | REST | GraphQL |
|--------|------|---------|
| **Öğrenme Eğrisi** | Düşük | Orta–Yüksek |
| **Esneklik** | Standart endpoint'ler | İstemci istediğini alır |
| **Önbellekleme** | HTTP cache (kolay) | Karmaşık |
| **Gerçek Zamanlı** | WebSocket ile ek kurulum | Subscription |
| **FastAPI Uyumu** | Mükemmel | Strawberry ile mümkün |
| **Flutter Uyumu** | http / dio | graphql_flutter |
| **Debug Kolaylığı** | Çok kolay | GraphiQL gerektirir |
| **N+1 Sorunu** | Yok | Var (DataLoader ile çözüm) |
| **Ekip Büyüklüğü** | Tüm boyutlar | Büyük ekipler |

### Avantajlar / Dezavantajlar

**REST**
- ✅ Endüstri standardı, her geliştirici biliyor.
- ✅ HTTP önbellekleme ile performans.
- ✅ FastAPI doğrudan REST destekler.
- ✅ Swagger/OpenAPI ile otomatik dokümantasyon.
- ❌ Over-fetching veya under-fetching sorunu olabilir.

**GraphQL**
- ✅ İstemci ihtiyacı kadar veri alır.
- ✅ Karmaşık ilişkisel sorgularda güçlü.
- ❌ İki kişilik ekip için fazla karmaşıklık.
- ❌ FastAPI ile kurulum REST kadar olgun değil.
- ❌ Önbellekleme ve güvenlik yapılandırması zor.

### Karar: **REST (API versiyonlama ile)**

**Gerekçe:** İki kişilik ekip için REST açık ara daha verimli. FastAPI'nin OpenAPI desteği dokümantasyonu otomatikleştirir. MVP ölçeğinde GraphQL'in getirisini götürüsü geçer.

**Versiyon Stratejisi:** `/api/v1/` önekiyle geriye dönük uyumluluk sağlanır.

---

## 12. Dağıtım Stratejisi (Deployment)

### 12.1 Mobil Uygulama

| Platform | Strateji |
|----------|---------|
| **Android** | Google Play Store — Flutter build apk/appbundle |
| **iOS** | Apple App Store — Flutter build ipa |
| **Dağıtım Aracı** | GitHub Actions + Fastlane |
| **Test Dağıtımı** | Firebase App Distribution |

### 12.2 Backend

| Kriter | Railway | Render | Fly.io | AWS EC2 |
|--------|---------|--------|--------|---------|
| **Ücretsiz Tier** | $5 kredi | 750 saat/ay | 3 shared VM | 750 saat (12 ay) |
| **Docker Desteği** | Evet | Evet | Evet | Evet |
| **Otomatik Deploy** | GitHub push ile | GitHub push ile | CLI | CI/CD gerekir |
| **Ölçeklenebilirlik** | Orta | Orta | Yüksek | Çok yüksek |
| **Kurulum Kolaylığı** | Çok kolay | Kolay | Orta | Zor |

**Karar: Railway (MVP) → AWS EC2/ECS (Ölçek)**

**Gerekçe:** Railway, GitHub Actions entegrasyonu ve Docker desteği ile MVP için en hızlı başlangıç sağlar. Ölçek büyüdükçe AWS'ye geçiş planlanır.

### 12.3 Veritabanı

| Kriter | Supabase | Railway PostgreSQL | Render PostgreSQL |
|--------|---------|-------------------|------------------|
| **Ücretsiz Tier** | 500 MB, 2 proje | 1 GB | 1 GB (90 gün) |
| **Yedekleme** | Günlük (pro) | Manuel | Günlük (pro) |
| **Performans** | Orta | Orta | Orta |
| **Ölçeklenebilirlik** | Pro plan ile | Sınırlı | Sınırlı |

**Karar: Supabase (MVP) → Managed PostgreSQL on AWS RDS (Ölçek)**

**Gerekçe:** Supabase ücretsiz tier ve Storage entegrasyonu ile MVP için idealdir. Üretim ölçeğinde AWS RDS daha güvenilir SLA sunar.

### 12.4 Kurumsal Web Platformu (Frontend)

**Karar: Vercel veya Netlify**

İki kişilik ekip için CI/CD entegrasyonu hazır, ücretsiz tier yeterli.

---

## 13. İzleme ve Loglama (Monitoring & Logging)

### Karşılaştırma

| Araç | Tür | Ücretsiz Tier | Kullanım Durumu |
|------|-----|--------------|-----------------|
| **Sentry** | Hata takibi | 5.000 hata/ay | Backend + Flutter |
| **Datadog** | APM + Log | 14 gün trial | Kurumsal — MVP için fazla |
| **Grafana + Loki** | Log aggregation | Self-hosted ücretsiz | DevOps bilgisi gerekir |
| **Railway Logs** | Temel loglar | Dahil | MVP için yeterli |
| **Firebase Crashlytics** | Mobil çökmeler | Ücretsiz | Flutter crash raporları |

### Karar: **Sentry (Backend + Mobil)**

**Araçlar:** `sentry-sdk[fastapi]` (Python), `sentry_flutter` (Flutter).

**Gerekçe:** Sentry hem FastAPI backend hem de Flutter mobil uygulama için tek platformdan hata takibi sağlar. Proje sahibi Sentry'yi onayladı. Ücretsiz tier (5.000 hata/ay) MVP için yeterli.

**Gelecek:** 100K kullanıcı aşıldığında Datadog veya Grafana geçişi değerlendirilir.

---

## 14. Analitik (Analytics)

### Karşılaştırma

| Araç | Ücretsiz Tier | Gizlilik | Flutter SDK | Kullanım |
|------|--------------|---------|-------------|---------|
| **Firebase Analytics** | Sınırsız | Google | Hazır | Ürün analitik |
| **Mixpanel** | 20M olay/ay | Kendi sunucu | Evet | İleri kullanıcı davranışı |
| **PostHog** | 1M olay/ay | Self-hosted seçenek | Evet | Açık kaynak alternatif |
| **Amplitude** | 10M olay/ay | Evet | Evet | Kurumsal |

### Karar: **Firebase Analytics**

**Araçlar:** `firebase_analytics` (Flutter), Google Analytics entegrasyonu.

**Gerekçe:** Firebase Analytics, FCM ile birlikte zaten kullanılan Firebase ekosisteminin bir parçası. Ücretsiz, sınırsız olay kaydı ve sıfır entegrasyon maliyeti sunar. Proje sahibi onayladı.

---

## 15. CI/CD

### Karşılaştırma

| Araç | Ücretsiz Tier | Flutter Desteği | Docker | Kolaylık |
|------|--------------|----------------|--------|---------|
| **GitHub Actions** | 2.000 dk/ay | Evet | Evet | Yüksek |
| **Bitrise** | 10 dk/build | Güçlü mobil | Hayır | Çok kolay |
| **Codemagic** | 500 dk/ay | Mükemmel | Evet | Çok kolay |
| **GitLab CI** | 400 dk/ay | Evet | Evet | Orta |

### Karar: **GitHub Actions**

**Gerekçe:** GitHub zaten kullanılıyor (gereksinim belgesi), 2.000 dk/ay ücretsiz tier MVP için yeterli. Flutter build, test ve Railway deploy işlemleri otomatize edilebilir. Codemagic Flutter-specific pipeline'lar için ek seçenek olarak değerlendirilebilir.

**Pipeline Stratejisi:**
- `push → main`: Test çalıştır → Railway'e deploy et.
- `push → release`: Flutter build → Firebase App Distribution.
- `tag → v*`: App Store / Play Store dağıtımı.

---

## 16. Test Stratejisi

### Katmanlar

| Katman | Araç | Kapsam |
|--------|------|--------|
| **Birim Test (Backend)** | pytest | Servis ve yardımcı fonksiyonlar |
| **Entegrasyon Test (Backend)** | pytest + httpx | API endpoint'leri |
| **Birim Test (Flutter)** | flutter_test | Widget ve logic |
| **Entegrasyon Test (Flutter)** | integration_test | Kullanıcı akışları |
| **E2E Test (Web)** | Playwright | Kurumsal web platformu |
| **Mock** | pytest-mock, mockito (Flutter) | Bağımlılık yalıtımı |

### Kapsam Hedefleri

| Katman | MVP Hedefi | v1.1 Hedefi |
|--------|-----------|------------|
| Backend birim | %60 | %80 |
| Backend entegrasyon | Tüm kritik endpoint'ler | Tüm endpoint'ler |
| Flutter birim | %50 | %70 |
| E2E | 5 kritik akış | 15 akış |

### Karar: **pytest (Backend) + flutter_test (Mobil) + Playwright (Web)**

**Gerekçe:** Her katman için ekosistemde standart araçlar. Gereksinim belgesi "test edilmemiş kod çalışır değildir" kuralını net belirtmektedir.

---

## 17. Güvenlik

### Önlemler

| Alan | Yaklaşım | Araç / Yöntem |
|------|---------|--------------|
| **Kimlik Doğrulama** | Firebase JWT | Firebase Admin SDK |
| **Yetkilendirme** | RBAC (rol bazlı) | FastAPI Depends + rol dekoratörleri |
| **Veri Şifreleme (transit)** | TLS 1.3 | Railway / Supabase varsayılan |
| **Veri Şifreleme (depolamada)** | AES-256 | Supabase / PostgreSQL |
| **SQL Injection** | ORM parametreli sorgu | SQLAlchemy |
| **Rate Limiting** | IP bazlı sınır | slowapi (FastAPI middleware) |
| **CORS** | Beyaz liste | FastAPI CORSMiddleware |
| **Hassas Veri** | Env variables | Railway secrets / GitHub Actions secrets |
| **KVKK / GDPR** | Açık rıza, silme hakkı | Tasarım aşamasında uyumluluk |
| **Bağımlılık Güvenliği** | Düzenli güncelleme | Dependabot (GitHub) |

### Karar: Güvenlik "By Design"

**Gerekçe:** A-01 (Güvenli Kimlik Doğrulama) ve A-02 (KVKK/GDPR Uyumu) MVP gereksinimidir. Güvenlik sonradan eklenmez; baştan tasarıma dahil edilir.

---

## Maliyet Analizi

> **Not:** Fiyatlar 2026 yılı itibarıyla tahminidir ve değişkenlik gösterebilir.  
> (~) ile işaretlenen değerler tahmindir.

### MVP Dönemi (0–1.000 Kullanıcı)

| Hizmet | Plan | Tahmini Maliyet |
|--------|------|----------------|
| Firebase Authentication | Spark (Ücretsiz) | $0 |
| Firebase Analytics | Ücretsiz | $0 |
| Firebase Crashlytics | Ücretsiz | $0 |
| Firebase Cloud Messaging | Ücretsiz | $0 |
| Supabase (DB + Storage) | Free Tier | $0 |
| Railway (Backend) | Starter $5 kredi | ~$5/ay |
| Gemini API | Free Tier (15 req/dk) | $0 |
| OpenAI GPT-4o-mini | Pay-as-you-go | ~$5–10/ay |
| Sentry | Developer (Ücretsiz) | $0 |
| GitHub Actions | Free Tier | $0 |
| **Toplam** | | **~$10–15/ay** |

### 10.000 Kullanıcı

| Hizmet | Plan | Tahmini Maliyet |
|--------|------|----------------|
| Firebase Authentication | Blaze (50K MAU ücretsiz) | $0 |
| Firebase FCM | Ücretsiz | $0 |
| Supabase | Pro $25/ay | $25/ay |
| Railway / Render | Pro | ~$20/ay |
| Gemini API | Pay-as-you-go (~100K istek) | ~$5/ay |
| OpenAI GPT-4o-mini | Pay-as-you-go | ~$30–50/ay |
| Sentry | Team $26/ay | $26/ay |
| PostHog | Free (1M olay) | $0 |
| **Toplam** | | **~$86–126/ay** |

### 100.000 Kullanıcı

| Hizmet | Plan | Tahmini Maliyet |
|--------|------|----------------|
| Firebase Authentication | Blaze (~50K MAU üzeri $0.0055/MAU) | ~$275/ay |
| AWS RDS PostgreSQL | db.t3.medium | ~$50/ay |
| AWS EC2 / ECS | 2–4 instance | ~$100–200/ay |
| AWS S3 | ~500 GB | ~$12/ay |
| Gemini API | ~1M istek | ~$50/ay |
| OpenAI GPT-4o-mini | Yüksek kullanım | ~$200–400/ay |
| Sentry | Business | ~$80/ay |
| PostHog | Scale | ~$0–450/ay |
| GitHub Actions | Pro | ~$10/ay |
| **Toplam** | | **~$777–1.477/ay** |

---

## Risk Analizi

### Flutter

| Risk | Düzey | Açıklama | Azaltma |
|------|-------|---------|---------|
| Dart ekosistemi olgunluğu | Düşük | Bazı kütüphaneler bakımsız | pub.dev puanını kontrol et |
| Google desteğini kesmesi | Çok Düşük | Açık kaynak, topluluk güçlü | — |
| Migration zorluğu | Yüksek | React Native'e geçiş büyük yatırım | Flutter'a güven; göç planlamak zorunda kalmayız |
| Uzun vadeli uygulanabilirlik | Yüksek | Google aktif geliştiriyor | — |

### FastAPI

| Risk | Düzey | Açıklama | Azaltma |
|------|-------|---------|---------|
| Monolitik büyüme | Orta | Modüler yapı dağıtılmazsa | Feature-based modül yapısı |
| Python GIL performansı | Düşük | Async ile önemsiz | Async-first kodlama |
| Migration zorluğu | Orta | NestJS/Go'ya geçiş büyük efor | FastAPI'yi doğru mimariyle kullan |
| Uzun vadeli uygulanabilirlik | Çok Yüksek | Tiangolo aktif geliştirme | — |

### PostgreSQL

| Risk | Düzey | Açıklama | Azaltma |
|------|-------|---------|---------|
| Yatay ölçekleme | Orta | Read replica ile çözülebilir | pgBouncer + read replicas |
| Migration zorluğu | Düşük | SQL standart; MySQL'e kolayca geçiş | Alembic migration'ları koru |
| Uzun vadeli uygulanabilirlik | Çok Yüksek | 30+ yıl aktif, topluluğun gözdesi | — |

### Firebase Authentication

| Risk | Düzey | Açıklama | Azaltma |
|------|-------|---------|---------|
| Vendor lock-in | Orta | Firebase'den ayrılmak maliyetli | JWT soyutlama katmanı |
| Google servis kesintisi | Düşük | %99.9+ SLA | — |
| Fiyat değişikliği | Orta | Google fiyatları artırabilir | Soyutlama katmanıyla geçiş hazırlığı |
| Migration zorluğu | Yüksek | Auth0 / Supabase Auth'a geçiş büyük efor | Erken soyutlama katmanı kritik |

### Supabase Storage

| Risk | Düzey | Açıklama | Azaltma |
|------|-------|---------|---------|
| Startup riski | Orta | Supabase görece yeni şirket | S3 uyumlu API migration'ı kolaylaştırır |
| Ölçek sınırları | Orta | Free tier hızla dolabilir | Pro plana geçiş planla |
| Migration zorluğu | Düşük | S3 API uyumlu | AWS S3 veya Cloudflare R2 geçişi kolay |

### Firebase Cloud Messaging

| Risk | Düzey | Açıklama | Azantma |
|------|-------|---------|---------|
| Vendor lock-in | Orta | Firebase ekosistemine bağımlılık | FCM soyutlama servisi |
| iOS APNs yapılandırma | Orta | Sertifika yönetimi | Fastlane ile otomatize |
| Migration zorluğu | Orta | OneSignal'a geçiş birkaç günlük iş | — |

### Gemini / OpenAI API

| Risk | Düzey | Açıklama | Azaltma |
|------|-------|---------|---------|
| Fiyat artışı | Orta | AI fiyatları değişkendir | Provider soyutlama katmanı |
| Rate limit | Düşük | Pay-as-you-go'da yok | — |
| Model kalitesi | Düşük | Sürekli gelişiyor | Model değişimi kolaylaştırılmış olmalı |
| Migration zorluğu | Düşük | Provider soyutlama ile kolay | AI abstraction layer |

### Riverpod

| Risk | Düzey | Açıklama | Azaltma |
|------|-------|---------|---------|
| Öğrenme eğrisi | Orta | Bloc'tan farklı paradigma | Resmi dokümantasyon yeterli |
| v3 breaking changes | Düşük | Riverpod hâlâ aktif | Migration notlarını takip et |
| Migration zorluğu | Orta | Bloc'a geçiş 1–2 hafta | Gereksinim değişmeden göç şart değil |

### Isar

| Risk | Düzey | Açıklama | Azaltma |
|------|-------|---------|---------|
| Olgunluk | Orta | Hive'a göre daha yeni | drift (SQLite) fallback planı |
| Topluluk büyüklüğü | Orta | Büyüyen ama küçük | GitHub Issues aktif |
| Migration zorluğu | Orta | drift'e geçiş veri migrasyonu gerektirir | Soyutlama repository pattern |

### SQLAlchemy

| Risk | Düzey | Açıklama | Azaltma |
|------|-------|---------|---------|
| Async öğrenme eğrisi | Düşük | Dokümantasyon yeterli | — |
| Migration zorluğu | Düşük | Alembic migration'ları taşınabilir | — |
| Uzun vadeli uygulanabilirlik | Çok Yüksek | 20 yıllık ekosistem | — |

---

## Teknoloji Yığını Özeti

> Bu tablo proje sahibi tarafından onaylanmış nihai teknolojiyi yansıtır.

| Kategori | Seçilen Teknoloji | Ortam Notu |
|----------|------------------|------------|
| Mobil Framework | **Flutter** | Android + iOS |
| Backend Framework | **FastAPI** | Python, async |
| Veritabanı | **PostgreSQL** | Alembic migration |
| ORM | **SQLAlchemy 2.0 + Alembic** | — |
| Authentication | **JWT** (python-jose + passlib) | Vendor bağımsız |
| Bulut Depolama | **AWS S3** | Geliştirmede: MinIO |
| Push Notifications | **Firebase Cloud Messaging** | — |
| AI Entegrasyonu | **Gemini 2.5 Flash** | İleride: OpenAI |
| State Management | **Riverpod** | riverpod_generator |
| Yerel Veritabanı | **drift** (SQLite) | drift_dev |
| API Stili | **REST** | /api/v1/ öneki |
| Deploy | **Railway** | — |
| Monitoring | **Sentry** | Backend + Mobil |
| Analytics | **Firebase Analytics** | — |
| CI/CD | **GitHub Actions** | — |
| Testing | **pytest + flutter_test + Playwright** | — |

---

## Sürüm Geçmişi

| Sürüm | Tarih | Değişiklik |
|-------|-------|-----------|
| 1.0 | 2026-07-06 | İlk sürüm — Meeting-006 (öneri) |
| 1.1 | 2026-07-06 | Proje sahibi onayı uygulandı: JWT, AWS S3/MinIO, Gemini 2.5 Flash, drift |
