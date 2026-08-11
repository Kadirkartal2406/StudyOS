import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:studyos_mobile/core/theme/app_theme.dart';
import 'package:studyos_mobile/shared/widgets/study_question_chrome.dart';

void main() {
  testWidgets('StudyChoiceOption selects and shows letter', (tester) async {
    var taps = 0;
    await tester.pumpWidget(
      MaterialApp(
        theme: AppTheme.lightTheme(),
        home: Scaffold(
          body: StudyChoiceOption(
            letter: 'A',
            label: 'İlk seçenek',
            selected: true,
            onTap: () => taps++,
          ),
        ),
      ),
    );

    expect(find.text('A'), findsOneWidget);
    expect(find.text('İlk seçenek'), findsOneWidget);
    await tester.tap(find.text('İlk seçenek'));
    await tester.pump();
    expect(taps, 1);
  });

  testWidgets('StudyQuestionFooter next vs finish labels', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        theme: AppTheme.lightTheme(),
        home: Scaffold(
          body: StudyQuestionFooter(
            canGoPrevious: true,
            isLast: false,
            submitting: false,
            onPrevious: () {},
            onNext: () {},
            onSubmit: () {},
          ),
        ),
      ),
    );

    expect(find.text('Önceki'), findsOneWidget);
    expect(find.text('Sonraki Soru'), findsOneWidget);
    expect(find.text('Bitir'), findsNothing);
  });

  testWidgets('StudyQuestionProgress shows fraction', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        theme: AppTheme.lightTheme(),
        home: const Scaffold(
          body: StudyQuestionProgress(
            current: 5,
            total: 20,
            subtitle: 'Matematik',
          ),
        ),
      ),
    );

    expect(find.textContaining('5 / 20'), findsOneWidget);
    expect(find.textContaining('Matematik'), findsOneWidget);
  });
}
