\# StudyOS — Confidence Engine



\*\*Belge Durumu:\*\* Resmi — SSOT

\*\*Sürüm:\*\* 2.0

\*\*Tarih:\*\* 2026-07-30

\*\*Üst Belge:\*\* system-architecture.md

\*\*Bağlı Belgeler:\*\*

\- observation-engine.md

\- rule-engine.md

\- evidence-model.md



\---



\# 1. Amaç



Confidence Engine, toplanan Evidence verilerini analiz ederek öğrencinin bir Topic üzerindeki öğrenme güvenini hesaplar.



Karar üretmez.



\---



\# 2. Temel Görev



Confidence Engine;



\- Evidence okur

\- Trend analiz eder

\- Öğrenme güvenini hesaplar

\- Confidence oluşturur



\---



\# 3. Girdiler



Confidence Engine aşağıdaki verileri kullanır.



\- Study Evidence

\- Question Evidence

\- Revision Evidence

\- Exam Evidence

\- Session History

\- Time History



\---



\# 4. Çıktı



Confidence Engine yalnızca Confidence üretir.



Rule üretmez.



Today oluşturmaz.



\---



\# 5. Confidence Nedir?



Confidence;



öğrencinin bir konuyu gerçekten öğrenmiş olma olasılığını temsil eder.



Başarı oranı değildir.



\---



\# 6. Confidence Hesabında Kullanılan Faktörler



Confidence hesaplanırken;



\- doğruluk

\- tekrar başarısı

\- çalışma süresi

\- unutma eğrisi

\- son çalışma tarihi

\- soru çeşitliliği

\- trend

\- veri miktarı



birlikte değerlendirilir.



\---



\# 7. Confidence Özellikleri



Confidence;



\- sürekli güncellenir

\- tek olaydan etkilenmez

\- geçmişi dikkate alır

\- Topic bazında hesaplanır



\---



\# 8. Confidence Seviyeleri



Confidence sistem içinde sayısal olarak tutulur.



Arayüzde gerekirse aşağıdaki seviyelere çevrilebilir.



\- Very Low

\- Low

\- Medium

\- High

\- Mastered



\---



\# 9. Confidence ve Rule Engine



Confidence Engine karar vermez.



Confidence yalnızca Rule Engine'e giriş sağlar.



\---



\# 10. Confidence ve Observation



Observation Engine



↓



Evidence



↓



Confidence Engine



↓



Confidence



şeklinde çalışır.



\---



\# 11. Confidence Güncelleme



Yeni Evidence oluştuğunda ilgili Topic yeniden hesaplanabilir.



Eski Confidence silinmez.



Yeni değer oluşturulur.



\---



\# 12. Tasarım Kuralları



\- Confidence yalnızca Evidence'dan hesaplanır.

\- Kullanıcı Confidence değiştiremez.

\- LLM Confidence hesaplayamaz.

\- Confidence tek başına karar oluşturmaz.



\---



\# Sonuç



Confidence Engine, öğrencinin öğrenme seviyesini ölçen analiz katmanıdır.



Karar üretmez.



Yalnızca Rule Engine'in doğru karar verebilmesi için güvenilir bir sinyal oluşturur.

