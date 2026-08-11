import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:studyos_mobile/core/theme/app_colors.dart';
import 'package:studyos_mobile/core/theme/app_theme.dart';
import 'package:studyos_mobile/shared/widgets/study_glass_button.dart';
import 'package:studyos_mobile/shared/widgets/study_icons.dart';

void main() {
  testWidgets('StudyGlassButton shows label and invokes onPressed', (tester) async {
    var taps = 0;
    await tester.pumpWidget(
      MaterialApp(
        theme: AppTheme.lightTheme(),
        home: Scaffold(
          body: StudyGlassButton(
            label: 'Çalışmaya Başla',
            onPressed: () => taps++,
          ),
        ),
      ),
    );

    expect(find.text('Çalışmaya Başla'), findsOneWidget);
    expect(find.byIcon(StudyIcons.play), findsOneWidget);
    expect(find.byIcon(StudyIcons.next), findsOneWidget);

    await tester.tap(find.text('Çalışmaya Başla'));
    await tester.pump();
    expect(taps, 1);
  });

  testWidgets('StudyGlassButton loading disables tap and shows spinner text', (
    tester,
  ) async {
    var taps = 0;
    await tester.pumpWidget(
      MaterialApp(
        theme: AppTheme.lightTheme(),
        home: Scaffold(
          body: StudyGlassButton(
            label: 'Kaydet',
            loading: true,
            onPressed: () => taps++,
          ),
        ),
      ),
    );

    expect(find.text('Yükleniyor...'), findsOneWidget);
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    await tester.tap(find.text('Yükleniyor...'));
    await tester.pump();
    expect(taps, 0);
  });

  testWidgets('StudyGlassButton disabled ignores presses', (tester) async {
    var taps = 0;
    await tester.pumpWidget(
      MaterialApp(
        theme: AppTheme.lightTheme(),
        home: Scaffold(
          body: StudyGlassButton(
            label: 'Pasif',
            onPressed: null,
          ),
        ),
      ),
    );

    await tester.tap(find.text('Pasif'));
    await tester.pump();
    expect(taps, 0);
  });

  testWidgets('Secondary glass keeps readable label without press', (
    tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        theme: AppTheme.lightTheme(),
        home: Scaffold(
          body: StudyGlassButton(
            label: 'Derse Devam Et',
            leadingIcon: Icons.bookmark_outline_rounded,
            variant: StudyGlassVariant.secondary,
            onPressed: () {},
          ),
        ),
      ),
    );

    final label = tester.widget<Text>(find.text('Derse Devam Et'));
    expect(
      label.style?.color,
      AppColors.onSurfaceOf(Brightness.light),
    );
    // Dark label on frosted glass — visible without press.
    expect(label.style!.color!.computeLuminance(), lessThan(0.2));
  });

  testWidgets('Secondary glass dark theme keeps light labels', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        theme: AppTheme.darkTheme(),
        home: Scaffold(
          body: StudyGlassButton(
            label: 'Hedefleri Gör',
            leadingIcon: Icons.bar_chart_rounded,
            variant: StudyGlassVariant.secondary,
            onPressed: () {},
          ),
        ),
      ),
    );

    final label = tester.widget<Text>(find.text('Hedefleri Gör'));
    expect(label.style?.color, AppColors.textPrimaryDark);
    expect(label.style!.color!.computeLuminance(), greaterThan(0.7));
  });

  testWidgets('StudyIconButton respects min touch size', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        theme: AppTheme.lightTheme(),
        home: Scaffold(
          body: StudyIconButton(
            icon: Icons.add,
            size: 40,
            onPressed: () {},
          ),
        ),
      ),
    );

    final box = tester.getSize(find.byType(StudyIconButton));
    expect(box.width, greaterThanOrEqualTo(44));
    expect(box.height, greaterThanOrEqualTo(44));
  });
}
