# StudyOS — Learning Operating System (LOS)

**Belge Durumu:** Resmi — Single Source of Truth (SSOT)
**Sürüm:** 2.0
**Tarih:** 2026-07-30
**Üst Belge:** product-vision.md
**Bağlı Belgeler:**
- design-principles.md
- domain-model.md
- rule-engine.md
- observation-engine.md
- confidence-engine.md
- today-engine.md
- living-plan.md

---

# 1. Learning Operating System Nedir?

Learning Operating System (LOS), StudyOS'un karar verme mekanizmasını tanımlayan çekirdek sistemdir.

LOS;

- öğrenciyi gözlemler,
- davranışını öğrenir,
- güven seviyesini hesaplar,
- karar üretir,
- çalışma yüzeyini oluşturur,
- her gün kendisini günceller.

LOS herhangi bir ekran değildir.

LOS uygulamanın görünmeyen işletim sistemidir.

---

# 2. Temel Amaç

LOS'un amacı öğrenciye araç sunmak değildir.

LOS'un amacı öğrencinin yerine karar vermektir.

Her gün yalnızca şu soruya cevap verir.

> Bugün öğrencinin yapması gereken en doğru çalışma nedir?

---

# 3. Learning Cycle

StudyOS aşağıdaki öğrenme döngüsü üzerine kuruludur.

Observe

↓

Collect Evidence

↓

Calculate Confidence

↓

Rule Engine Decision

↓

Today Projection

↓

Execute

↓

Observe Again

↓

Continuous Learning

Bu döngü hiçbir zaman durmaz.

---

# 4. Observe

LOS önce gözlemler.

Henüz hiçbir karar verilmez.

Observation yalnızca veri toplama aşamasıdır.

Örnek gözlemler

- Çalışılan Topic
- Pomodoro süresi
- Çalışma sıklığı
- Günün saati
- Soru doğruluk oranı
- Çalışma alışkanlığı
- Tekrar davranışı
- Deneme performansı
- Çalışma sürekliliği

Observation yorum yapmaz.

Sadece kayıt tutar.

---

# 5. Evidence

Observation sonucu oluşan her kayıt Evidence olarak adlandırılır.

Evidence;

öğrencinin gerçekten yaptığı davranışların kanıtıdır.

Örnek Evidence

- Topic üzerinde 45 dakika çalışma
- 20 soruda %80 başarı
- Revision tamamlandı
- Pomodoro yarıda bırakıldı
- NotebookLM Quiz tamamlandı

Evidence sistemin tek gerçek veri kaynağıdır.

---

# 6. Confidence

Evidence doğrudan karar üretmez.

Önce Confidence hesaplanır.

Confidence;

belirli bir Topic'in ne kadar öğrenildiğini gösteren güven skorudur.

Confidence;

tek bir doğru,

tek bir yanlış,

tek bir deneme,

tek bir çalışma

ile değişmez.

Confidence yalnızca zaman içinde oluşur.

---

# 7. Rule Engine

Rule Engine sistemin beynidir.

Rule Engine;

Confidence,

Observation,

Evidence,

Journey,

Revision,

Learning History

verilerini birlikte değerlendirerek karar üretir.

Rule Engine;

- yeni Topic seçebilir,
- tekrar zamanı belirleyebilir,
- çalışma yoğunluğunu değiştirebilir,
- Living Plan'i adapte edebilir.

---

# 8. Today Engine

Rule Engine karar ürettikten sonra bu karar kullanıcıya doğrudan gösterilmez.

Karar önce Today Engine tarafından projekte edilir.

Today Engine'in görevi;

karmaşık kararları

tek bir günlük çalışma akışına dönüştürmektir.

Bugün ekranı bunun sonucudur.

---

# 9. Living Plan

StudyOS'ta plan sabit değildir.

Plan yaşayan bir yapıdır.

Living Plan;

her gün,

yeni Observation,

yeni Evidence,

yeni Confidence

ile yeniden değerlendirilir.

Plan;

oluşturulmaz.

Evrilir.

---

# 10. Topic Merkezli Mimari

LOS Subject merkezli çalışmaz.

Tüm kararlar Topic seviyesinde alınır.

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

Subject yalnızca organizasyon katmanıdır.

Öğrenme Topic üzerinde gerçekleşir.

---

# 11. Kullanıcının Rolü

Kullanıcının görevi sistemi yönetmek değildir.

Kullanıcı yalnızca;

- çalışır,
- cevap verir,
- gerekirse kaynak ekler,
- gerekirse intent seçer.

Sistem;

- planlar,
- gözlemler,
- analiz eder,
- adapte olur.

---

# 12. Yapay Zekânın Rolü

LOS iki ayrı karar katmanı kullanır.

## Rule Engine

Deterministic karar üretir.

Örneğin

- Bugün tekrar yapılmalı.
- Confidence düştü.
- Yeni Topic açılmalı.

## LLM

Rule Engine kararını açıklar.

Örneğin

"Neden bugün bu konuyu çalışıyorum?"

LLM hiçbir zaman Rule Engine yerine karar vermez.

---

# 13. Öğrenme İlkeleri

LOS aşağıdaki kurallardan asla sapmaz.

- Tek veri karar oluşturmaz.
- Her karar kanıta dayanır.
- Öğrenci modül yönetmez.
- Karmaşıklık sistem içinde kalır.
- Topic öğrenmenin merkezidir.
- Rule Engine karar verir.
- LLM açıklar.
- Her gün yeniden değerlendirilir.

---

# 14. Başarı Ölçütü

LOS başarılı olduğu zaman;

öğrenci

hangi konuyu çalışacağını düşünmez,

hangi tekrarı yapacağını düşünmez,

hangi hedefe odaklanacağını düşünmez.

StudyOS zaten bunları onun yerine belirlemiştir.

---

# Son Cümle

Learning Operating System,

StudyOS'un en önemli bileşenidir.

Ekranlar değişebilir.

Teknolojiler değişebilir.

Ancak LOS döngüsü değişmez.