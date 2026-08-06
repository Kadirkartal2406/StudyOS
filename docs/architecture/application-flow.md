\# StudyOS — Application Flow



\*\*Belge Durumu:\*\* Resmi — SSOT

\*\*Sürüm:\*\* 2.0

\*\*Tarih:\*\* 2026-07-30

\*\*Üst Belge:\*\* system-architecture.md



\---



\# 1. Amaç



Bu belge, StudyOS içerisindeki veri akışını tanımlar.



Sistemin hangi sırayla çalıştığını gösterir.



\---



\# 2. Genel Akış



User Action



↓



Observation Engine



↓



Evidence



↓



Confidence Engine



↓



Learning Memory



↓



Rule Engine



↓



Living Plan



↓



Today Engine



↓



User Interface



\---



\# 3. Kullanıcı Etkileşimi



Kullanıcı yalnızca;



\- çalışır

\- soru çözer

\- tekrar yapar

\- kaynak ekler

\- AI kullanır



\---



\# 4. Observation



Her kullanıcı davranışı Observation Engine tarafından yakalanır.



Observation yeni bir Evidence oluşturur.



\---



\# 5. Evidence



Evidence sistemin tek gerçek veri kaynağıdır.



Tüm kararlar buradan beslenir.



\---



\# 6. Confidence



Confidence Engine Evidence verilerini analiz eder.



Topic bazında güven hesaplar.



\---



\# 7. Learning Memory



Confidence ve davranış geçmişi Learning Memory'yi günceller.



\---



\# 8. Rule Engine



Rule Engine;



\- Today'i belirler

\- Living Plan'ı günceller

\- öncelikleri hesaplar



\---



\# 9. Living Plan



Living Plan sürekli yaşayan çalışma planıdır.



Bugünkü planın kaynağıdır.



\---



\# 10. Today Engine



Today Engine;



Living Plan'dan yalnızca bugünkü çalışmayı üretir.



\---



\# 11. Kullanıcıya Gösterilen



Arayüzde yalnızca;



\- Next Action

\- Daily Progress

\- Remaining Blocks

\- Short Journey Summary



gösterilir.



\---



\# 12. Geri Besleme Döngüsü



Today



↓



Study



↓



Observation



↓



Evidence



↓



Confidence



↓



Rule



↓



Today



Bu döngü sürekli devam eder.



\---



\# 13. Tasarım Kuralları



\- Kullanıcı karar vermez.

\- Sistem sürekli öğrenir.

\- Her yeni davranış sistemi geliştirir.

\- Veri akışı tek yönlüdür.



\---



\# Sonuç



StudyOS'un bütün ekranları ve modülleri bu veri akışı üzerine kuruludur.



Tüm sistem aynı öğrenme döngüsünü takip eder.

