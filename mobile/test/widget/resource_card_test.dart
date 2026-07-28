import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:studyos_mobile/features/study_resources/domain/entities/study_resource_entity.dart';
import 'package:studyos_mobile/features/study_resources/presentation/widgets/resource_card.dart';

void main() {
  testWidgets('ResourceCard shows title and watch button for youtube',
      (tester) async {
    final resource = StudyResourceEntity(
      id: '1',
      title: 'Matematik Videosu',
      resourceType: ResourceType.youtube,
      status: ResourceStatus.notStarted,
      orderIndex: 0,
      url: 'https://youtu.be/abc',
      provider: 'youtube',
      durationSeconds: 120,
      createdAt: DateTime(2026, 7, 17),
      updatedAt: DateTime(2026, 7, 17),
    );

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: ResourceCard(
            resource: resource,
            onOpen: () {},
            onComplete: () {},
            onDelete: () {},
          ),
        ),
      ),
    );

    expect(find.text('Matematik Videosu'), findsOneWidget);
    expect(find.text('İzle'), findsOneWidget);
  });
}
