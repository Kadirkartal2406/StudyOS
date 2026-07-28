class AiSettingsModel {
  const AiSettingsModel({
    required this.effectiveProvider,
    required this.availableProviders,
    required this.streamingEnabled,
    required this.fallbackProvider,
    this.preferredProvider,
    this.preferredModel,
    this.effectiveModel,
    this.debug = const {},
  });

  final String? preferredProvider;
  final String? preferredModel;
  final String effectiveProvider;
  final String? effectiveModel;
  final String fallbackProvider;
  final List<String> availableProviders;
  final bool streamingEnabled;
  final Map<String, dynamic> debug;

  factory AiSettingsModel.fromJson(Map<String, dynamic> json) {
    final providers = (json['available_providers'] as List<dynamic>? ?? [])
        .map((e) => e.toString())
        .toList();
    final debugRaw = json['debug'];
    return AiSettingsModel(
      preferredProvider: json['preferred_provider'] as String?,
      preferredModel: json['preferred_model'] as String?,
      effectiveProvider: json['effective_provider'] as String? ?? 'null',
      effectiveModel: json['effective_model'] as String?,
      fallbackProvider: json['fallback_provider'] as String? ?? 'null',
      availableProviders: providers,
      streamingEnabled: json['streaming_enabled'] as bool? ?? false,
      debug: debugRaw is Map
          ? debugRaw.map((k, v) => MapEntry(k.toString(), v))
          : const {},
    );
  }
}
