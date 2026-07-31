\# StudyOS — API Overview



\*\*Belge Durumu:\*\* Resmi — SSOT

\*\*Sürüm:\*\* 2.0

\*\*Tarih:\*\* 2026-07-30

\*\*Üst Belge:\*\* system-architecture.md



\---



\# 1. Amaç



Bu belge, StudyOS API mimarisinin genel yapısını tanımlar.



API, frontend ile backend arasındaki tek resmi iletişim katmanıdır.



\---



\# 2. Temel İlkeler



StudyOS API;



\- REST tabanlıdır.

\- JSON kullanır.

\- Stateless çalışır.

\- Versioned API yaklaşımını benimser.



\---



\# 3. API Yapısı



API aşağıdaki ana alanlardan oluşur.



\- Authentication

\- User

\- Exam

\- Subject

\- Topic

\- Today

\- Journey

\- Study

\- Question

\- Revision

\- Exam Result

\- Resource

\- AI

\- Settings



\---



\# 4. API Versiyonlama



Tüm endpointler versiyon numarası içerir.



Örnek



/api/v1/...



\---



\# 5. Kimlik Doğrulama



Kimlik doğrulama JWT Access Token üzerinden yapılır.



Yetkisiz istekler reddedilir.



\---



\# 6. Veri Formatı



Tüm istekler ve cevaplar JSON formatındadır.



\---



\# 7. Başarılı Cevap



Başarılı istekler uygun HTTP Status Code ile döner.



Örnek



\- 200 OK

\- 201 Created

\- 204 No Content



\---



\# 8. Hata Cevapları



Standart hata kodları kullanılır.



Örnek



\- 400 Bad Request

\- 401 Unauthorized

\- 403 Forbidden

\- 404 Not Found

\- 409 Conflict

\- 422 Validation Error

\- 500 Internal Server Error



\---



\# 9. API Tasarım İlkeleri



\- Endpoint isimleri tutarlı olmalıdır.

\- Resource tabanlı tasarım tercih edilir.

\- İş mantığı endpoint'e değil servis katmanına aittir.

\- Response yapıları standart olmalıdır.



\---



\# 10. Rule Engine



Frontend hiçbir zaman Rule Engine'i doğrudan çağırmaz.



Rule Engine yalnızca backend içerisinde çalışır.



\---



\# 11. AI Servisleri



LLM servisleri doğrudan istemciye açılmaz.



Tüm AI işlemleri backend üzerinden gerçekleştirilir.



\---



\# 12. Güvenlik



API;



\- JWT Authentication

\- HTTPS

\- Rate Limiting

\- Input Validation



kullanır.



\---



\# Sonuç



StudyOS API, frontend ile backend arasındaki tek resmi iletişim katmanıdır.



Tüm istemciler aynı API sözleşmesini kullanır.

