\# StudyOS — Exam API



\*\*Belge Durumu:\*\* Resmi — SSOT

\*\*Sürüm:\*\* 2.0

\*\*Tarih:\*\* 2026-07-30

\*\*Üst Belge:\*\* api-overview.md



\---



\# 1. Amaç



Exam API, kullanıcının sınav paketlerini ve aktif sınavını yönetir.



\---



\# 2. Sorumluluklar



\- Exam Pack listeleme

\- Active Exam değiştirme

\- Primary Exam görüntüleme

\- Exam bilgilerini alma



\---



\# 3. Endpointler



GET /api/v1/exams



GET /api/v1/exams/{exam\_id}



GET /api/v1/exams/active



PATCH /api/v1/exams/active



GET /api/v1/exams/primary



\---



\# 4. Active Exam



Kullanıcının şu anda çalıştığı sınavdır.



Today Engine yalnızca Active Exam üzerinde çalışır.



\---



\# 5. Primary Exam



Kullanıcının ana hedefidir.



Journey hesaplamalarında kullanılır.



\---



\# 6. Exam Pack



Her sınav kendi öğrenme yapısına sahiptir.



Örnek:



\- YKS

\- KPSS Lisans

\- KPSS Önlisans

\- KPSS Ortaöğretim

\- ALES

\- YDS



\---



\# 7. Subject Yapısı



Exam seçildiğinde yalnızca o sınava ait Subject ve Topic yapısı döner.



\---



\# 8. Authentication



Tüm endpointler JWT Authentication gerektirir.



\---



\# 9. Yetkilendirme



Kullanıcı yalnızca kendi sınav tercihlerini değiştirebilir.



\---



\# 10. Hata Kodları



\- 400 Bad Request

\- 401 Unauthorized

\- 403 Forbidden

\- 404 Not Found



\---



\# 11. Tasarım Kuralları



\- Exam kullanıcı tarafından oluşturulamaz.

\- Exam Pack sistem tarafından yönetilir.

\- Active Exam değişebilir.

\- Primary Exam yalnızca gerekli durumlarda değiştirilir.



\---



\# Sonuç



Exam API, StudyOS'un tüm öğrenme deneyiminin başlangıç noktasıdır.

```

