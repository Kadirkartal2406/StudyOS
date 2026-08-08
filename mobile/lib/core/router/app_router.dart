import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../features/achievements/presentation/screens/achievements_screen.dart';
import '../../features/adaptive_planner/presentation/screens/adaptive_planner_screen.dart';
import '../../features/ai_chat/presentation/screens/chat_screen.dart';
import '../../features/ai_chat/presentation/screens/conversations_screen.dart';
import '../../features/ai_coach/presentation/screens/ai_coach_screen.dart';
import '../../features/ai_settings/presentation/screens/ai_settings_screen.dart';
import '../../features/assessment/presentation/screens/assessment_overview_screen.dart';
import '../../features/assessment/presentation/screens/assessment_session_screen.dart';
import '../../features/assessment/presentation/screens/daily_challenge_subjects_screen.dart';
import '../../features/assessment/presentation/screens/daily_exams_list_screen.dart';
import '../../features/assessment/presentation/screens/daily_leaderboard_screen.dart';
import '../../features/assessment/presentation/screens/daily_optical_screen.dart';
import '../../features/auth/presentation/providers/auth_provider.dart';
import '../../features/auth/presentation/providers/auth_state.dart';
import '../../features/auth/presentation/screens/forgot_password_screen.dart';
import '../../features/auth/presentation/screens/login_screen.dart';
import '../../features/auth/presentation/screens/register_screen.dart';
import '../../features/auth/presentation/screens/reset_password_screen.dart';
import '../../features/auth/presentation/screens/splash_screen.dart';
import '../../features/beta_feedback/presentation/screens/analytics_dashboard_screen.dart';
import '../../features/beta_feedback/presentation/screens/beta_feedback_screen.dart';
import '../../features/beta_feedback/presentation/screens/qie_eval_screen.dart';
import '../../features/dashboard/presentation/screens/dashboard_screen.dart';
import '../../features/dashboard/presentation/screens/menu_screen.dart';
import '../../features/educational_assets/presentation/screens/maps_list_screen.dart';
import '../../features/educational_assets/presentation/screens/map_viewer_screen.dart';
import '../../features/exam_tracking/presentation/screens/add_exam_screen.dart';

import '../../features/exam_tracking/presentation/screens/edit_exam_screen.dart';
import '../../features/exam_tracking/presentation/screens/exam_detail_screen.dart';
import '../../features/exam_tracking/presentation/screens/exam_list_screen.dart';
import '../../features/exam_tracking/presentation/screens/exam_statistics_screen.dart';
import '../../features/goal_engine/presentation/screens/add_goal_screen.dart';
import '../../features/goal_engine/presentation/screens/edit_goal_screen.dart';
import '../../features/goal_engine/presentation/screens/goal_detail_screen.dart';
import '../../features/goal_engine/presentation/screens/goals_screen.dart';
import '../../features/journey/presentation/screens/journey_screen.dart';
import '../../features/memory/presentation/screens/memory_form_screen.dart';
import '../../features/memory/presentation/screens/memory_screen.dart';
import '../../features/notification_settings/presentation/screens/notification_settings_screen.dart';
import '../../features/onboarding/domain/entities/learning_profile_entity.dart';
import '../../features/onboarding/presentation/providers/first_run_phase_provider.dart';
import '../../features/onboarding/presentation/providers/learning_profile_provider.dart';
import '../../features/onboarding/presentation/screens/onboarding_screen.dart';
import '../../features/onboarding/presentation/screens/profile_screen.dart';
import '../../features/onboarding/presentation/screens/settings_screen.dart';
import '../../features/onboarding/presentation/screens/setup_calibration_screen.dart';
import '../../features/onboarding/presentation/screens/setup_preparing_screen.dart';
import '../../features/onboarding/presentation/screens/setup_system_summary_screen.dart';
import '../../features/onboarding/presentation/screens/setup_today_plan_screen.dart';
import '../../features/onboarding/presentation/screens/setup_tour_screen.dart';
import '../../features/onboarding/presentation/screens/setup_wow_screen.dart';
import '../../features/question_tracking/presentation/screens/add_question_screen.dart';
import '../../features/question_tracking/presentation/screens/edit_question_screen.dart';
import '../../features/question_tracking/presentation/screens/question_detail_screen.dart';
import '../../features/question_tracking/presentation/screens/question_list_screen.dart';
import '../../features/question_tracking/presentation/screens/question_statistics_screen.dart';
import '../../features/revision/presentation/screens/revision_screen.dart';
import '../../features/statistics/presentation/screens/statistics_screen.dart';
import '../../features/study_plan/presentation/screens/add_study_plan_screen.dart';
import '../../features/study_plan/presentation/screens/edit_study_plan_screen.dart';
import '../../features/study_plan/presentation/screens/study_plan_detail_screen.dart';
import '../../features/study_plan/presentation/screens/study_plan_screen.dart';
import '../../features/study_resources/presentation/screens/resources_screen.dart';
import '../../features/study_session/presentation/screens/pomodoro_screen.dart';
import '../../features/study_session/presentation/screens/session_detail_screen.dart';
import '../../features/study_session/presentation/screens/session_history_screen.dart';
import '../../features/subjects/presentation/screens/subject_hub_screen.dart';
import '../../features/subjects/presentation/screens/subjects_screen.dart';
import '../../features/subjects/presentation/screens/topic_work_surface_screen.dart';
import '../../features/topic_quiz/presentation/screens/quiz_session_screen.dart';

