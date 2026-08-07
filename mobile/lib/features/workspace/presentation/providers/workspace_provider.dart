import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';
import 'package:flutter/material.dart';
import '../../domain/entities/annotation_object.dart';

enum DrawingTool { pen, highlighter, eraser, text, select, eae }

class WorkspaceState {
  final List<AnnotationObject> objects;
  final List<List<AnnotationObject>> undoHistory;
  final List<List<AnnotationObject>> redoHistory;
  final DrawingTool currentTool;
  final Color currentColor;
  final double currentStrokeWidth;
  final AnnotationObject? selectedObject;

  WorkspaceState({
    this.objects = const [],
    this.undoHistory = const [],
    this.redoHistory = const [],
    this.currentTool = DrawingTool.pen,
    this.currentColor = Colors.black,
    this.currentStrokeWidth = 2.0,
    this.selectedObject,
  });

  WorkspaceState copyWith({
    List<AnnotationObject>? objects,
    List<List<AnnotationObject>>? undoHistory,
    List<List<AnnotationObject>>? redoHistory,
    DrawingTool? currentTool,
    Color? currentColor,
    double? currentStrokeWidth,
    AnnotationObject? selectedObject,
  }) {
    return WorkspaceState(
      objects: objects ?? this.objects,
      undoHistory: undoHistory ?? this.undoHistory,
      redoHistory: redoHistory ?? this.redoHistory,
      currentTool: currentTool ?? this.currentTool,
      currentColor: currentColor ?? this.currentColor,
      currentStrokeWidth: currentStrokeWidth ?? this.currentStrokeWidth,
      selectedObject: selectedObject ?? this.selectedObject,
    );
  }
}

class WorkspaceNotifier extends StateNotifier<WorkspaceState> {
  WorkspaceNotifier() : super(WorkspaceState());

  void setTool(DrawingTool tool) {
    state = state.copyWith(currentTool: tool, selectedObject: null);
  }

  void setColor(Color color) {
    state = state.copyWith(currentColor: color);
  }

  void setStrokeWidth(double width) {
    state = state.copyWith(currentStrokeWidth: width);
  }

  void _saveHistory() {
    final newUndo = List<List<AnnotationObject>>.from(state.undoHistory)..add(state.objects);
    state = state.copyWith(undoHistory: newUndo, redoHistory: []);
  }

  void addStroke(List<Offset> points) {
    if (points.isEmpty) return;
    _saveHistory();
    final color = state.currentTool == DrawingTool.highlighter 
        ? state.currentColor.withOpacity(0.3) 
        : state.currentColor;
    final width = state.currentTool == DrawingTool.highlighter 
        ? state.currentStrokeWidth * 3 
        : state.currentStrokeWidth;
        
    final newStroke = StrokeObject(
      id: const Uuid().v4(),
      points: points,
      color: color,
      strokeWidth: width,
    );
    
    state = state.copyWith(objects: [...state.objects, newStroke]);
  }

  void eraseAt(Offset point, {double radius = 15.0}) {
    final toRemove = <String>{};
    for (final obj in state.objects) {
      if (obj is StrokeObject) {
        for (final p in obj.points) {
          if ((p - point).distance <= radius) {
            toRemove.add(obj.id);
            break;
          }
        }
      }
    }
    if (toRemove.isNotEmpty) {
      _saveHistory();
      final remaining = state.objects.where((o) => !toRemove.contains(o.id)).toList();
      state = state.copyWith(objects: remaining);
    }
  }
  
  void undo() {
    if (state.undoHistory.isEmpty) return;
    final newRedo = List<List<AnnotationObject>>.from(state.redoHistory)..add(state.objects);
    final prev = state.undoHistory.last;
    final newUndo = List<List<AnnotationObject>>.from(state.undoHistory)..removeLast();
    state = state.copyWith(objects: prev, undoHistory: newUndo, redoHistory: newRedo);
  }

  void redo() {
    if (state.redoHistory.isEmpty) return;
    final newUndo = List<List<AnnotationObject>>.from(state.undoHistory)..add(state.objects);
    final next = state.redoHistory.last;
    final newRedo = List<List<AnnotationObject>>.from(state.redoHistory)..removeLast();
    state = state.copyWith(objects: next, undoHistory: newUndo, redoHistory: newRedo);
  }

  void addEaeAsset(String assetId, Offset position) {
    _saveHistory();
    final newEae = EaeObject(
      id: const Uuid().v4(),
      assetId: assetId,
      position: position,
    );
    state = state.copyWith(objects: [...state.objects, newEae]);
  }
}

final workspaceProvider = StateNotifierProvider<WorkspaceNotifier, WorkspaceState>((ref) {
  return WorkspaceNotifier();
});
