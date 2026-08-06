\# StudyOS — Rule Engine



\*\*Belge Durumu:\*\* Resmi — SSOT

\*\*Sürüm:\*\* 2.0

\*\*Tarih:\*\* 2026-07-30

\*\*Üst Belge:\*\* system-architecture.md

\*\*Bağlı Belgeler:\*\*

\- observation-engine.md

\- confidence-engine.md

\- today-engine.md

\- living-plan.md



\---



\# 1. Amaç



Rule Engine, StudyOS'un deterministik karar motorudur.



Sistemde alınan bütün öğrenme kararları yalnızca Rule Engine tarafından üretilir.



\---



\# 2. Temel Görev



Rule Engine;



\- Evidence okur

\- Confidence değerlendirir

\- Learning Memory kullanır

\- Living Plan günceller

\- Today oluşturulmasını tetikler



\---



\# 3. Girdiler



Rule Engine aşağıdaki verileri kullanır.



\- Evidence

\- Confidence

\- Journey

\- Study History

\- Revision History

\- Learning Memory

\- Active Exam



\---



\# 4. Çıktılar



Rule Engine yalnızca karar üretir.



Örnek çıktılar



\- Review Required

\- Continue Learning

\- Mastered

\- Increase Priority

\- Decrease Priority

\- Create Today Action

\- Update Living Plan



\---



\# 5. Karar Prensibi



Tek bir olay hiçbir zaman karar oluşturmaz.



Kararlar yalnızca yeterli veri oluştuğunda verilir.



\---



\# 6. Değerlendirilen Faktörler



Rule Engine;



\- doğruluk

\- süre

\- tekrar geçmişi

\- çalışma sıklığı

\- trend

\- confidence

\- unutma riski



gibi sinyalleri birlikte değerlendirir.



\---



\# 7. Rule Önceliği



Öncelik sırası



1\. Kritik tekrar

2\. Zayıf Topic

3\. Devam eden çalışma

4\. Yeni Topic

5\. İleri seviye geliştirme



\---



\# 8. Rule Engine Yetkileri



Rule Engine;



\- Today oluşturabilir

\- Living Plan güncelleyebilir

\- Revision oluşturabilir

\- Priority değiştirebilir



\---



\# 9. Rule Engine'in Yetkisi Olmayan İşler



Rule Engine;



\- açıklama yazmaz

\- AI sohbeti yapmaz

\- konu anlatmaz

\- içerik üretmez



\---



\# 10. LLM ile İlişki



Rule Engine karar verir.



LLM yalnızca kararı açıklar.



Örnek



Rule Engine



> Bu Topic tekrar edilmeli.



LLM



> Son çalışmalarında başarı oranın düştüğü için bu konuyu tekrar etmeni öneriyorum.



\---



\# 11. Karar Özellikleri



Kararlar



\- deterministik

\- tekrarlanabilir

\- açıklanabilir

\- test edilebilir



olmalıdır.



\---



\# 12. Güncelleme Politikası



Yeni Evidence geldikçe Rule Engine yeniden çalışabilir.



Ancak gereksiz hesaplama yapılmaz.



\---



\# 13. Tasarım Kuralları



\- Rule Engine tek karar merkezidir.

\- LLM hiçbir zaman Rule Engine yerine geçmez.

\- Kullanıcı karar üretmez.

\- Kararlar Explain katmanından bağımsızdır.



\---



\# Sonuç



StudyOS'un bütün öğrenme kararları Rule Engine tarafından üretilir.



Sistem davranışının tek otoritesi Rule Engine'dir.

