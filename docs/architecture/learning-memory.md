\# StudyOS — Learning Memory



\*\*Belge Durumu:\*\* Resmi — SSOT

\*\*Sürüm:\*\* 2.0

\*\*Tarih:\*\* 2026-07-30

\*\*Üst Belge:\*\* system-architecture.md

\*\*Bağlı Belgeler:\*\*

\- observation-engine.md

\- confidence-engine.md

\- living-plan.md

\- rule-engine.md



\---



\# 1. Amaç



Learning Memory, öğrencinin uzun vadeli öğrenme davranışlarını saklayan sistem bileşenidir.



Bilgi ezberlemez.



Davranış öğrenir.



\---



\# 2. Temel Görev



Learning Memory;



\- öğrenme alışkanlıklarını saklar

\- davranış örüntülerini çıkarır

\- Rule Engine'e sinyal sağlar



\---



\# 3. Saklanan Bilgiler



Örnek bilgiler



\- en verimli çalışma saatleri

\- ortalama odak süresi

\- mola alışkanlığı

\- tekrar eğilimi

\- konu tamamlama davranışı

\- çalışma sıklığı



\---



\# 4. Saklanmayan Bilgiler



Learning Memory;



\- sohbet geçmişi

\- promptlar

\- kullanıcı notları

\- rastgele bilgiler



saklamaz.



\---



\# 5. Veri Kaynağı



Learning Memory yalnızca Observation Engine tarafından üretilen Evidence verilerini kullanır.



\---



\# 6. Güncellenme



Learning Memory sürekli gelişir.



Yeni davranış geldikçe model güncellenebilir.



\---



\# 7. Rule Engine İlişkisi



Rule Engine;



karar üretirken Learning Memory'den yararlanır.



\---



\# 8. Living Plan İlişkisi



Living Plan;



öğrencinin alışkanlıklarına göre adapte edilir.



Bu adaptasyonun temel girdilerinden biri Learning Memory'dir.



\---



\# 9. Kullanıcı Etkileşimi



Learning Memory kullanıcı tarafından yönetilemez.



CRUD ekranı bulunmaz.



\---



\# 10. Gizlilik



Learning Memory;



yalnızca öğrenme deneyimini geliştirmek amacıyla kullanılır.



Kişisel davranış modeli kullanıcıya aittir.



\---



\# 11. Tasarım Kuralları



\- Learning Memory karar üretmez.

\- Learning Memory davranış öğrenir.

\- Evidence olmadan Learning Memory oluşmaz.

\- Kullanıcı manuel olarak değiştiremez.



\---



\# 12. Yaşam Döngüsü



Evidence



↓



Learning Memory



↓



Rule Engine



↓



Living Plan



↓



Today



\---



\# Sonuç



Learning Memory, StudyOS'un öğrenciyi zamanla tanımasını sağlayan davranış hafızasıdır.



Sistem kişiyi değil, öğrenme biçimini öğrenir.

