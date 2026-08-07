import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/asset_contracts/asset_manifest_contract.dart';
import '../../../../core/asset_engine/asset_bundle_decoder.dart';
import '../../../../core/asset_engine/providers/eae_render_provider.dart';
import '../../../../shared/widgets/eae_vector_canvas_widget.dart';
import '../providers/asset_search_provider.dart';

class EAEInteractiveCanvas extends ConsumerStatefulWidget {
  const EAEInteractiveCanvas({
    super.key,
    required this.targetAssetId,
    required this.onNodeSelected,
    this.selectedNodeId,
    this.correctNodeId,
    this.showAnswer = false,
  });

  final String targetAssetId;
  final ValueChanged<String> onNodeSelected;
  final String? selectedNodeId;
  final String? correctNodeId;
  final bool showAnswer;

  @override
  ConsumerState<EAEInteractiveCanvas> createState() =>
      _EAEInteractiveCanvasState();
}

class _EAEInteractiveCanvasState extends ConsumerState<EAEInteractiveCanvas> {
  DecodedAssetBundle? _bundle;
  Object? _bundleError;
  bool _loadingBundle = false;

  @override
  void initState() {
    super.initState();
    _loadBundle();
  }

  @override
  void didUpdateWidget(covariant EAEInteractiveCanvas oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.targetAssetId != widget.targetAssetId) {
      _loadBundle();
    }
    if (oldWidget.selectedNodeId != widget.selectedNodeId ||
        oldWidget.correctNodeId != widget.correctNodeId ||
        oldWidget.showAnswer != widget.showAnswer) {
      _syncSelectionHighlights();
    }
  }

  Future<void> _loadBundle() async {
    setState(() {
      _loadingBundle = true;
      _bundleError = null;
    });
    try {
      final repo = ref.read(assetRepositoryProvider);
      final bytes = await repo.downloadBundle(widget.targetAssetId);
      final decoded = EAEAssetBundleDecoder.decodeBundleBytes(bytes);
      if (!mounted) return;
      setState(() {
        _bundle = decoded;
        _loadingBundle = false;
      });
      _syncSelectionHighlights();
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _bundleError = e;
        _loadingBundle = false;
      });
    }
  }

  void _syncSelectionHighlights() {
    final notifier = ref.read(eaeRenderNotifierProvider.notifier);
    notifier.clearSelection();
    final selected = widget.selectedNodeId;
    if (selected != null && selected.isNotEmpty) {
      notifier.selectNode(selected);
    }
    final highlights = <String>{};
    if (widget.showAnswer && widget.correctNodeId != null) {
      highlights.add(widget.correctNodeId!);
    }
    if (widget.selectedNodeId != null) {
      highlights.add(widget.selectedNodeId!);
    }
    notifier.setHighlightedNodes(highlights);
  }

  @override
  Widget build(BuildContext context) {
    final assetAsync = ref.watch(assetDetailProvider(widget.targetAssetId));

    if (_loadingBundle) {
      return const Center(
        child: Padding(
          padding: EdgeInsets.all(32),
          child: CircularProgressIndicator(),
        ),
      );
    }

    if (_bundle != null) {
      return Column(
        children: [
          _buildInteractionModeSelector(ref),
          Expanded(
            child: Stack(
              children: [
                EAEVectorCanvasWidget(
                  manifest: _bundle!.manifest,
                  svgContent: _bundle!.svgContent,
                  onNodeTapped: widget.showAnswer
                      ? null
                      : (node) => _handleNodeInteraction(node, ref),
                ),
                _buildInteractionOverlay(ref),
              ],
            ),
          ),
        ],
      );
    }

    return assetAsync.when(
      data: (manifest) => _fallbackBboxCanvas(manifest),
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, _) => Center(
        child: Text(
          'Asset yüklenemedi: ${_bundleError ?? error}',
          style: const TextStyle(color: Colors.red),
          textAlign: TextAlign.center,
        ),
      ),
    );
  }

  Widget _fallbackBboxCanvas(EAEAssetManifestContract manifest) {
    final viewport = manifest.viewport;
    final width = viewport.width > 0 ? viewport.width : 400.0;
    final height = viewport.height > 0 ? viewport.height : 300.0;

    return LayoutBuilder(
      builder: (context, constraints) {
        final scale = constraints.maxWidth / width;
        return SizedBox(
          width: constraints.maxWidth,
          height: height * scale,
          child: Stack(
            children: [
              Container(color: Colors.grey.shade200),
              ...manifest.layers.expand((layer) {
                return layer.nodes.map((node) {
                  final bbox = node.boundingBox;
                  if (bbox.length < 4) return const SizedBox.shrink();
                  final x = bbox[0] * scale;
                  final y = bbox[1] * scale;
                  final w = (bbox[2] - bbox[0]) * scale;
                  final h = (bbox[3] - bbox[1]) * scale;
                  final selected = node.id == widget.selectedNodeId;
                  final correct = node.id == widget.correctNodeId;
                  return Positioned(
                    left: x,
                    top: y,
                    width: w.abs(),
                    height: h.abs(),
                    child: GestureDetector(
                      onTap: widget.showAnswer
                          ? null
                          : () => widget.onNodeSelected(node.id),
                      child: Container(
                        decoration: BoxDecoration(
                          color: widget.showAnswer && correct
                              ? Colors.green.withValues(alpha: 0.3)
                              : selected
                                  ? Colors.blue.withValues(alpha: 0.3)
                                  : Colors.transparent,
                          border: Border.all(
                            color: correct && widget.showAnswer
                                ? Colors.green
                                : Colors.blue,
                          ),
                        ),
                      ),
                    ),
                  );
                });
              }),
            ],
          ),
        );
      },
    );
  }

  Widget _buildInteractionModeSelector(WidgetRef ref) {
    final mode = ref.watch(eaeRenderNotifierProvider).interactionMode;
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: EAEInteractionMode.values.map((m) {
          return Padding(
            padding: const EdgeInsets.symmetric(horizontal: 4.0),
            child: ChoiceChip(
              label: Text(m.name.toUpperCase(), style: const TextStyle(fontSize: 10)),
              selected: mode == m,
              onSelected: (selected) {
                if (selected) {
                  ref.read(eaeRenderNotifierProvider.notifier).setInteractionMode(m);
                }
              },
            ),
          );
        }).toList(),
      ),
    );
  }

  void _handleNodeInteraction(EAENodeContract node, WidgetRef ref) {
    widget.onNodeSelected(node.id);
    final notifier = ref.read(eaeRenderNotifierProvider.notifier);
    final state = ref.read(eaeRenderNotifierProvider);
    
    if (state.interactionMode == EAEInteractionMode.explore) {
      // Show info overlay implemented via overlay widget
    } else if (state.interactionMode == EAEInteractionMode.practice) {
      if (state.activeQuestionNodeId == node.id) {
        notifier.addMatch(node.id);
        notifier.setActiveQuestion(null); // Wait for next question
      }
    }
  }

  Widget _buildInteractionOverlay(WidgetRef ref) {
    final state = ref.watch(eaeRenderNotifierProvider);
    final node = state.lastTappedNodeId != null ? _bundle?.manifest.layers.expand((l) => l.nodes).where((n) => n.id == state.lastTappedNodeId).firstOrNull : null;
    
    if (state.interactionMode == EAEInteractionMode.explore && node != null) {
      return Positioned(
        bottom: 16,
        left: 16,
        right: 16,
        child: Card(
          elevation: 8,
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(node.getLocalizedName('tr'), style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                if (node.educationalMetadata?.explanations?['tr'] != null)
                  Padding(
                    padding: const EdgeInsets.only(top: 8.0),
                    child: Text(node.educationalMetadata!.explanations!['tr']!),
                  ),
                if (node.educationalMetadata?.hints?['tr'] != null)
                   Padding(
                    padding: const EdgeInsets.only(top: 8.0),
                    child: Text('İpucu: ${node.educationalMetadata!.hints!['tr']}', style: const TextStyle(fontStyle: FontStyle.italic)),
                  ),
              ],
            ),
          ),
        ),
      );
    }
    return const SizedBox.shrink();
  }
}
