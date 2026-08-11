import 'package:flutter/material.dart';

/// StudyOS Icon System v1.0 — outlined 24pt semantic icons (2px line language).
class StudyIcons {
  StudyIcons._();

  // ── Navigation ────────────────────────────────────────────
  static const IconData today = Icons.home_outlined;
  static const IconData subjects = Icons.menu_book_outlined;
  static const IconData focus = Icons.adjust;
  static const IconData plan = Icons.event_available_outlined;
  static const IconData menu = Icons.menu_rounded;

  // ── Home / Dashboard ──────────────────────────────────────
  static const IconData progress = Icons.data_usage_outlined;
  static const IconData goal = Icons.track_changes_outlined;
  static const IconData continueStudy = Icons.play_circle_outline_rounded;
  static const IconData calendar = Icons.calendar_today_outlined;
  static const IconData statistics = Icons.bar_chart_rounded;
  static const IconData journey = Icons.route_outlined;
  static const IconData maps = Icons.map_outlined;

  // ── Study & questions ─────────────────────────────────────
  static const IconData play = Icons.play_arrow_rounded;
  static const IconData next = Icons.chevron_right_rounded;
  static const IconData previous = Icons.chevron_left_rounded;
  static const IconData answer = Icons.edit_outlined;
  static const IconData solution = Icons.visibility_outlined;
  static const IconData bookmark = Icons.bookmark_border_rounded;
  static const IconData document = Icons.description_outlined;
  static const IconData quiz = Icons.quiz_outlined;
  static const IconData exam = Icons.assignment_outlined;
  static const IconData dailyExam = Icons.auto_stories_outlined;
  static const IconData levelTest = Icons.assessment_outlined;
  static const IconData examResults = Icons.grading_outlined;
  static const IconData revision = Icons.replay_outlined;
  static const IconData questions = Icons.help_outline_rounded;

  // ── Planning & focus ──────────────────────────────────────
  static const IconData addPlan = Icons.add_box_outlined;
  static const IconData checklist = Icons.checklist_rounded;
  static const IconData edit = Icons.edit_note_outlined;
  static const IconData reminder = Icons.notifications_none_rounded;
  static const IconData notifications = Icons.notifications_none_rounded;
  static const IconData pomodoro = Icons.timer_outlined;
  static const IconData clock = Icons.schedule_outlined;
  static const IconData pause = Icons.pause_rounded;
  static const IconData stop = Icons.stop_rounded;
  static const IconData planner = Icons.auto_awesome_outlined;
  static const IconData memory = Icons.psychology_outlined;
  static const IconData resources = Icons.folder_outlined;

  // ── AI & communication ────────────────────────────────────
  static const IconData aiChat = Icons.chat_bubble_outline_rounded;
  static const IconData aiCoach = Icons.smart_toy_outlined;
  static const IconData aiSettings = Icons.tune_rounded;
  static const IconData help = Icons.help_outline_rounded;
  static const IconData feedback = Icons.rate_review_outlined;

  // ── Profile & status ──────────────────────────────────────
  static const IconData profile = Icons.person_outline_rounded;
  static const IconData settings = Icons.settings_outlined;
  static const IconData security = Icons.shield_outlined;
  static const IconData logout = Icons.logout_rounded;
  static const IconData success = Icons.check_circle_outline_rounded;
  static const IconData info = Icons.info_outline_rounded;
  static const IconData warning = Icons.warning_amber_rounded;
  static const IconData error = Icons.cancel_outlined;
  static const IconData search = Icons.search_rounded;
  static const IconData refresh = Icons.refresh_rounded;
  static const IconData achievements = Icons.emoji_events_outlined;

  /// Subject list accent icons (rotate by index).
  static const List<IconData> subjectGlyphs = [
    Icons.explore_outlined,
    Icons.edit_outlined,
    Icons.menu_book_outlined,
    Icons.science_outlined,
    Icons.public_outlined,
  ];
}