/// Auth + onboarding hard gate için router notifier.
/// AuthState / Learning Profile değişince GoRouter yeniden değerlendirilir.
class _RouterNotifier extends ChangeNotifier {
  _RouterNotifier(this._ref) {
    _ref.listen<AuthState>(authProvider, (_, __) {
      notifyListeners();
    });
    _ref.listen<AsyncValue<LearningProfileEntity>>(
      learningProfileProvider,
      (_, __) {
        notifyListeners();
      },
    );
    _ref.listen<String?>(firstRunPhaseProvider, (_, __) {
      notifyListeners();
    });
  }

  final Ref _ref;

  String? redirect(BuildContext context, GoRouterState state) {
    final authState = _ref.read(authProvider);
    final location = state.matchedLocation;

    // Splash, login/register/forgot-password dışında hiçbir yerde olmaz
    const authRoutes = {
      '/login',
      '/register',
      '/forgot-password',
      '/reset-password',
    };

    final isAuthRoute = authRoutes.contains(location);
    final isOnboarding = location == '/onboarding';
    final isSetup = location.startsWith('/setup');

    return switch (authState) {
      // İlk açılış — yalnızca splash'ta oturum kontrolü
      AuthInitial() => location == '/splash' ? null : '/splash',
      // Login/register/refresh sırasında mevcut ekranda kal (splash'e
      // düşüp checkSession'ın yarışı bozmasını engelle)
      AuthLoading() => null,
      // Giriş yapıldı — Sprint-3.1.A hard gate: onboarding zorunlu
      AuthAuthenticated() => () {
          final profileAsync = _ref.read(learningProfileProvider);
          // Profil yüklenirken: login'de kal (splash'e atma — "takılı kaldı" hissi)
          if (profileAsync.isLoading) {
            if (isAuthRoute ||
                location == '/splash' ||
                isOnboarding ||
                isSetup) {
              return null;
            }
            return null;
          }
          // Profil hatası: yeni kullanıcıyı onboarding'e al (dashboard'a yanlış düşme)
          if (profileAsync.hasError) {
            if (!isOnboarding && !isSetup && location != '/setup/wow') {
              return '/setup/wow';
            }
            return null;
          }
          final required =
              profileAsync.valueOrNull?.onboardingRequired ?? true;
          if (required && !isOnboarding && location != '/setup/wow') {
            // İlk kez: WOW sonra sohbet
            return '/setup/wow';
          }
          // RC3 — sohbet sonrası kurulum fazı
          if (!required) {
            final phase = _ref.read(firstRunPhaseProvider.notifier);
            if (phase.isSetupPending) {
              final target = phase.setupRoute;
              if (target != null) {
                // Seviye testi oturumu sırasında assessment route'una izin ver
                final phaseValue = _ref.read(firstRunPhaseProvider);
                final inCalibrationSession = phaseValue == 'calibration_active' &&
                    location.startsWith('/assessment');
                // Plan düzenleme — system summary / today plan sırasında
                final editingPlan =
                    (phaseValue == 'system_summary' ||
                        phaseValue == 'today_plan') &&
                    (location.startsWith('/planner') ||
                        location.startsWith('/goals'));
                if (!isSetup &&
                    !inCalibrationSession &&
                    !editingPlan &&
                    location != target) {
                  return target;
                }
              }
            }
          }
          if (!required && (isAuthRoute || location == '/splash')) {
            final phase = _ref.read(firstRunPhaseProvider.notifier);
            if (phase.isSetupPending) {
              return phase.setupRoute ?? '/dashboard';
            }
            return '/dashboard';
          }
          return null;
        }(),
      // Giriş yapılmadı — login'e yönlendir (splash dahil)
      AuthUnauthenticated() || AuthError() =>
        isAuthRoute ? null : '/login',
    };
  }
}

