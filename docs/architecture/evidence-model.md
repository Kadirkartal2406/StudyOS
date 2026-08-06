\# StudyOS — Evidence Model



\*\*Belge Durumu:\*\* Resmi — SSOT

\*\*Sürüm:\*\* 2.0

\*\*Tarih:\*\* 2026-07-30

\*\*Üst Belge:\*\* domain-model.md

\*\*Bağlı Belgeler:\*\*

\- observation-engine.md

\- confidence-engine.md

\- rule-engine.md



\---



\# 1. Amaç



Evidence Model, StudyOS içerisinde kullanılan tüm öğrenme kanıtlarını tanımlar.



Evidence sistemin tek gerçek veri kaynağıdır.



\---



\# 2. Evidence Nedir?



Evidence;



öğrencinin gerçekleştirdiği doğrulanabilir bir öğrenme davranışıdır.



\---



\# 3. Temel Özellikler



Her Evidence;



\- immutable'dır

\- zaman damgasına sahiptir

\- Topic'e bağlıdır

\- kullanıcıya aittir

\- Observation Engine tarafından oluşturulur



\---



\# 4. Evidence Türleri



StudyOS aşağıdaki Evidence türlerini destekler.



\- Study Evidence

\- Question Evidence

\- Revision Evidence

\- Exam Evidence

\- Resource Evidence

\- AI Activity Evidence

\- Session Evidence



\---



\# 5. Study Evidence



Bir çalışma oturumunu temsil eder.



Örnek bilgiler



\- süre

\- Topic

\- başlangıç

\- bitiş



\---



\# 6. Question Evidence



Çözülen soruların sonucudur.



İçerebilir



\- doğru

\- yanlış

\- boş

\- süre

\- zorluk



\---



\# 7. Revision Evidence



Tamamlanan tekrar oturumudur.



İçerebilir



\- sonuç

\- tekrar süresi

\- başarı durumu



\---



\# 8. Exam Evidence



Deneme veya sınav sonuçlarını temsil eder.



İçerebilir



\- net

\- puan

\- Topic bazlı performans



\---



\# 9. Resource Evidence



Kaynak kullanımını temsil eder.



Örnek



\- PDF okundu

\- Video izlendi

\- NotebookLM kullanıldı



\---



\# 10. AI Activity Evidence



AI destekli öğrenme aktivitelerini temsil eder.



Örnek



\- Quiz üretildi

\- Explain kullanıldı

\- Özet oluşturuldu



\---



\# 11. Evidence Yaşam Döngüsü



User Action



↓



Observation Engine



↓



Evidence



↓



Confidence Engine



↓



Rule Engine



\---



\# 12. Evidence Kuralları



\- Evidence silinmez.

\- Evidence değiştirilmez.

\- Yeni davranış yeni Evidence üretir.

\- Rule Engine yalnızca Evidence kullanır.



\---



\# 13. Evidence Kullanımı



Evidence;



\- Confidence hesaplamak

\- Learning Memory oluşturmak

\- Today üretmek

\- Living Plan güncellemek



amacıyla kullanılır.



\---



\# 14. Tasarım İlkeleri



\- Evidence sistemin tek gerçek veri kaynağıdır.

\- Her öğrenme davranışı kayıt altına alınır.

\- Evidence yorum içermez.

\- Evidence karar içermez.



\---



\# Sonuç



StudyOS'un bütün öğrenme sistemi Evidence üzerine kuruludur.



Evidence olmadan Confidence oluşmaz.



Confidence olmadan Rule Engine çalışmaz.

