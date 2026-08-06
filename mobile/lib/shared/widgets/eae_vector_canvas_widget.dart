import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/asset_contracts/asset_manifest_contract.dart';
import '../../core/asset_engine/eae_canvas_painter.dart';
import '../../core/asset_engine/eae_hit_tester.dart';
import '../../core/asset_engine/path_parser.dart';
import '../../core/asset_engine/providers/eae_render_provider.dart';

class EAEVectorCanvasWidget extends ConsumerStatefulWidget {
  final EAEAssetManifestContract manifest;
  final String svgContent;
  final ValueChanged<EAENodeContract>? onNodeTapped;
  final bool enableMultiSelect;

  const EAEVectorCanvasWidget({
    super.key,
    required this.manifest,
    required this.svgContent,
    this.onNodeTapped,
    this.enableMultiSelect = false,
  });

  @override
  ConsumerState<EAEVectorCanvasWidget> createState() =>
      _EAEVectorCanvasWidgetState();
}

class _EAEVectorCanvasWidgetState
    extends ConsumerState<EAEVectorCanvasWidget> {
  final TransformationController _transformationController =
      TransformationController();
  final Map<String, Path> _parsedPaths = {};

  @override
  void initState() {
    super.initState();
    _parseSvgPaths();
    _transformationController.addListener(_onTransformationChanged);
  }

  @override
  void didUpdateWidget(covariant EAEVectorCanvasWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.svgContent != widget.svgContent ||
        oldWidget.manifest.assetId != widget.manifest.assetId) {
      _parsedPaths.clear();
      _parseSvgPaths();
    }
  }

  @override
  void dispose() {
    _transformationController.removeListener(_onTransformationChanged);
    _transformationController.dispose();
    super.dispose();
  }

  void _onTransformationChanged() {
    final scale = _transformationController.value.getMaxScaleOnAxis();
    ref.read(eaeRenderNotifierProvider.notifier).updateScale(scale);
  }

  void _parseSvgPaths() {
    if (widget.svgContent.isEmpty) return;

    final pathTagRegex = RegExp(
      '<path[^>]*id="([^"]+)"[^>]*d="([^"]+)"[^>]*>',
      caseSensitive: false,
    );

    final matches = pathTagRegex.allMatches(widget.svgContent);
    for (final match in matches) {
      final id = match.group(1);
      final pathData = match.group(2);
      if (id != null && pathData != null && pathData.isNotEmpty) {
        _parsedPaths[id] = EAEPathParser.parseSvgPathData(pathData);
      }
    }

    final altRegex = RegExp(
      '<path[^>]*d="([^"]+)"[^>]*id="([^"]+)"[^>]*>',
      caseSensitive: false,
    );
    final altMatches = altRegex.allMatches(widget.svgContent);
    for (final match in altMatches) {
      final pathData = match.group(1);
      final id = match.group(2);
      if (id != null && pathData != null && pathData.isNotEmpty) {
        _parsedPaths[id] = EAEPathParser.parseSvgPathData(pathData);
      }
    }
  }

  void _handleTapUp(TapUpDetails details) {
    final renderState = ref.read(eaeRenderNotifierProvider);
    final localPosition = details.localPosition;

    final hitNode = EAEHitTester.performHitTest(
      localPoint: localPosition,
      manifest: widget.manifest,
      parsedNodePaths: _parsedPaths,
      currentScale: renderState.currentScale,
    );

    if (hitNode != null) {
      ref.read(eaeRenderNotifierProvider.notifier).selectNode(
            hitNode.id,
            multiSelect: widget.enableMultiSelect,
          );
      widget.onNodeTapped?.call(hitNode);
    }
  }

  @override
  Widget build(BuildContext context) {
    final renderState = ref.watch(eaeRenderNotifierProvider);
    final viewport = widget.manifest.viewport;

    return Container(
      color: Colors.transparent,
      child: InteractiveViewer(
        transformationController: _transformationController,
        minScale: viewport.defaultScale,
        maxScale: viewport.maxScale,
        clipBehavior: Clip.hardEdge,
        child: GestureDetector(
          onTapUp: _handleTapUp,
          child: CustomPaint(
            size: Size(viewport.width, viewport.height),
            painter: EAEVectorCanvasPainter(
              manifest: widget.manifest,
              parsedPaths: _parsedPaths,
              selectedNodeIds: renderState.selectedNodeIds,
              highlightedNodeIds: renderState.highlightedNodeIds,
              currentScale: renderState.currentScale,
            ),
          ),
        ),
      ),
    );
  }
}
