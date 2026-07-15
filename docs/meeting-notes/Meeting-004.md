# Meeting-004 — AI Geliştirme Anayasasının Oluşturulması

**Tarih:** 2026-07-04  
**Katılımcı AI:** Claude (Anthropic) — Sonnet 4.6  
**Oturum Hedefi:** StudyOS projesi için kalıcı AI Geliştirme Anayasası oluşturmak  
**Durum:** Tamamlandı  
**Önceki Toplantı:** Meeting-003 — Resmi Sunum Oluşturma

---

## Yapılanlar

### 1. AI Anayasası Oluşturuldu
`docs/project/ai-rules.md` dosyası sıfırdan yazıldı.

Anayasa aşağıdaki 10 bölümden oluşmaktadır:

| Bölüm | Başlık |
|-------|--------|
| 1 | AI Rolü — sorumluluklar ve yasaklar |
| 2 | İletişim Kuralları |
| 3 | Geliştirme Kuralları |
| 4 | Dokümantasyon Kuralları |
| 5 | Mimari Kurallar |
| 6 | Token Optimizasyon Kuralları |
| 7 | Dosya Yönetimi Kuralları |
| 8 | Karar Alma Kuralları |
| 9 | Kalite Kontrol Listesi |
| 10 | Gelecek Uyumluluk |

### 2. Toplantı Notu Oluşturuldu
Bu dosya — `docs/meeting-notes/Meeting-004.md`

---

## Alınan Kararlar

| # | Karar | Gerekçe |
|---|-------|---------|
| D-001 | Anayasa Türkçe yazılır | Hedef kitle Türkiye pazarındadır; proje dili Türkçe olarak belirlendi |
| D-002 | Anayasa model bağımsız tasarlanır | Claude, GPT, Gemini gibi farklı modellerin aynı kuralları izlemesi sağlanır |
| D-003 | 10 temel kural özeti eklenir | Uzun belgeyi her oturumda okumak yerine hızlı referans noktası sunulur |
| D-004 | ADR (Architecture Decision Record) formatı benimsenir | Karar geçmişinin izlenebilir ve yapılandırılmış biçimde tutulması için |
| D-005 | Onay noktaları açıkça tanımlanır | AI'ın nihai kararlar üretmesinin önüne geçmek için |

---

## Oluşturulan / Güncellenen Dosyalar

| Dosya | İşlem | Açıklama |
|-------|-------|----------|
| `docs/project/ai-rules.md` | **OLUŞTURULDU** | 10 bölümlük resmi AI Anayasası |
| `docs/meeting-notes/Meeting-004.md` | **OLUŞTURULDU** | Bu toplantı notu |
| `docs/project/` | **OLUŞTURULDU** | Yeni klasör; proje anayasası ve genel kurallar için |
| `docs/meeting-notes/` | **OLUŞTURULDU** | Yeni klasör; tüm toplantı notları için |

---

## Açık Sorular

| # | Soru | Öncelik |
|---|------|---------|
| AQ-001 | `docs/decisions/` klasörü için ilk ADR belgesi ne zaman oluşturulacak? | Orta |
| AQ-002 | Her klasöre eklenecek `README.md` dosyaları ne zaman yazılacak? | Düşük |
| AQ-003 | Anayasanın İngilizce versiyonu gerekiyor mu? (yabancı paydaşlar için) | Düşük |
| AQ-004 | Token optimizasyon kuralları için bağlam penceresi sınırı sayısal olarak belirtilmeli mi? | Düşük |

---

## Kalite Kontrol

Oturum kapatılmadan önce anayasada tanımlanan kontrol listesi uygulandı:

```
[x] Oturum hedefi tamamlandı
[x] Toplantı notu oluşturuldu
[x] Alınan kararlar belgelendi (bu dosyada)
[x] Değiştirilen/oluşturulan dosyalar listelendi
[x] Adlandırma kurallarına uygunluk kontrol edildi
[x] Bilgi tekrarı oluşturulmadı
[x] Yeni çelişki eklenmedi
[x] Onay gerektiren madde bulunmuyor (bu oturum dokümantasyon odaklıydı)
[x] Bir sonraki adım netleştirildi
```

---

## Bir Sonraki Adım

**Meeting-005 önerisi:** Teknik Mimari Tasarımı

Anayasa artık yürürlüktedir. Bir sonraki oturumda teknik mimari kararları (veritabanı, API tasarımı, klasör yapısı) `docs/architecture/` altında yapılandırılmış biçimde ele alınabilir.

> Tüm gelecek AI oturumları `docs/project/ai-rules.md` belgesini okuyarak başlamalıdır.