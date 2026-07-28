import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../features/achievements/presentation/providers/achievement_provider.dart';
import '../../features/adaptive_planner/presentation/providers/planner_provider.dart';
import '../../features/ai_chat/presentation/providers/ai_chat_provider.dart';
import '../../features/ai_coach/presentation/providers/ai_coach_provider.dart';
import '../../features/ai_settings/presentation/providers/ai_settings_provider.dart';
import '../../features/auth/presentation/providers/auth_provider.dart';
import '../../features/auth/presentation/providers/auth_state.dart';
import '../../features/exam_tracking/presentation/providers/exam_provider.dart';
import '../../features/goal_engine/presentation/providers/goal_provider.dart';
import '../../features/memory/presentation/providers/memory_provider.dart';
import '../../features/notification_settings/presentation/providers/notification_settings_provider.dart';
import '../../features/onboarding/presentation/providers/active_exam_provider.dart';
import '../../features/onboarding/presentation/providers/learning_profile_provider.dart';
import '../../features/question_tracking/presentation/providers/question_tracking_provider.dart';
import '../../features/revision/presentation/providers/revision_provider.dart';
import '../../features/statistics/presentation/providers/statistics_provider.dart';
import '../../features/study_plan/presentation/providers/study_plan_provider.dart';
import '../../features/study_session/presentation/providers/session_history_provider.dart';
import '../../features/study_session/presentation/providers/study_session_provider.dart';

/// Auth kullanıcı kimliği değişince kullanıcıya özel cache'leri temizler.
/// `dashboardProvider` auth'u zaten watch eder; burada diğer StateNotifier'lar.
final sessionScopeProvider = Provider<void>((ref) {
  ref.listen<AuthState>(authProvider, (previous, next) {
    final prevId = previous is AuthAuthenticated ? previous.user.id : null;
    final nextId = next is AuthAuthenticated ? next.user.id : null;
    if (prevId == nextId) return;

    ref.invalidate(learningProfileProvider);
    ref.invalidate(activeExamControllerProvider);
    ref.invalidate(revisionProvider);
    ref.invalidate(studyPlanProvider);
    ref.invalidate(plannerProvider);
    ref.invalidate(examProvider);
    ref.invalidate(questionListProvider);
    ref.invalidate(questionStatsProvider);
    ref.invalidate(goalProvider);
    ref.invalidate(memoryProvider);
    ref.invalidate(statisticsProvider);
    ref.invalidate(achievementProvider);
    ref.invalidate(aiCoachProvider);
    ref.invalidate(aiChatProvider);
    ref.invalidate(aiSettingsProvider);
    ref.invalidate(notificationSettingsProvider);
    ref.invalidate(studySessionProvider);
    ref.invalidate(sessionHistoryProvider);
  });
});
