library;

/// StudyOS Educational Asset Engine (EAE) — Client Asset Manifest Contracts
/// Corresponds to backend app.core.asset_contracts specification.

class EAEViewportContract {
  final double width;
  final double height;
  final double defaultScale;
  final double maxScale;

  const EAEViewportContract({
    required this.width,
    required this.height,
    this.defaultScale = 1.0,
    this.maxScale = 8.0,
  });

  factory EAEViewportContract.fromJson(Map<String, dynamic> json) {
    return EAEViewportContract(
      width: (json['width'] as num).toDouble(),
      height: (json['height'] as num).toDouble(),
      defaultScale: (json['default_scale'] as num?)?.toDouble() ?? 1.0,
      maxScale: (json['max_scale'] as num?)?.toDouble() ?? 8.0,
    );
  }

  Map<String, dynamic> toJson() => {
        'width': width,
        'height': height,
        'default_scale': defaultScale,
        'max_scale': maxScale,
      };
}

class EAENodeContract {
  final String id;
  final Map<String, String> name;
  final List<double> boundingBox;
  final Map<String, dynamic> attributes;

  const EAENodeContract({
    required this.id,
    required this.name,
    required this.boundingBox,
    this.attributes = const {},
  });

  factory EAENodeContract.fromJson(Map<String, dynamic> json) {
    final rawName = json['name'] as Map<String, dynamic>? ?? {};
    final localizedName = rawName.map((k, v) => MapEntry(k, v.toString()));
    final rawBbox = (json['bounding_box'] as List<dynamic>?)
            ?.map((e) => (e as num).toDouble())
            .toList() ??
        [0.0, 0.0, 0.0, 0.0];

    return EAENodeContract(
      id: json['id'] as String,
      name: localizedName,
      boundingBox: rawBbox,
      attributes: json['attributes'] as Map<String, dynamic>? ?? {},
    );
  }

  String getLocalizedName(String languageCode) {
    return name[languageCode] ?? name['tr'] ?? name['en'] ?? id;
  }
}

class EAELayerContract {
  final String id;
  final int zIndex;
  final double minLod;
  final List<EAENodeContract> nodes;

  const EAELayerContract({
    required this.id,
    this.zIndex = 0,
    this.minLod = 1.0,
    this.nodes = const [],
  });

  factory EAELayerContract.fromJson(Map<String, dynamic> json) {
    final rawNodes = (json['nodes'] as List<dynamic>?)
            ?.map((e) => EAENodeContract.fromJson(e as Map<String, dynamic>))
            .toList() ??
        [];

    return EAELayerContract(
      id: json['id'] as String,
      zIndex: (json['z_index'] as num?)?.toInt() ?? 0,
      minLod: (json['min_lod'] as num?)?.toDouble() ?? 1.0,
      nodes: rawNodes,
    );
  }
}

class EAEAssetManifestContract {
  final String schemaVersion;
  final String assetId;
  final String version;
  final String domain;
  final String format;
  final Map<String, String> title;
  final EAEViewportContract viewport;
  final List<EAELayerContract> layers;
  final List<String> tags;
  final String licenseType;
  final String? tenantId;

  const EAEAssetManifestContract({
    required this.schemaVersion,
    required this.assetId,
    required this.version,
    required this.domain,
    required this.format,
    required this.title,
    required this.viewport,
    required this.layers,
    this.tags = const [],
    this.licenseType = 'studyos_core',
    this.tenantId,
  });

  factory EAEAssetManifestContract.fromJson(Map<String, dynamic> json) {
    final rawTitle = json['title'] as Map<String, dynamic>? ?? {};
    final localizedTitle = rawTitle.map((k, v) => MapEntry(k, v.toString()));
    final rawLayers = (json['layers'] as List<dynamic>?)
            ?.map((e) => EAELayerContract.fromJson(e as Map<String, dynamic>))
            .toList() ??
        [];
    final rawTags = (json['tags'] as List<dynamic>?)
            ?.map((e) => e.toString())
            .toList() ??
        [];

    return EAEAssetManifestContract(
      schemaVersion: json['schema_version'] as String? ?? '1.0',
      assetId: json['asset_id'] as String,
      version: json['version'] as String,
      domain: json['domain'] as String,
      format: json['format'] as String? ?? 'svg',
      title: localizedTitle,
      viewport: EAEViewportContract.fromJson(
        json['viewport'] as Map<String, dynamic>,
      ),
      layers: rawLayers,
      tags: rawTags,
      licenseType: json['license_type'] as String? ?? 'studyos_core',
      tenantId: json['tenant_id'] as String?,
    );
  }

  String getLocalizedTitle(String languageCode) {
    return title[languageCode] ?? title['tr'] ?? title['en'] ?? assetId;
  }
}
