import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/workspace_provider.dart';
import '../widgets/canvas_painter.dart';

class BlankWorkspaceScreen extends ConsumerStatefulWidget {
  const BlankWorkspaceScreen({super.key});

  @override
  ConsumerState<BlankWorkspaceScreen> createState() => _BlankWorkspaceScreenState();
}

class _BlankWorkspaceScreenState extends ConsumerState<BlankWorkspaceScreen> {
  List<Offset> _currentStroke = [];
  final TransformationController _transformationController = TransformationController();

  void _onPanStart(DragStartDetails details) {
    final state = ref.read(workspaceProvider);
    if (state.currentTool == DrawingTool.select || state.currentTool == DrawingTool.eae) return;
    
    // Convert global position to local position considering InteractiveViewer transform
    final localPosition = _transformationController.toScene(details.localPosition);
    
    if (state.currentTool == DrawingTool.eraser) {
      ref.read(workspaceProvider.notifier).eraseAt(localPosition);
    } else {
      setState(() {
        _currentStroke = [localPosition];
      });
    }
  }

  void _onPanUpdate(DragUpdateDetails details) {
    final state = ref.read(workspaceProvider);
    if (state.currentTool == DrawingTool.select || state.currentTool == DrawingTool.eae) return;

    final localPosition = _transformationController.toScene(details.localPosition);

    if (state.currentTool == DrawingTool.eraser) {
      ref.read(workspaceProvider.notifier).eraseAt(localPosition);
    } else if (_currentStroke.isNotEmpty) {
      setState(() {
        _currentStroke.add(localPosition);
      });
    }
  }

  void _onPanEnd(DragEndDetails details) {
    if (_currentStroke.isNotEmpty) {
      ref.read(workspaceProvider.notifier).addStroke(_currentStroke);
      setState(() {
        _currentStroke = [];
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(workspaceProvider);
    final notifier = ref.read(workspaceProvider.notifier);

    // Disable InteractiveViewer pan when drawing
    final canPanAndZoom = state.currentTool == DrawingTool.select;

    return Scaffold(
      backgroundColor: Colors.grey[200],
      appBar: AppBar(
        title: const Text('Digital Notebook'),
        actions: [
          IconButton(
            icon: const Icon(Icons.undo),
            onPressed: state.undoHistory.isNotEmpty ? notifier.undo : null,
          ),
          IconButton(
            icon: const Icon(Icons.redo),
            onPressed: state.redoHistory.isNotEmpty ? notifier.redo : null,
          ),
        ],
      ),
      body: Column(
        children: [
          // Toolbar
          Container(
            color: Colors.white,
            padding: const EdgeInsets.all(8.0),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  _ToolButton(
                    icon: Icons.pan_tool,
                    isSelected: state.currentTool == DrawingTool.select,
                    onTap: () => notifier.setTool(DrawingTool.select),
                    tooltip: 'Select / Pan',
                  ),
                  _ToolButton(
                    icon: Icons.edit,
                    isSelected: state.currentTool == DrawingTool.pen,
                    onTap: () => notifier.setTool(DrawingTool.pen),
                    tooltip: 'Pen',
                  ),
                  _ToolButton(
                    icon: Icons.brush,
                    isSelected: state.currentTool == DrawingTool.highlighter,
                    onTap: () => notifier.setTool(DrawingTool.highlighter),
                    tooltip: 'Highlighter',
                  ),
                  _ToolButton(
                    icon: Icons.auto_fix_normal,
                    isSelected: state.currentTool == DrawingTool.eraser,
                    onTap: () => notifier.setTool(DrawingTool.eraser),
                    tooltip: 'Eraser',
                  ),
                  const VerticalDivider(),
                  _ColorButton(
                    color: Colors.black,
                    isSelected: state.currentColor == Colors.black,
                    onTap: () => notifier.setColor(Colors.black),
                  ),
                  _ColorButton(
                    color: Colors.red,
                    isSelected: state.currentColor == Colors.red,
                    onTap: () => notifier.setColor(Colors.red),
                  ),
                  _ColorButton(
                    color: Colors.blue,
                    isSelected: state.currentColor == Colors.blue,
                    onTap: () => notifier.setColor(Colors.blue),
                  ),
                  _ColorButton(
                    color: Colors.yellow,
                    isSelected: state.currentColor == Colors.yellow,
                    onTap: () => notifier.setColor(Colors.yellow),
                  ),
                ],
              ),
            ),
          ),
          // Canvas
          Expanded(
            child: ClipRect(
              child: InteractiveViewer(
                transformationController: _transformationController,
                panEnabled: canPanAndZoom,
                scaleEnabled: true,
                minScale: 0.5,
                maxScale: 5.0,
                child: GestureDetector(
                  onPanStart: _onPanStart,
                  onPanUpdate: _onPanUpdate,
                  onPanEnd: _onPanEnd,
                  child: Container(
                    width: 3000,
                    height: 3000,
                    color: Colors.white,
                    child: CustomPaint(
                      painter: CanvasPainter(
                        objects: state.objects,
                        currentStroke: _currentStroke,
                        currentTool: state.currentTool,
                        currentColor: state.currentColor,
                        currentStrokeWidth: state.currentStrokeWidth,
                      ),
                      size: const Size(3000, 3000),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _ToolButton extends StatelessWidget {
  final IconData icon;
  final bool isSelected;
  final VoidCallback onTap;
  final String tooltip;

  const _ToolButton({
    required this.icon,
    required this.isSelected,
    required this.onTap,
    required this.tooltip,
  });

  @override
  Widget build(BuildContext context) {
    return IconButton(
      icon: Icon(icon, color: isSelected ? Theme.of(context).primaryColor : Colors.grey),
      tooltip: tooltip,
      onPressed: onTap,
    );
  }
}

class _ColorButton extends StatelessWidget {
  final Color color;
  final bool isSelected;
  final VoidCallback onTap;

  const _ColorButton({
    required this.color,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 4),
        width: 24,
        height: 24,
        decoration: BoxDecoration(
          color: color,
          shape: BoxShape.circle,
          border: isSelected ? Border.all(color: Colors.black, width: 2) : null,
        ),
      ),
    );
  }
}
