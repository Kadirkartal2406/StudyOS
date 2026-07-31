\# StudyOS — Today API



\*\*Belge Durumu:\*\* Resmi — SSOT

\*\*Sürüm:\*\* 2.0

\*\*Tarih:\*\* 2026-07-30

\*\*Üst Belge:\*\* api-overview.md



\---



\# 1. Amaç



Today API, StudyOS'un ana giriş noktasıdır.



Kullanıcı uygulamayı açtığında yalnızca Today Engine ile etkileşime girer.



\---



\# 2. Sorumluluklar



\- Next Action üretmek

\- Günlük ilerlemeyi döndürmek

\- Kalan çalışma bloklarını hesaplamak

\- Günlük özet oluşturmak



\---



\# 3. Endpointler



GET /api/v1/today



GET /api/v1/today/next-action



GET /api/v1/today/progress



GET /api/v1/today/blocks



POST /api/v1/today/complete



POST /api/v1/today/skip



\---



\# 4. Next Action



Today Engine her zaman yalnızca bir adet Next Action üretir.



Örnek:



\- Matematik → Problemler

\- Tarih → Osmanlı Kuruluş

\- Revision

\- Deneme Analizi



\---



\# 5. Günlük İlerleme



Today API;



\- tamamlanan blok

\- toplam blok

\- tamamlanan süre

\- kalan süre



bilgilerini döndürür.



\---



\# 6. Complete



Bir çalışma tamamlandığında Today Engine yeni Next Action üretir.



\---



\# 7. Skip



Skip işlemi doğrudan planı değiştirmez.



Rule Engine bu davranışı Observation olarak kaydeder.



\---



\# 8. Authentication



JWT gerektirir.



\---



\# 9. Yetkilendirme



Kullanıcı yalnızca kendi Today verisini görebilir.



\---



\# 10. Hata Kodları



\- 400 Bad Request

\- 401 Unauthorized

\- 403 Forbidden



\---



\# 11. Tasarım Kuralları



\- Dashboard = Today

\- Aynı anda yalnızca bir Next Action vardır.

\- Kullanıcı görev oluşturmaz.

\- Kullanıcı plan yönetmez.

\- Today yalnızca sistem tarafından üretilir.



\---



\# 12. LOS Uyumu



Today;



Sense → Decide → Project



zincirinin kullanıcıya görünen son katmanıdır.



\---



\# Sonuç



Today API, StudyOS'un günlük çalışma deneyimini yöneten ana servisidir.s

