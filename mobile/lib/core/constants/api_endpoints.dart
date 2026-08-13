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

  // ── Dashboard ───────────────────────────────────────────
  static const String dashboard = '/dashboard';

  // ── Study Plans (Sprint-1.4, bkz. api-design.md §2.6) ──────
  static const String studyPlans = '/study-plans';
  static String studyPlan(String id) => '/study-plans/$id';
  static String studyPlanStart(String id) => '/study-plans/$id/start';
  static String studyPlanComplete(String id) => '/study-plans/$id/complete';
  static String studyPlanSkip(String id) => '/study-plans/$id/skip';
  static String studyPlanResources(String id) => '/study-plans/$id/resources';

  // ── Study Resources (Sprint-2.5) ──────────────────────────
  static const String resources = '/resources';
  static String resource(String id) => '/resources/$id';
  static String resourceOpen(String id) => '/resources/$id/open';
  static const String resourcesStatistics = '/resources/statistics';

  // ── Study Sessions / Pomodoro (Sprint-1.5) ─────────────────
  static const String studySessionsStart = '/study-sessions/start';
  static const String studySessionsPause = '/study-sessions/pause';
  static const String studySessionsResume = '/study-sessions/resume';
  static const String studySessionsFinish = '/study-sessions/finish';
  static const String studySessionsBreakStart = '/study-sessions/break/start';
  static const String studySessionsBreakEnd = '/study-sessions/break/end';
  static const String studySessionsActive = '/study-sessions/active';
  static const String studySessionsToday = '/study-sessions/today';
  static const String studySessionsTodaySummary = '/study-sessions/today-summary';
  static const String studySessionsHistory = '/study-sessions/history';
  static const String studySessionsStatistics = '/study-sessions/statistics';
  static String studySession(String id) => '/study-sessions/$id';

  // ── Statistics (Sprint-1.6) ────────────────────────────────
  static const String statisticsOverview = '/statistics/overview';
  static const String statisticsDaily = '/statistics/daily';
  static const String statisticsWeekly = '/statistics/weekly';
  static const String statisticsMonthly = '/statistics/monthly';
  static const String statisticsSubjects = '/statistics/subjects';
  static const String statisticsTopics = '/statistics/topics';
  static const String statisticsProductivity = '/statistics/productivity';
  static const String statisticsHeatmap = '/statistics/heatmap';
  static const String statisticsStreak = '/statistics/streak';

  // ── Questions (Sprint-1.9) ─────────────────────────────────
  static const String questions = '/questions';
  static String question(String id) => '/questions/$id';
  static const String questionsStatistics = '/questions/statistics';
  static const String questionsDaily = '/questions/daily';
  static const String questionsSubjects = '/questions/subjects';
  static const String questionsTopics = '/questions/topics';
  static const String questionsExams = '/questions/exams';

  // ── Notification Settings (Sprint-1.8) ─────────────────────
  static const String notificationSettings = '/notification-settings';
  static const String notificationSettingsFcmToken =
      '/notification-settings/fcm-token';

  // ── Notifications (inbox — sonraki sprint) ─────────────────
  static const String notifications = '/notifications';
  static const String notificationsUnreadCount = '/notifications/unread-count';

  // ── AI Insights (Sprint-2.0) ─────────────────────────────
  static const String aiOverview = '/ai/overview';
  static const String aiRecommendations = '/ai/recommendations';
  static const String aiTrends = '/ai/trends';
  static const String aiPerformance = '/ai/performance';
  static const String aiProductivity = '/ai/productivity';

  // ── AI Chat (Sprint-2.2 / 2.4) ───────────────────────────
  static const String aiChat = '/ai/chat';
  static const String aiChatStream = '/ai/chat/stream';
  static const String aiSettings = '/ai/settings';
  static const String aiConversations = '/ai/conversations';
  static String aiConversation(String id) => '/ai/conversations/$id';
  // Taslak LLM endpoint (henüz yok)
  static const String aiStudyCoach = '/ai/study-coach';

  // ── Goals (Sprint-2.1) ───────────────────────────────────
  static const String goals = '/goals';
  static const String goalsActive = '/goals/active';
  static const String goalsCompleted = '/goals/completed';
  static const String goalsProgress = '/goals/progress';
  static const String goalsWeekly = '/goals/weekly';
  static const String goalsMonthly = '/goals/monthly';
  static String goal(String id) => '/goals/$id';
  static String goalExplain(String id) => '/goals/$id/explain';

  // ── Memory (Sprint-2.3) ──────────────────────────────────
  static const String memory = '/memory';
  static String memoryItem(String id) => '/memory/$id';
  static const String memorySearch = '/memory/search';
  static const String memorySettings = '/memory/settings';
  static const String memoryExport = '/memory/export';
  static const String memoryClear = '/memory/clear';

  // ── Exams (Sprint-2.6) ─────────────────────────────────────
  static const String exams = '/exams';
  static const String examCatalog = '/exam-catalog';
  static String examCatalogExam(String exam) => '/exam-catalog/$exam';
  static String examCatalogPacks(String exam) => '/exam-catalog/$exam/packs';
  static String examCatalogPack(String exam, String pack) =>
      '/exam-catalog/$exam/packs/$pack';
  static String examCatalogSubjects(String exam) =>
      '/exam-catalog/$exam/subjects';
  static String examCatalogSubjectTopics(String exam, String subject) =>
      '/exam-catalog/$exam/subjects/$subject/topics';
  static String examCatalogTopic(String topic) => '/exam-catalog/topics/$topic';
  static String examCatalogImportance(String exam) =>
      '/exam-catalog/$exam/importance';
  static String exam(String id) => '/exams/$id';
  static String examResults(String id) => '/exams/$id/results';
  static const String examsStatistics = '/exams/statistics';
  static const String examsTrends = '/exams/trends';

  // ── Planner (Sprint-2.7 / Sprint-9) ──────────────────────────
  static const String plannerGenerate = '/planner/generate';
  static const String plannerSuggestions = '/planner/suggestions';
  static String plannerDraft(String id) => '/planner/$id';
  static String plannerAccept(String id) => '/planner/$id/accept';
  static String plannerReject(String id) => '/planner/$id/reject';
  static String plannerExplain(String id) => '/planner/$id/explain';
  static String plannerSuggestionAccept(String id) =>
      '/planner/suggestions/$id/accept';
  static String plannerSuggestionReject(String id) =>
      '/planner/suggestions/$id/reject';

  // ── Revisions (Sprint-2.8) ─────────────────────────────────
  static const String revisions = '/revisions';
  static const String revisionsToday = '/revisions/today';
  static const String revisionsWeek = '/revisions/week';
  static const String revisionsOverdue = '/revisions/overdue';
  static const String revisionsStatistics = '/revisions/statistics';
  static const String revisionsHeatmap = '/revisions/heatmap';
  static const String revisionsGenerate = '/revisions/generate';
  static String revision(String id) => '/revisions/$id';
  static String revisionReview(String id) => '/revisions/$id/review';
  static String revisionSkip(String id) => '/revisions/$id/skip';
  static String revisionPostpone(String id) => '/revisions/$id/postpone';
  static String revisionExplain(String id) => '/revisions/$id/explain';

  // ── Achievements (Sprint-2.9) ──────────────────────────────
  static const String achievements = '/achievements';
  static const String achievementsUnlocked = '/achievements/unlocked';
  static const String achievementsProgress = '/achievements/progress';
  static const String achievementsCheck = '/achievements/check';
  static String achievement(String id) => '/achievements/$id';
  static String achievementExplain(String id) => '/achievements/$id/explain';

  // ── Learning Profile / Onboarding (Sprint-3.0 / 3.1.A) ─────
  static const String learningProfile = '/learning-profile/me';
  static const String activeExam = '/learning-profile/active-exam';
  static const String onboardingStatus = '/learning-profile/onboarding/status';
  static const String onboardingComplete =
      '/learning-profile/onboarding/complete';
  static const String onboardingWelcomeTone =
      '/learning-profile/onboarding/welcome-tone';
  static const String onboardingSkip = '/learning-profile/onboarding/skip';
  static const String examTargets = '/learning-profile/exam-targets';
  static const String subjectCatalog = '/learning-profile/subjects/catalog';
  static const String mySubjects = '/learning-profile/subjects/me';
  static String subjectHub(String subjectCode) =>
      '/learning-profile/subjects/$subjectCode';
  static String subjectTopics(String subjectCode) =>
      '/learning-profile/subjects/$subjectCode/topics';
  static String topicWorkSurface(String subjectCode, String topicCode) =>
      '/learning-profile/subjects/$subjectCode/topics/$topicCode/work-surface';
  static String topicNotebook(String subjectCode, String topicCode) =>
      '/learning-profile/subjects/$subjectCode/topics/$topicCode/notebook';
  static String topicExplain(String subjectCode, String topicCode) =>
      '/learning-profile/subjects/$subjectCode/topics/$topicCode/explain';
  static String topicQuizGenerate(String subjectCode, String topicCode) =>
      '/learning-profile/subjects/$subjectCode/topics/$topicCode/questions/generate';

  // ── Topic Quiz Session (Sprint-14) ──────────────────────
  static String topicQuizSessionGenerate(String subjectCode, String topicCode) =>
      '/topic-quiz/subjects/$subjectCode/topics/$topicCode/generate';
  static String topicQuizSession(String generationId) =>
      '/topic-quiz/$generationId';
  static String topicQuizSessionSubmit(String generationId) =>
      '/topic-quiz/$generationId/submit';
  static String topicQuizHistory(String subjectCode, String topicCode) =>
      '/topic-quiz/subjects/$subjectCode/topics/$topicCode/history';

  // ── Topic Test Catalog (published weekly tests) ─────────
  static const String topicTestsCatalog = '/topic-tests/catalog';
  static String topicTestStart(String testId) =>
      '/topic-tests/tests/$testId/start';
  static String topicTestAttempt(String attemptId) =>
      '/topic-tests/attempts/$attemptId';
  static String topicTestSubmit(String attemptId) =>
      '/topic-tests/attempts/$attemptId/submit';

  // ── Assessment Engine (Sprint-18) ───────────────────────
  static const String assessment = '/assessment';
  static const String assessmentStart = '/assessment/start';
  static String assessmentSession(String sessionId) =>
      '/assessment/sessions/$sessionId';
  static String assessmentSessionPdf(String sessionId) =>
      '/assessment/sessions/$sessionId/pdf';
  static String assessmentSubmit(String sessionId) =>
      '/assessment/sessions/$sessionId/submit';
  static String assessmentContinueAdaptive(String sessionId) =>
      '/assessment/sessions/$sessionId/continue-adaptive';
  static String assessmentQuestionExplain(String sessionId, String questionId) =>
      '/assessment/sessions/$sessionId/questions/$questionId/explain';
  static String assessmentSessionReportPdf(String sessionId) =>
      '/assessment/sessions/$sessionId/report.pdf';
  static const String dailyChallenge = '/assessment/daily-challenge';
  static const String dailyChallengeStart = '/assessment/daily-challenge/start';
  static const String dailyChallengeSubjects =
      '/assessment/daily-challenge/subjects';
  static const String dailyChallengeLeaderboard =
      '/assessment/daily-challenge/leaderboard';
  static const String dailyChallengeLeaderboardOverall =
      '/assessment/daily-challenge/leaderboard/overall';
  static const String estimatedScore = '/assessment/estimated-score';
  static const String ranking = '/assessment/ranking';

  // ── Knowledge Layer (Sprint-19) ─────────────────────────
  static String knowledgeIndexResource(String resourceId) =>
      '/knowledge/resources/$resourceId/index';
  static const String knowledgeReindex = '/knowledge/notebook/reindex';
  static String knowledgeTopicNotebook(String subjectCode, String topicCode) =>
      '/knowledge/topics/$subjectCode/$topicCode/notebook';
  static String knowledgeNotebook(String notebookId) =>
      '/knowledge/notebook/$notebookId';
  static String knowledgeCitations(String notebookId) =>
      '/knowledge/notebook/$notebookId/citations';

  // ── Adaptive Coach (Sprint-20) ──────────────────────────
  static const String coachToday = '/coach/today';
  static const String coachWeekly = '/coach/weekly';
  static const String coachTimeline = '/coach/timeline';
  static const String coachAssessmentSummary = '/coach/assessment-summary';

  // ── Beta RC (Sprint-21) ─────────────────────────────────
  static const String analyticsTrack = '/beta/analytics/track';
  static const String analyticsBatch = '/beta/analytics/batch';
  static const String analyticsDashboard = '/beta/analytics/dashboard';
  static const String betaFeedback = '/beta/feedback';
  static const String qieEvalQueue = '/beta/qie-eval/queue';
  static const String qieEvalSubmit = '/beta/qie-eval';

  // ── Journey trends (Sprint-15) ──────────────────────────
  static const String journeyTrends = '/learning-profile/journey/trends';

  // ── AI Explain (Sprint-12) ──────────────────────────────
  static const String aiExplain = '/ai/explain';

  // ── Health ──────────────────────────────────────────────
  static const String health = '/health';
}
