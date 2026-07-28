import 'package:flutter_test/flutter_test.dart';
import 'package:studyos_mobile/features/study_resources/data/models/study_resource_model.dart';
import 'package:studyos_mobile/features/study_resources/domain/entities/study_resource_entity.dart';

void main() {
  test('StudyResourceModel.fromJson maps youtube', () {
    final model = StudyResourceModel.fromJson({
      'id': '11111111-1111-1111-1111-111111111111',
      'title': 'TYT',
      'resource_type': 'youtube',
      'url': 'https://youtu.be/abc',
      'status': 'not_started',
      'order_index': 1,
      'created_at': '2026-07-17T10:00:00Z',
      'updated_at': '2026-07-17T10:00:00Z',
      'metadata': {'youtube_ready': false},
    });
    final entity = model.toEntity();
    expect(entity.resourceType, ResourceType.youtube);
    expect(entity.isYoutube, isTrue);
    expect(entity.metadata['youtube_ready'], isFalse);
  });
}
