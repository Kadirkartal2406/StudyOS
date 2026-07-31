\# StudyOS — AI Architecture



\*\*Belge Durumu:\*\* Resmi — SSOT

\*\*Sürüm:\*\* 2.0

\*\*Tarih:\*\* 2026-07-30

\*\*Üst Belge:\*\* system-architecture.md

\*\*Bağlı Belgeler:\*\*

\- rule-engine.md

\- learning-memory.md

\- design-principles.md



\---



\# 1. Amaç



AI Architecture, StudyOS içerisinde yapay zekanın hangi görevleri yapacağını ve hangi görevleri yapmayacağını tanımlar.



\---



\# 2. Temel İlke



Rule Engine karar verir.



LLM yalnızca açıklar.



\---



\# 3. AI Katmanları



StudyOS iki farklı AI katmanına sahiptir.



\- Rule Engine

\- LLM Layer



\---



\# 4. Rule Engine



Rule Engine;



\- karar üretir

\- öncelik belirler

\- Today oluşturulmasını sağlar

\- Living Plan'ı günceller



\---



\# 5. LLM Layer



LLM;



\- açıklar

\- özet çıkarır

\- soru üretir

\- quiz oluşturur

\- anlatım yapar



Karar üretmez.



\---



\# 6. Prompt Yönetimi



Promptlar kullanıcı tarafından yazılmaz.



Sistem;



\- intent

\- Topic

\- bağlam

\- kullanıcı isteği



bilgilerinden prompt oluşturur.



\---



\# 7. Intent Sistemi



Kullanıcı örnek olarak;



\- Açıkla

\- Özetle

\- Quiz oluştur

\- Flashcard üret

\- Örnek çöz

\- Daha basit anlat



gibi intent seçer.



\---



\# 8. AI Belleği



LLM uzun vadeli hafıza tutmaz.



Kalıcı öğrenme davranışı yalnızca Learning Memory içerisinde saklanır.



\---



\# 9. AI ve Confidence



LLM;



Confidence hesaplayamaz.



Confidence yalnızca Confidence Engine tarafından oluşturulur.



\---



\# 10. AI ve Rule Engine



LLM;



Rule Engine kararlarını değiştiremez.



Yalnızca nedenini açıklar.



\---



\# 11. Desteklenen AI Görevleri



\- Explain

\- Quiz Generation

\- Flashcard Generation

\- Resource Summarization

\- PDF Explanation

\- NotebookLM Integration



\---



\# 12. Yasaklanan Görevler



LLM;



\- çalışma planı oluşturamaz

\- Goal belirleyemez

\- Revision planlayamaz

\- Confidence hesaplayamaz

\- Today oluşturamaz



\---



\# 13. Tasarım Kuralları



\- AI kullanıcı yerine karar vermez.

\- AI sistem kurallarını değiştirmez.

\- Promptlar sistem tarafından oluşturulur.

\- LLM yalnızca yardımcı katmandır.



\---



\# Sonuç



StudyOS'ta yapay zeka, öğrenmeyi kolaylaştırır.



Öğrenme kararlarını ise her zaman sistemin Rule Engine katmanı verir.

