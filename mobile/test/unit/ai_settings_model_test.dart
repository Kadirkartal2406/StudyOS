import 'package:flutter_test/flutter_test.dart';
import 'package:studyos_mobile/features/ai_settings/data/models/ai_settings_model.dart';

void main() {
  test('AiSettingsModel.fromJson', () {
    final model = AiSettingsModel.fromJson({
      'preferred_provider': 'gemini',
      'preferred_model': 'gemini-2.0-flash',
      'effective_provider': 'gemini',
      'effective_model': 'gemini-2.0-flash',
      'fallback_provider': 'null',
      'available_providers': ['null', 'gemini', 'openai', 'claude'],
      'streaming_enabled': false,
      'debug': {'has_gemini_key': false},
    });
    expect(model.preferredProvider, 'gemini');
    expect(model.availableProviders, contains('claude'));
    expect(model.debug['has_gemini_key'], isFalse);
  });
}
