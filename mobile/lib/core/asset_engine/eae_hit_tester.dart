import 'package:flutter/material.dart';
import '../asset_contracts/asset_manifest_contract.dart';

class EAEHitTestResult {
  final EAENodeContract node;
  final Offset localOffset;

  const EAEHitTestResult({
    required this.node,
    required this.localOffset,
  });
}

class EAEHitTester {
  /// Evaluates local canvas point against R-Tree spatial bounding boxes and exact Path geometry.
  static EAENodeContract? performHitTest({
    required Offset localPoint,
    required EAEAssetManifestContract manifest,
    required Map<String, Path> parsedNodePaths,
    double currentScale = 1.0,
  }) {
    for (final layer in manifest.layers.reversed) {
      if (currentScale < layer.minLod) continue;

      for (final node in layer.nodes.reversed) {
        final bbox = node.boundingBox;
        if (bbox.length < 4) continue;

        final minX = bbox[0];
        final minY = bbox[1];
        final maxX = bbox[2];
        final maxY = bbox[3];

        // 1. R-Tree Bounding Box Candidate Check
        if (localPoint.dx >= minX &&
            localPoint.dx <= maxX &&
            localPoint.dy >= minY &&
            localPoint.dy <= maxY) {

          // 2. Exact Path Contains Check
          final path = parsedNodePaths[node.id];
          if (path != null) {
            if (path.contains(localPoint)) {
              return node;
            }
          } else {
            // Fallback to bounding box hit if path data not parsed
            return node;
          }
        }
      }
    }
    return null;
  }
}
