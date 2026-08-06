\# StudyOS — Observation Engine



\*\*Belge Durumu:\*\* Resmi — SSOT

\*\*Sürüm:\*\* 2.0

\*\*Tarih:\*\* 2026-07-30

\*\*Üst Belge:\*\* system-architecture.md

\*\*Bağlı Belgeler:\*\*

\- confidence-engine.md

\- domain-model.md

\- evidence-model.md



\---



\# 1. Amaç



Observation Engine, öğrencinin yaptığı her davranışı gözlemleyen sistemdir.



StudyOS'un ilk öğrenme katmanıdır.



\---



\# 2. Temel Görev



Observation Engine;



\- kullanıcı davranışlarını toplar

\- bunları standart hale getirir

\- Evidence üretir



Karar vermez.



\---



\# 3. Girdiler



Observation Engine aşağıdaki olayları dinler.



\- Study Session

\- Question Result

\- Revision Result

\- Exam Result

\- Resource Usage

\- NotebookLM Activity

\- Topic Visit

\- Session Duration



\---



\# 4. Çıktı



Observation Engine yalnızca Evidence üretir.



Başka hiçbir çıktı üretmez.



\---



\# 5. Observation Prensibi



Sistem kullanıcıyı izlemez.



Sistem öğrenme davranışlarını gözlemler.



Amaç;



öğrenciyi değerlendirmek değil,



öğrenme modelini oluşturmaktır.



\---



\# 6. Evidence Oluşturma



Her kullanıcı davranışı yeni bir Evidence üretir.



Evidence değiştirilmez.



Silinmez.



Yeni veri yeni Evidence oluşturur.



\---



\# 7. Observation Kuralları



Observation Engine;



\- yorum yapmaz

\- puan vermez

\- confidence hesaplamaz

\- karar üretmez



\---



\# 8. Observation Kalitesi



Observation verileri;



\- tutarlı

\- zaman damgalı

\- doğrulanabilir



olmalıdır.



\---



\# 9. Observation ve Confidence



Observation Engine



↓



Evidence



↓



Confidence Engine



şeklinde çalışır.



Observation Engine doğrudan Confidence üretmez.



\---



\# 10. Observation ve Rule Engine



Observation Engine Rule Engine'i çağırmaz.



Yeni Evidence oluştuğunda sistem gerekli olduğunda Rule Engine'i tetikler.



\---



\# 11. Desteklenen Evidence Türleri



\- Study Evidence

\- Question Evidence

\- Revision Evidence

\- Exam Evidence

\- Resource Evidence

\- AI Activity Evidence



\---



\# 12. Tasarım Kuralları



\- Her davranış tek bir Evidence üretir.

\- Observation Engine deterministiktir.

\- Observation Engine veri kaybetmez.

\- Observation Engine karar içermez.

\- Observation Engine LLM kullanmaz.



\---



\# Sonuç



Observation Engine, StudyOS'un duyularıdır.



Sistem önce gözlemler.



Daha sonra Confidence Engine değerlendirir.



En son Rule Engine karar verir.

