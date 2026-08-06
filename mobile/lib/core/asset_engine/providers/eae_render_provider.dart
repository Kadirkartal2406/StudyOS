import 'package:flutter_riverpod/flutter_riverpod.dart';

class EAERenderState {
  final Set<String> selectedNodeIds;
  final Set<String> highlightedNodeIds;
  final double currentScale;
  final String? lastTappedNodeId;

  const EAERenderState({
    this.selectedNodeIds = const {},
    this.highlightedNodeIds = const {},
    this.currentScale = 1.0,
    this.lastTappedNodeId,
  });

  EAERenderState copyWith({
    Set<String>? selectedNodeIds,
    Set<String>? highlightedNodeIds,
    double? currentScale,
    String? lastTappedNodeId,
  }) {
    return EAERenderState(
      selectedNodeIds: selectedNodeIds ?? this.selectedNodeIds,
      highlightedNodeIds: highlightedNodeIds ?? this.highlightedNodeIds,
      currentScale: currentScale ?? this.currentScale,
      lastTappedNodeId: lastTappedNodeId ?? this.lastTappedNodeId,
    );
  }
}

class EAERenderNotifier extends StateNotifier<EAERenderState> {
  EAERenderNotifier() : super(const EAERenderState());

  void selectNode(String nodeId, {bool multiSelect = false}) {
    if (multiSelect) {
      final updated = Set<String>.from(state.selectedNodeIds);
      if (updated.contains(nodeId)) {
        updated.remove(nodeId);
      } else {
        updated.add(nodeId);
      }
      state = state.copyWith(
        selectedNodeIds: updated,
        lastTappedNodeId: nodeId,
      );
    } else {
      state = state.copyWith(
        selectedNodeIds: {nodeId},
        lastTappedNodeId: nodeId,
      );
    }
  }

  void clearSelection() {
    state = state.copyWith(selectedNodeIds: {}, lastTappedNodeId: null);
  }

  void setHighlightedNodes(Set<String> nodeIds) {
    state = state.copyWith(highlightedNodeIds: nodeIds);
  }

  void updateScale(double scale) {
    state = state.copyWith(currentScale: scale);
  }
}

final eaeRenderNotifierProvider =
    StateNotifierProvider.autoDispose<EAERenderNotifier, EAERenderState>((ref) {
  return EAERenderNotifier();
});
