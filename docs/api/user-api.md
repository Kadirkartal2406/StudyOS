\# StudyOS — User API



\*\*Belge Durumu:\*\* Resmi — SSOT

\*\*Sürüm:\*\* 2.0

\*\*Tarih:\*\* 2026-07-30

\*\*Üst Belge:\*\* api-overview.md



\---



\# 1. Amaç



User API, kullanıcı profilinin ve kişisel ayarlarının yönetilmesini sağlar.



\---



\# 2. Sorumluluklar



\- Profil bilgilerini görüntüleme

\- Profil güncelleme

\- Avatar yönetimi

\- Timezone

\- Language

\- Notification tercihleri

\- Account ayarları



\---



\# 3. Endpointler



GET /api/v1/users/me



PATCH /api/v1/users/me



DELETE /api/v1/users/me



GET /api/v1/users/settings



PATCH /api/v1/users/settings



\---



\# 4. Profil Bilgileri



Kullanıcı profili;



\- ad

\- soyad

\- e-posta

\- avatar

\- ülke

\- saat dilimi

\- dil



bilgilerini içerir.



\---



\# 5. Kullanıcı Ayarları



Settings;



\- notification

\- reminder

\- theme

\- language

\- timezone



alanlarından oluşur.



\---



\# 6. Hesap Silme



DELETE isteği kullanıcı hesabını kalıcı olarak silmez.



Hesap önce pasif duruma alınır.



\---



\# 7. Authentication



Tüm endpointler JWT gerektirir.



\---



\# 8. Yetkilendirme



Kullanıcı yalnızca kendi hesabını yönetebilir.



Başka kullanıcıların bilgilerine erişemez.



\---



\# 9. Güvenlik



\- JWT Authentication

\- Input Validation

\- Authorization Control



zorunludur.



\---



\# 10. Hata Kodları



\- 400 Bad Request

\- 401 Unauthorized

\- 403 Forbidden

\- 404 Not Found

\- 422 Validation Error



\---



\# 11. Tasarım Kuralları



\- Profil ile öğrenme verileri ayrıdır.

\- Learning Memory bu API üzerinden yönetilmez.

\- Sistem davranışları kullanıcı tarafından değiştirilemez.



\---



\# Sonuç



User API yalnızca kullanıcı hesabı ve kişisel ayarların yönetiminden sorumludur.