/// GoRouter Riverpod provider'ı.
final appRouterProvider = Provider<GoRouter>((ref) {
  final notifier = _RouterNotifier(ref);

  return GoRouter(
    initialLocation: '/splash',
    debugLogDiagnostics: false,
    refreshListenable: notifier,
    redirect: notifier.redirect,
    routes: [
      GoRoute(
        path: '/splash',
        name: 'splash',
        builder: (_, __) => const SplashScreen(),
      ),
      GoRoute(
        path: '/login',
        name: 'login',
        builder: (_, __) => const LoginScreen(),
      ),
      GoRoute(
        path: '/register',
        name: 'register',
        builder: (_, __) => const RegisterScreen(),
      ),
      GoRoute(
        path: '/forgot-password',
        name: 'forgot-password',
        builder: (_, __) => const ForgotPasswordScreen(),
      ),
      GoRoute(
        path: '/reset-password',
        name: 'reset-password',
        builder: (context, state) => ResetPasswordScreen(
          token: state.uri.queryParameters['token'],
        ),
      ),
      GoRoute(
        path: '/maps',
        name: 'maps',
        builder: (_, __) => const MapsListScreen(),
      ),
      GoRoute(
        path: '/maps/view',
        name: 'map-viewer',
        builder: (_, state) {
          final uri = state.uri.queryParameters['uri'] ?? 'studyos://assets/geography/turkey_admin/v1';
          final title = state.uri.queryParameters['title'] ?? 'Harita';
          return MapViewerScreen(uri: uri, title: title);
        },
      ),

      GoRoute(
        path: '/dashboard',
        name: 'dashboard',
        builder: (_, __) => const DashboardScreen(),
      ),
      GoRoute(
        path: '/menu',
        name: 'menu',
        builder: (_, __) => const MenuScreen(),
      ),
      GoRoute(
        path: '/onboarding',
        name: 'onboarding',
        builder: (_, __) => const OnboardingScreen(),
      ),
      GoRoute(
        path: '/setup/wow',
        name: 'setup-wow',
        builder: (_, __) => const SetupWowScreen(),
      ),
      GoRoute(
        path: '/setup/calibration',
        name: 'setup-calibration',
        builder: (_, __) => const SetupCalibrationScreen(),
      ),
      GoRoute(
        path: '/setup/preparing',
        name: 'setup-preparing',
        builder: (_, __) => const SetupPreparingScreen(),
      ),
      GoRoute(
        path: '/setup/system-summary',
        name: 'setup-system-summary',
        builder: (_, __) => const SetupSystemSummaryScreen(),
      ),
      GoRoute(
        path: '/setup/today-plan',
        name: 'setup-today-plan',
        builder: (_, __) => const SetupTodayPlanScreen(),
      ),
      GoRoute(
        path: '/setup/tour',
        name: 'setup-tour',
        builder: (_, __) => const SetupTourScreen(),
      ),
      GoRoute(
        path: '/profile',
        name: 'profile',
        builder: (_, __) => const ProfileScreen(),
      ),
      GoRoute(
        path: '/settings',
        name: 'settings',
        builder: (_, __) => const SettingsScreen(),
      ),
      GoRoute(
        path: '/subjects',
        name: 'subjects',
        builder: (_, __) => const SubjectsScreen(),
        routes: [
          GoRoute(
            path: ':subjectCode',
            name: 'subject-hub',
            builder: (_, state) => SubjectHubScreen(
              subjectCode: state.pathParameters['subjectCode']!,
            ),
            routes: [
              GoRoute(
                path: 'topics/:topicCode',
                name: 'topic-work-surface',
                builder: (_, state) => TopicWorkSurfaceScreen(
                  subjectCode: state.pathParameters['subjectCode']!,
                  topicCode: state.pathParameters['topicCode']!,
                ),
              ),
            ],
          ),
        ],
      ),
      GoRoute(
        path: '/study-plan',
        name: 'study-plan',
        builder: (_, state) => StudyPlanScreen(
          subjectCode: state.uri.queryParameters['subject_code'],
        ),
        routes: [
          GoRoute(
            path: 'add',
            name: 'study-plan-add',
            builder: (_, __) => const AddStudyPlanScreen(),
          ),
          GoRoute(
            path: 'edit/:id',
            name: 'study-plan-edit',
            builder: (_, state) =>
                EditStudyPlanScreen(planId: state.pathParameters['id']!),
          ),
          GoRoute(
            path: ':id/resources',
            name: 'study-plan-resources',
            builder: (_, state) => ResourcesScreen(
              studyPlanId: state.pathParameters['id'],
            ),
          ),
          GoRoute(
            path: ':id',
            name: 'study-plan-detail',
            builder: (_, state) => StudyPlanDetailScreen(
              planId: state.pathParameters['id']!,
            ),
          ),
        ],
      ),
      GoRoute(
        path: '/resources',
        name: 'resources',
        builder: (_, state) => ResourcesScreen(
          subjectCode: state.uri.queryParameters['subject_code'],
          topicCode: state.uri.queryParameters['topic_code'],
        ),
      ),
      GoRoute(
        path: '/exams',
        name: 'exams',
        builder: (_, state) => ExamListScreen(
          subjectCode: state.uri.queryParameters['subject_code'],
        ),
        routes: [
          GoRoute(
            path: 'add',
            name: 'exams-add',
            builder: (_, __) => const AddExamScreen(),
          ),
          GoRoute(
            path: 'statistics',
            name: 'exams-statistics',
            builder: (_, __) => const ExamStatisticsScreen(),
          ),
          GoRoute(
            path: 'edit/:id',
            name: 'exams-edit',
            builder: (_, state) =>
                EditExamScreen(examId: state.pathParameters['id']!),
          ),
          GoRoute(
            path: ':id',
            name: 'exams-detail',
            builder: (_, state) =>
                ExamDetailScreen(examId: state.pathParameters['id']!),
          ),
        ],
      ),
      GoRoute(
        path: '/planner',
        name: 'planner',
        builder: (_, state) => AdaptivePlannerScreen(
          subjectCode: state.uri.queryParameters['subject_code'],
        ),
      ),
      GoRoute(
        path: '/revisions',
        name: 'revisions',
        builder: (_, state) => RevisionScreen(
          subjectCode: state.uri.queryParameters['subject_code'],
        ),
      ),
      GoRoute(
        path: '/achievements',
        name: 'achievements',
        builder: (_, __) => const AchievementsScreen(),
      ),
      GoRoute(
        path: '/pomodoro',
        name: 'pomodoro',
        builder: (_, state) => PomodoroScreen(
          subjectCode: state.uri.queryParameters['subject_code'],
          topicCode: state.uri.queryParameters['topic_code'],
          topicName: state.uri.queryParameters['topic_name'],
        ),
      ),
      GoRoute(
        path: '/quiz-session',
        name: 'quiz-session',
        builder: (_, state) {
          final subject = state.uri.queryParameters['subject_code'] ?? '';
          final topic = state.uri.queryParameters['topic_code'] ?? '';
          return QuizSessionScreen(
            subjectCode: subject,
            topicCode: topic,
            topicName: state.uri.queryParameters['topic_name'],
            generationId: state.uri.queryParameters['generation_id'],
          );
        },
      ),
      // Sprint 18 — Assessment Engine
      GoRoute(
        path: '/assessment',
        name: 'assessment',
        builder: (_, __) => const AssessmentOverviewScreen(),
        routes: [
          GoRoute(
            path: 'daily',
            name: 'assessment-daily',
            builder: (_, __) => const DailyChallengeSubjectsScreen(),
            routes: [
              GoRoute(
                path: 'history',
                name: 'assessment-daily-history',
                builder: (_, __) => const DailyExamsListScreen(),
              ),
              GoRoute(
                path: 'start',
                name: 'assessment-daily-start',
                builder: (_, state) => AssessmentSessionScreen(
                  bootstrap: 'daily',
                  subjectCode: state.uri.queryParameters['subject_code'],
                ),
              ),
              GoRoute(
                path: 'leaderboard',
                name: 'assessment-daily-leaderboard',
                builder: (_, state) => DailyLeaderboardScreen(
                  subjectCode: state.uri.queryParameters['subject_code'],
                ),
              ),
              GoRoute(
                path: 'optical',
                name: 'assessment-daily-optical',
                builder: (_, state) {
                  final sid = state.uri.queryParameters['session_id'] ?? '';
                  return DailyOpticalScreen(sessionId: sid);
                },
              ),
              GoRoute(
                path: ':sessionId',
                name: 'assessment-daily-past',
                builder: (_, state) => DailyChallengeSubjectsScreen(
                  sessionId: state.pathParameters['sessionId'],
                ),
              ),
            ],
          ),
          GoRoute(
            path: 'branch/start',
            name: 'assessment-branch-start',
            builder: (_, state) {
              final kind = state.uri.queryParameters['kind'];
              final fromSetup =
                  state.uri.queryParameters['setup'] == '1';
              final countRaw = state.uri.queryParameters['count'];
              final count = int.tryParse(countRaw ?? '');
              return AssessmentSessionScreen(
                bootstrap: kind == 'calibration' ? 'calibration' : 'branch',
                subjectCode: state.uri.queryParameters['subject_code'],
                fromSetup: fromSetup,
                questionCount: count,
              );
            },
          ),
          GoRoute(
            path: 'session/:id',
            name: 'assessment-session',
            builder: (_, state) => AssessmentSessionScreen(
              sessionId: state.pathParameters['id'],
            ),
          ),
        ],
      ),
      GoRoute(
        path: '/session-history',
        name: 'session-history',
        builder: (_, __) => const SessionHistoryScreen(),
        routes: [
          GoRoute(
            path: ':id',
            name: 'session-detail',
            builder: (_, state) => SessionDetailScreen(
              sessionId: state.pathParameters['id']!,
            ),
          ),
        ],
      ),
      GoRoute(
        path: '/statistics',
        name: 'statistics',
        builder: (_, __) => const StatisticsScreen(),
      ),
      // Sprint 10 — Journey Surface
      GoRoute(
        path: '/journey',
        name: 'journey',
        builder: (_, __) => const JourneyScreen(),
      ),
      GoRoute(
        path: '/feedback',
        name: 'feedback',
        builder: (_, __) => const BetaFeedbackScreen(),
      ),
      GoRoute(
        path: '/qie-eval',
        name: 'qie-eval',
        builder: (_, __) => const QieEvalScreen(),
      ),
      GoRoute(
        path: '/analytics',
        name: 'analytics',
        builder: (_, __) => const AnalyticsDashboardScreen(),
      ),
      GoRoute(
        path: '/ai-coach',
        name: 'ai-coach',
        builder: (_, __) => const AiCoachScreen(),
      ),
      GoRoute(
        path: '/ai-settings',
        name: 'ai-settings',
        builder: (_, __) => const AiSettingsScreen(),
      ),
      GoRoute(
        path: '/ai-chat',
        name: 'ai-chat',
        builder: (_, __) => const ConversationsScreen(),
        routes: [
          GoRoute(
            path: 'new',
            name: 'ai-chat-new',
            builder: (_, __) => const ChatScreen(conversationId: 'new'),
          ),
          GoRoute(
            path: ':id',
            name: 'ai-chat-detail',
            builder: (_, state) => ChatScreen(
              conversationId: state.pathParameters['id'],
            ),
          ),
        ],
      ),
      GoRoute(
        path: '/questions',
        name: 'questions',
        builder: (_, state) => QuestionListScreen(
          subjectCode: state.uri.queryParameters['subject_code'],
        ),
        routes: [
          GoRoute(
            path: 'add',
            name: 'questions-add',
            builder: (_, __) => const AddQuestionScreen(),
          ),
          GoRoute(
            path: 'statistics',
            name: 'questions-statistics',
            builder: (_, __) => const QuestionStatisticsScreen(),
          ),
          GoRoute(
            path: ':id',
            name: 'questions-detail',
            builder: (_, state) => QuestionDetailScreen(
              recordId: state.pathParameters['id']!,
            ),
            routes: [
              GoRoute(
                path: 'edit',
                name: 'questions-edit',
                builder: (_, state) => EditQuestionScreen(
                  recordId: state.pathParameters['id']!,
                ),
              ),
            ],
          ),
        ],
      ),
      GoRoute(
        path: '/goals',
        name: 'goals',
        builder: (_, __) => const GoalsScreen(),
        routes: [
          GoRoute(
            path: 'add',
            name: 'goals-add',
            builder: (_, __) => const AddGoalScreen(),
          ),
          GoRoute(
            path: ':id',
            name: 'goals-detail',
            builder: (_, state) => GoalDetailScreen(
              goalId: state.pathParameters['id']!,
            ),
            routes: [
              GoRoute(
                path: 'edit',
                name: 'goals-edit',
                builder: (_, state) => EditGoalScreen(
                  goalId: state.pathParameters['id']!,
                ),
              ),
            ],
          ),
        ],
      ),
      GoRoute(
        path: '/notification-settings',
        name: 'notification-settings',
        builder: (_, __) => const NotificationSettingsScreen(),
      ),
      GoRoute(
        path: '/memory',
        name: 'memory',
        builder: (_, __) => const MemoryScreen(),
        routes: [
          GoRoute(
            path: 'add',
            name: 'memory-add',
            builder: (_, __) => const MemoryFormScreen(),
          ),
          GoRoute(
            path: ':id',
            name: 'memory-edit',
            builder: (_, state) => MemoryFormScreen(
              memoryId: state.pathParameters['id'],
            ),
          ),
        ],
      ),
    ],
    errorBuilder: (_, state) => Scaffold(
      backgroundColor: const Color(0xFF0A0E1A),
      body: Center(
        child: Text(
          'Sayfa bulunamadı: ${state.error}',
          style: const TextStyle(color: Colors.white),
        ),
      ),
    ),
  );
});
