# Sprint 5 — Çalışma Oturumu: Tam Döngü

**Durum:** ✅ Tamamlandı  
**Tarih:** 2026-07-20  
**Önceki sprint:** Alignment Sprint-4 (tamamlandı)  
**Test kriteri:** Pomodoro oturumu bitince `topic_evidence` tablosuna kayıt düşmeli, `topic_confidence` güncellenmiş olmalı.

---

## Sorun Tespiti

LOS'un Evidence katmanı backend'de hazır ama mobil taraf konu bilgisini (`subject_code`, `topic_code`) oturum başlatma isteğine **göndermiyordu**. Bu nedenle:
- `study_sessions` tablosunda `subject_code` / `topic_code` NULL kalıyordu
- `EvidenceService.ingest_session()` çağrılıyor ama topic bind edilemediği için kanıt zayıf/bağsız kalıyordu
- `TopicConfidence` hiç güncellenemiyordu

---

## M5.1 — Mobil: Oturum Başlatmada Topic Bilgisi

### Değişen dosyalar
- `PomodoroScreen` → `topicCode` parametresi alır, `setContext` çağırır
- `app_router.dart` → `/pomodoro` route'u `topic_code` query param'ı okur
- `StartStudySessionUsecase` → `subjectCode`, `topicCode` parametresi alır
- `StudySessionRepository` → `start()` imzası güncellendi
- `StudySessionRepositoryImpl` → body'ye ekler
- `StudySessionNotifier` → `start()` metodu konu bilgisini gönderir

---

## M5.2 — Backend: Evidence Zinciri Doğrulama

### Kontrol listesi
- `study_session_service.finish()` → `EvidenceService.ingest_session()` çağrısı ✅
- `ingest_session()` → `subject_code` / `topic_code` ile Effort + Temporal Evidence üretir ✅
- `EvidenceService.trigger_confidence_recalculation()` → `ConfidenceEngine.recalculate()` ✅

---

## M5.3 — Mobil: Topic Work Surface'te Oturum Özeti

### Değişen dosyalar
- `TopicWorkSurfaceScreen` → o konudaki toplam oturum sayısı + dakika gösterir
- Backend endpoint `/subjects/{code}/topics/{code}/work-surface` zaten `study_minutes` döndürüyor
- UI'da basit istatistik satırı

---

## Test Senaryosu

1. Kayıt ol (KPSS)
2. Derslere git → bir konu seç → "Çalışmaya Başla"
3. Pomodoro ekranında 1 dk odak, 0 dk mola ayarla
4. Başlat → bitir
5. Backend: `SELECT * FROM topic_evidence WHERE user_id = ...` → kayıt var mı?
6. Backend: `SELECT * FROM topic_confidence WHERE user_id = ...` → güncellendi mi?
7. Today dashboard yenile → Next Action değişti mi?
