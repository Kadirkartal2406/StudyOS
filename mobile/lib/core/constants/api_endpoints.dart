/// StudyOS — API Endpoint sabitleri.
class ApiEndpoints {
  ApiEndpoints._();

  // ── Auth ────────────────────────────────────────────────
  static const String register = '/auth/register';
  static const String login = '/auth/login';
  static const String refresh = '/auth/refresh';
  static const String logout = '/auth/logout';
  static const String forgotPassword = '/auth/forgot-password';
  static const String resetPassword = '/auth/reset-password';
  static const String verifyEmail = '/auth/verify-email';

  // ── Users ───────────────────────────────────────────────
  static const String me = '/users/me';

  // ── Students ────────────────────────────────────────────
  static const String studentMe = '/students/me';
  static const String studentStatistics = '/statistics/me/daily';

  // ── Study Plans ─────────────────────────────────────────
  static const String studyPlanToday = '/study-plans/today';
  static const String studyPlans = '/study-plans';

  // ── Notifications ───────────────────────────────────────
  static const String notifications = '/notifications';
  static const String notificationsUnreadCount = '/notifications/unread-count';

  // ── AI ──────────────────────────────────────────────────
  static const String aiStudyCoach = '/ai/study-coach';

  // ── Health ──────────────────────────────────────────────
  static const String health = '/health';
}
