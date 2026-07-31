\# StudyOS — System Architecture



\*\*Belge Durumu:\*\* Resmi — SSOT

\*\*Sürüm:\*\* 2.0

\*\*Tarih:\*\* 2026-07-30

\*\*Üst Belge:\*\* docs/product/domain-model.md

\*\*Bağlı Belgeler:\*\*

\- rule-engine.md

\- observation-engine.md

\- confidence-engine.md

\- today-engine.md

\- living-plan.md

\- backend-architecture.md



\---



\# 1. Amaç



Bu belge StudyOS'un üst seviye sistem mimarisini tanımlar.



Kod değil, mimari sorumlulukları açıklar.



\---



\# 2. Mimari Yaklaşım



StudyOS katmanlı bir Learning Operating System mimarisi kullanır.



Her katman yalnızca kendi sorumluluğunu yerine getirir.



Katmanlar birbirinin işini yapmaz.



\---



\# 3. Üst Seviye Mimari



```

Client



↓



API



↓



Application Layer



↓



Learning Operating System



↓



Infrastructure



↓



Database

```



\---



\# 4. Client



Kullanıcının etkileşim kurduğu arayüzdür.



Görevleri



\- ekran oluşturmak

\- kullanıcı girdilerini almak

\- Today'i göstermek

\- Topic Work Surface'i göstermek



Karar üretmez.



\---



\# 5. API Layer



Client ile sistem arasındaki iletişimi sağlar.



Görevleri



\- request doğrulama

\- authentication

\- authorization

\- response oluşturma



İş kuralı içermez.



\---



\# 6. Application Layer



Use-case'leri yönetir.



Görevleri



\- servisleri çağırmak

\- transaction yönetmek

\- süreçleri koordine etmek



Karar üretmez.



\---



\# 7. Learning Operating System



Sistemin çekirdeğidir.



LOS aşağıdaki alt sistemlerden oluşur.



\- Observation Engine

\- Confidence Engine

\- Rule Engine

\- Today Engine

\- Living Plan

\- Learning Memory



StudyOS'un bütün zekâsı burada bulunur.



\---



\# 8. Observation Engine



Davranış verilerini toplar.



Çıktısı:



Evidence



\---



\# 9. Confidence Engine



Evidence verilerini analiz eder.



Çıktısı:



Confidence Score



\---



\# 10. Rule Engine



Confidence ve diğer sinyalleri değerlendirir.



Çıktıları



\- Decision

\- Living Plan Update

\- Today Recommendation



Rule Engine deterministik çalışır.



\---



\# 11. Today Engine



Rule Engine kararlarını kullanıcıya uygun hale getirir.



Çıktısı



Today Screen



Bugünkü çalışma burada oluşur.



\---



\# 12. Living Plan



Uzun dönem çalışma planını yönetir.



Plan oluşturmaz.



Planı sürekli adapte eder.



\---



\# 13. Learning Memory



Davranış modellerini saklar.



Örnek



\- çalışma alışkanlığı

\- süre tercihleri

\- odaklandığı saatler



\---



\# 14. Infrastructure Layer



Teknik servisleri içerir.



Örnek



\- Database

\- Cache

\- Queue

\- File Storage

\- Notification

\- AI Provider



İş kuralı içermez.



\---



\# 15. Database



Kalıcı veriyi saklar.



Temel varlıklar



\- User

\- Journey

\- Exam

\- Subject

\- Topic

\- Evidence

\- Confidence

\- Today

\- Resource



\---



\# 16. Mimari İlkeler



\- Client karar üretmez.

\- API iş kuralı içermez.

\- Application yalnızca orkestrasyon yapar.

\- LOS karar üretir.

\- Infrastructure yalnızca servis sağlar.

\- Database yalnızca veri saklar.



\---



\# 17. Veri Akışı



```

User Action



↓



Observation Engine



↓



Evidence



↓



Confidence Engine



↓



Rule Engine



↓



Today Engine



↓



UI

```



\---



\# 18. Temel Kurallar



\- Her davranış Evidence üretir.

\- Her Decision Rule Engine'den gelir.

\- Today yalnızca Today Engine tarafından oluşturulur.

\- LLM hiçbir zaman sistem kararı üretmez.

\- LOS sistemin tek karar merkezidir.



\---



\# Sonuç



StudyOS'un tüm iş mantığı Learning Operating System içerisinde bulunur.



Diğer tüm katmanlar yalnızca bu sistemi destekler.

