/// M25 — Home screen widget + iOS Live Activities mimari iskeleti (P1).
///
/// Beta sonrası:
/// - Android: `home_widget` ile bugünkü süre / aktif sayaç / Molaya Çık|Derse Dön
/// - iOS: ActivityKit Live Activities + Dynamic Island
///
/// Veri kaynağı: [StudySessionNotifier] state + `/study-sessions/active`.
/// Bildirim katmanı: [StudySessionLiveNotificationService].
///
/// Bu dosya bilinçli olarak boş bir sözleşme tutar; çekirdek motorlara
/// (Decision / Living Plan / Confidence / Coach) bağımlılık yok.
abstract final class StudySessionSurfacePorts {
  /// Home widget / Live Activity’ye yazılacak snapshot.
  static const String sharedPrefsKey = 'study_session_live_snapshot';

  /// Widget aksiyonları — native taraf bu string’leri dinler.
  static const String actionTakeBreak = 'take_break';
  static const String actionResumeStudy = 'resume_study';
}
