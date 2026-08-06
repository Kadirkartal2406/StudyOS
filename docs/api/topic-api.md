\# StudyOS — Topic API



\*\*Belge Durumu:\*\* Resmi — SSOT

\*\*Sürüm:\*\* 2.0

\*\*Tarih:\*\* 2026-07-30

\*\*Üst Belge:\*\* api-overview.md



\---



\# 1. Amaç



Topic API, StudyOS'un temel öğrenme birimi olan Topic Work Surface'i yönetir.



Topic yalnızca bilgi gösteren bir sayfa değildir.



Topic, öğrencinin çalıştığı aktif çalışma yüzeyidir.



\---



\# 2. Sorumluluklar



\- Topic listeleme

\- Topic detayını getirme

\- Topic Work Surface oluşturma

\- Topic istatistiklerini döndürme

\- Topic Confidence bilgisini sağlama



\---



\# 3. Endpointler



GET /api/v1/topics



GET /api/v1/topics/{topic\_code}



GET /api/v1/topics/{topic\_code}/workspace



GET /api/v1/topics/{topic\_code}/summary



GET /api/v1/topics/{topic\_code}/confidence



\---



\# 4. Topic Yapısı



Her Topic;



\- topic\_code

\- subject\_code

\- exam\_code

\- title

\- description

\- difficulty

\- estimated\_duration



alanlarına sahiptir.



\---



\# 5. Work Surface



Topic Work Surface içerisinde;



\- Today Action

\- Study Session

\- Pomodoro

\- NotebookLM

\- AI Explain

\- Resource

\- Question Result

\- Revision

\- Confidence



görünür.



\---



\# 6. Confidence



Confidence değeri kullanıcı tarafından değiştirilmez.



Rule Engine tarafından hesaplanır.



\---



\# 7. Authentication



JWT gerektirir.



\---



\# 8. Yetkilendirme



Kullanıcı yalnızca kendi çalışma verilerine erişebilir.



\---



\# 9. Hata Kodları



\- 400 Bad Request

\- 401 Unauthorized

\- 403 Forbidden

\- 404 Topic Not Found



\---



\# 10. Tasarım Kuralları



\- Topic öğrenme birimidir.

\- Subject yalnızca kapsayıcıdır.

\- Evidence Topic altında toplanır.

\- Free-text topic kullanılmaz.

\- Tüm aktiviteler topic\_code ile ilişkilidir.



\---



\# 11. LOS Uyumu



Topic;



Sense → Evidence → Confidence → Decide → Explain



zincirinin merkezidir.



\---



\# Sonuç



Topic API, StudyOS'un en önemli API'lerinden biridir ve tüm öğrenme davranışı Topic Work Surface etrafında şekillenir.

