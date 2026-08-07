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
  final TransformationController? externalTransformationController;
  final bool panEnabled;
  final bool scaleEnabled;
  final bool enableMultiSelect;

  const EAEVectorCanvasWidget({
    super.key,
    required this.manifest,
    required this.svgContent,
    this.onNodeTapped,
    this.externalTransformationController,
    this.panEnabled = true,
    this.scaleEnabled = true,
    this.enableMultiSelect = false,
  });

  @override
  ConsumerState<EAEVectorCanvasWidget> createState() =>
      _EAEVectorCanvasWidgetState();
}

class _EAEVectorCanvasWidgetState
    extends ConsumerState<EAEVectorCanvasWidget> {
  late TransformationController _transformationController;
  final Map<String, Path> _parsedPaths = {};
  bool _isInitialScaleSet = false;

  @override
  void initState() {
    super.initState();
    _transformationController =
        widget.externalTransformationController ?? TransformationController();
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
    if (widget.externalTransformationController !=
            oldWidget.externalTransformationController) {
      if (oldWidget.externalTransformationController == null) {
        _transformationController.removeListener(_onTransformationChanged);
        _transformationController.dispose();
      }
      _transformationController = widget.externalTransformationController ??
          TransformationController();
      _transformationController.addListener(_onTransformationChanged);
    }
  }

  @override
  void dispose() {
    _transformationController.removeListener(_onTransformationChanged);
    if (widget.externalTransformationController == null) {
      _transformationController.dispose();
    }
    super.dispose();
  }

  void _onTransformationChanged() {
    final scale = _transformationController.value.getMaxScaleOnAxis();
    Future.microtask(() {
      if (mounted) {
        ref.read(eaeRenderNotifierProvider.notifier).updateScale(scale);
      }
    });
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
    final viewport = widget.manifest.viewport;

    return Consumer(
      builder: (context, ref, child) {
        final renderState = ref.watch(eaeRenderNotifierProvider);
        return LayoutBuilder(
          builder: (context, constraints) {
            if (!_isInitialScaleSet && constraints.maxWidth > 0) {
              final scale = constraints.maxWidth / viewport.width;
              _transformationController.value = Matrix4.identity()..scale(scale);
              _isInitialScaleSet = true;
            }
            
            return Container(
              color: Colors.transparent,
              child: InteractiveViewer(
                transformationController: _transformationController,
                minScale: 0.1,
                maxScale: viewport.maxScale * 2,
                clipBehavior: Clip.hardEdge,
                panEnabled: widget.panEnabled,
                scaleEnabled: widget.scaleEnabled,
                child: GestureDetector(
                  onTapUp: _handleTapUp,
                  child: CustomPaint(
                    size: Size(viewport.width, viewport.height),
                    painter: EAEVectorCanvasPainter(
                      manifest: widget.manifest,
                      parsedPaths: _parsedPaths,
                      selectedNodeIds: renderState.selectedNodeIds,
                      highlightedNodeIds: renderState.highlightedNodeIds,
                      matchedNodeIds: renderState.matchedNodeIds,
                      activeQuestionNodeId: renderState.activeQuestionNodeId,
                      currentScale: renderState.currentScale,
                      interactionMode: renderState.interactionMode,
                    ),
                  ),
                ),
              ),
            );
          }
        );
      },
    );
  }
}
