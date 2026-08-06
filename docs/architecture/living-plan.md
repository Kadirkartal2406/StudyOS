\# StudyOS — Living Plan



\*\*Belge Durumu:\*\* Resmi — SSOT

\*\*Sürüm:\*\* 2.0

\*\*Tarih:\*\* 2026-07-30

\*\*Üst Belge:\*\* system-architecture.md

\*\*Bağlı Belgeler:\*\*

\- observation-engine.md

\- confidence-engine.md

\- today-engine.md

\- rule-engine.md



\---



\# 1. Amaç



Living Plan, öğrencinin zamanla değişen çalışma planıdır.



Statik değildir.



\---



\# 2. Temel Görev



Living Plan;



\- öğrenciyi gözlemler

\- öneriler oluşturur

\- kabul edilen planı uygular

\- zamanla adapte olur



\---



\# 3. Living Plan Döngüsü



Observation



↓



Evidence



↓



Confidence



↓



Rule Engine



↓



Suggestion



↓



Accept



↓



Living Plan



↓



Today



\---



\# 4. İlk Gün



İlk kullanımda sistem;



\- öğrenciyi tanır

\- mevcut alışkanlıklarını öğrenir

\- gerekirse başlangıç planı önerir



\---



\# 5. Adaptasyon



Living Plan;



\- her gün yeniden yazılmaz

\- zaman içinde küçük değişikliklerle gelişir



\---



\# 6. Kullanıcı Rolü



Kullanıcı;



\- plan oluşturmaz

\- blok eklemez

\- sıralama yapmaz



Yalnızca öneriyi kabul eder veya reddeder.



\---



\# 7. Güncellenme Sebepleri



Living Plan;



\- yeni Observation

\- Confidence değişimi

\- Exam değişimi

\- Available Time değişimi



sonrasında güncellenebilir.



\---



\# 8. Rule Engine İlişkisi



Rule Engine;



Living Plan üzerinde değişiklik önerir.



Living Plan bu önerileri uygular.



\---



\# 9. Today İlişkisi



Today Engine;



Living Plan'ın yalnızca bugünkü bölümünü kullanıcıya gösterir.



\---



\# 10. Tasarım Kuralları



\- Living Plan kullanıcı tarafından yönetilmez.

\- Plan sürekli yaşayan bir yapıdır.

\- Ani değişikliklerden kaçınılır.

\- Küçük ve güvenli adaptasyonlar tercih edilir.



\---



\# 11. Yasaklar



Living Plan;



\- tek yanlışla değişmez

\- tek doğruyla değişmez

\- anlık duyguya göre değişmez



Yeterli kanıt oluşmadan adapte olmaz.



\---



\# Sonuç



Living Plan, StudyOS'un öğrenciyi zamanla tanıyan ve gelişen çalışma planıdır.



Plan yaşayan bir sistemdir; kullanıcı tarafından yönetilen bir takvim değildir.

