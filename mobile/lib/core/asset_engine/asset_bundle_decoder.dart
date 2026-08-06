import 'dart:convert';
import 'dart:typed_data';

import 'package:archive/archive.dart';

import '../asset_contracts/asset_manifest_contract.dart';

class DecodedAssetBundle {
  final EAEAssetManifestContract manifest;
  final String svgContent;
  final Map<String, dynamic> spatialTree;

  const DecodedAssetBundle({
    required this.manifest,
    required this.svgContent,
    required this.spatialTree,
  });
}

class EAEAssetBundleDecoder {
  /// Unpacks and decodes binary zlib compressed bundle bytes on client side.
  static DecodedAssetBundle decodeBundleBytes(List<int> compressedBytes) {
    final decompressedBytes =
        const ZLibDecoder().decodeBytes(Uint8List.fromList(compressedBytes));
    final jsonString = utf8.decode(decompressedBytes);
    final jsonMap = json.decode(jsonString) as Map<String, dynamic>;

    final manifestMap = jsonMap['manifest'] as Map<String, dynamic>;
    final svgContent = jsonMap['svg_content'] as String? ?? '';
    final spatialTree = jsonMap['spatial_tree'] as Map<String, dynamic>? ?? {};

    final manifest = EAEAssetManifestContract.fromJson(manifestMap);

    return DecodedAssetBundle(
      manifest: manifest,
      svgContent: svgContent,
      spatialTree: spatialTree,
    );
  }
}
