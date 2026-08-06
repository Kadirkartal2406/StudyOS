\# StudyOS — Authentication API



\*\*Belge Durumu:\*\* Resmi — SSOT

\*\*Sürüm:\*\* 2.0

\*\*Tarih:\*\* 2026-07-30

\*\*Üst Belge:\*\* api-overview.md



\---



\# 1. Amaç



Authentication API, kullanıcı kimlik doğrulama ve oturum yönetimini sağlar.



\---



\# 2. Sorumluluklar



\- Kayıt olma

\- Giriş yapma

\- Çıkış yapma

\- Access Token üretme

\- Refresh Token yenileme

\- Şifre değiştirme

\- Şifre sıfırlama



\---



\# 3. Endpointler



POST /api/v1/auth/register



POST /api/v1/auth/login



POST /api/v1/auth/logout



POST /api/v1/auth/refresh



POST /api/v1/auth/change-password



POST /api/v1/auth/forgot-password



POST /api/v1/auth/reset-password



GET /api/v1/auth/me



\---



\# 4. Authentication



Tüm korunan endpointler



Authorization: Bearer <access\_token>



başlığı ile çalışır.



\---



\# 5. Access Token



\- JWT kullanılır.

\- Kısa ömürlüdür.

\- API erişimi sağlar.



\---



\# 6. Refresh Token



\- Daha uzun ömürlüdür.

\- Yeni Access Token üretmek için kullanılır.



\---



\# 7. Login Akışı



Kullanıcı



↓



Email + Password



↓



JWT Access Token



↓



Refresh Token



↓



Authenticated Session



\---



\# 8. Logout



Logout işlemi sonrasında;



\- Refresh Token geçersiz hale gelir.

\- Kullanıcı yeniden giriş yapmak zorundadır.



\---



\# 9. Güvenlik



\- HTTPS zorunludur.

\- Şifreler hashlenerek saklanır.

\- JWT imzalanır.

\- Rate limiting uygulanır.



\---



\# 10. Hata Kodları



\- 400 Bad Request

\- 401 Unauthorized

\- 403 Forbidden

\- 404 Not Found

\- 422 Validation Error



\---



\# 11. Tasarım Kuralları



\- JWT dışında kimlik doğrulama kullanılmaz.

\- Session backend'de tutulmaz.

\- Stateless mimari korunur.



\---



\# Sonuç



Authentication API, StudyOS içerisindeki tüm güvenli erişimin giriş noktasıdır.

