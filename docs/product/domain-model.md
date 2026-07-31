\# StudyOS — Domain Model



\*\*Belge Durumu:\*\* Resmi — Single Source of Truth (SSOT)

\*\*Sürüm:\*\* 2.0

\*\*Tarih:\*\* 2026-07-30

\*\*Üst Belge:\*\* learning-operating-system.md

\*\*Bağlı Belgeler:\*\*

\- database-schema.md

\- api-contract.md

\- rule-engine.md

\- confidence-engine.md



\---



\# 1. Amaç



Bu belge StudyOS'un ortak domain dilini tanımlar.



Her entity, servis, API ve veritabanı bu modele göre geliştirilir.



\---



\# 2. Domain Hiyerarşisi



```

User



↓



Journey



↓



Exam



↓



Subject



↓



Topic



↓



Evidence



↓



Confidence



↓



Decision



↓



Today



↓



Study Session

```



\---



\# 3. User



StudyOS'u kullanan kişidir.



Sorumlulukları:



\- çalışmak

\- intent belirtmek

\- geri bildirim vermek



Kullanıcı;



\- Goal yönetmez

\- Plan oluşturmaz

\- Revision yönetmez

\- Resource organize etmez



\---



\# 4. Journey



Öğrencinin uzun dönem öğrenme yolculuğudur.



Journey;



\- hedef

\- ilerleme

\- öğrenme davranışı

\- geçmiş



bilgilerini temsil eder.



\---



\# 5. Exam



Öğrencinin hazırlandığı sınavdır.



Örnekler



\- YKS

\- KPSS

\- ALES

\- YDS



Bir Journey içerisinde yalnızca bir Active Exam bulunur.



\---



\# 6. Subject



Exam içerisindeki ana dersi temsil eder.



Örnek



\- Matematik

\- Fizik

\- Türkçe



Subject yalnızca kapsayıcıdır.



Kararlar Subject seviyesinde alınmaz.



\---



\# 7. Topic



StudyOS'un temel öğrenme birimidir.



Örnek



\- Fonksiyonlar

\- Limit

\- Hücre



Her Topic benzersiz bir topic\_code ile tanımlanır.



Tüm öğrenme aktiviteleri Topic'e bağlanır.



\---



\# 8. Evidence



Öğrencinin yaptığı her davranışın kaydıdır.



Örnekler



\- Study Session

\- Question Result

\- Revision

\- Exam Result

\- NotebookLM Activity

\- Resource Usage



Evidence değiştirilemez.



Yeni veri yeni Evidence üretir.



\---



\# 9. Confidence



Bir Topic'in öğrenilme güven seviyesidir.



Confidence;



\- 0–100 arası skor

\- sürekli güncellenen değer

\- Rule Engine girdisi



olarak kullanılır.



\---



\# 10. Decision



Rule Engine tarafından üretilen sistem kararıdır.



Örnekler



\- Review Required

\- Continue Learning

\- Mastered

\- Increase Priority

\- Decrease Priority



Decision kullanıcı tarafından değiştirilemez.



\---



\# 11. Today



Bugünkü çalışma projeksiyonudur.



Today;



\- Next Action

\- çalışma blokları

\- günlük hedef



bilgilerini içerir.



Today her gün yeniden oluşturulur.



\---



\# 12. Study Session



Bir çalışma oturumunu temsil eder.



Study Session;



\- başlangıç zamanı

\- bitiş zamanı

\- süre

\- Topic

\- sonuç



bilgilerini içerir.



Her oturum yeni Evidence üretir.



\---



\# 13. Resource



Topic'e bağlı öğrenme materyalidir.



Örnekler



\- PDF

\- Video

\- Kitap

\- NotebookLM



Resource öğrenme birimi değildir.



\---



\# 14. Revision



Bir Topic için oluşturulan tekrar kaydıdır.



Revision;



\- Rule Engine tarafından üretilir

\- kullanıcı tarafından tamamlanır



Revision bir Evidence türüdür.



\---



\# 15. Question Result



Çözülen soru sonucudur.



İçerir



\- doğru

\- yanlış

\- boş

\- süre

\- zorluk



Question Result tek başına karar üretmez.



Confidence hesabına katkı sağlar.



\---



\# 16. Learning Memory



Öğrenci hakkında sistem tarafından öğrenilen davranış modelidir.



Örnek



\- sabah daha verimli

\- matematikte süre problemi

\- uzun pomodoro tercih ediyor



Learning Memory kullanıcı tarafından düzenlenmez.



\---



\# 17. Living Plan



Rule Engine tarafından sürekli güncellenen öğrenme planıdır.



Living Plan;



\- oluşturulmaz

\- adapte edilir



Today bu planın günlük görünümüdür.



\---



\# 18. Rule Engine



Sistemin deterministik karar motorudur.



Girdiler



\- Evidence

\- Confidence

\- Journey

\- Revision

\- Study History



Çıktılar



\- Decision

\- Today

\- Living Plan Update



\---



\# 19. LLM



StudyOS'ta yardımcı açıklama katmanıdır.



Görevleri



\- Explain

\- Summarize

\- Teach

\- Generate



LLM karar üretmez.



\---



\# 20. Domain Kuralları



\- Öğrenme birimi Topic'tir.

\- Evidence silinmez.

\- Confidence doğrudan değiştirilemez.

\- Decision yalnızca Rule Engine üretir.

\- Today her gün yeniden oluşturulur.

\- Living Plan sürekli adapte olur.

\- Subject yalnızca organizasyon katmanıdır.

\- LLM hiçbir zaman Rule Engine yerine geçmez.

```

