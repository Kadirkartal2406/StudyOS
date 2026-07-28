import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:studyos_mobile/features/dashboard/presentation/widgets/last_exam_card.dart';

void main() {
  testWidgets('LastExamCard shows empty state', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: Scaffold(body: LastExamCard())),
    );
    expect(find.text('Henüz deneme yok'), findsOneWidget);
  });

  testWidgets('LastExamCard shows title and net', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: LastExamCard(
            title: 'TYT Deneme',
            net: 42.5,
            deltaNet: 3.0,
            aiSummary: 'Son deneme özeti',
          ),
        ),
      ),
    );
    expect(find.text('TYT Deneme'), findsOneWidget);
    expect(find.textContaining('42.5'), findsOneWidget);
    expect(find.text('Son deneme özeti'), findsOneWidget);
  });
}
