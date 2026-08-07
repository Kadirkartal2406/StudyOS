import 'package:flutter_riverpod/flutter_riverpod.dart';

enum EAEInteractionMode {
  explore,
  study,
  practice,
  exam,
  hotspotQuiz,
  label,
  dragDrop,
  match,
  revealAnswers,
  freeExploration
}

class EAERenderState {
  final Set<String> selectedNodeIds;
  final Set<String> highlightedNodeIds;
  final double currentScale;
  final String? lastTappedNodeId;
  final EAEInteractionMode interactionMode;
  final Set<String> matchedNodeIds;
  final String? activeQuestionNodeId;

  const EAERenderState({
    this.selectedNodeIds = const {},
    this.highlightedNodeIds = const {},
    this.currentScale = 1.0,
    this.lastTappedNodeId,
    this.interactionMode = EAEInteractionMode.explore,
    this.matchedNodeIds = const {},
    this.activeQuestionNodeId,
  });

  EAERenderState copyWith({
    Set<String>? selectedNodeIds,
    Set<String>? highlightedNodeIds,
    double? currentScale,
    String? lastTappedNodeId,
    EAEInteractionMode? interactionMode,
    Set<String>? matchedNodeIds,
    String? activeQuestionNodeId,
  }) {
    return EAERenderState(
      selectedNodeIds: selectedNodeIds ?? this.selectedNodeIds,
      highlightedNodeIds: highlightedNodeIds ?? this.highlightedNodeIds,
      currentScale: currentScale ?? this.currentScale,
      lastTappedNodeId: lastTappedNodeId ?? this.lastTappedNodeId,
      interactionMode: interactionMode ?? this.interactionMode,
      matchedNodeIds: matchedNodeIds ?? this.matchedNodeIds,
      activeQuestionNodeId: activeQuestionNodeId ?? this.activeQuestionNodeId,
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

  void setInteractionMode(EAEInteractionMode mode) {
    state = state.copyWith(
      interactionMode: mode,
      selectedNodeIds: {},
      highlightedNodeIds: {},
      matchedNodeIds: {},
      activeQuestionNodeId: null,
    );
  }

  void setActiveQuestion(String? nodeId) {
    state = state.copyWith(activeQuestionNodeId: nodeId);
  }

  void addMatch(String nodeId) {
    final updated = Set<String>.from(state.matchedNodeIds)..add(nodeId);
    state = state.copyWith(matchedNodeIds: updated);
  }
}

final eaeRenderNotifierProvider =
    StateNotifierProvider.autoDispose<EAERenderNotifier, EAERenderState>((ref) {
  return EAERenderNotifier();
});
