import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:syncfusion_flutter_pdfviewer/pdfviewer.dart';

import '../providers/workspace_provider.dart';
import '../widgets/canvas_painter.dart';
import '../widgets/eae_draggable_widget.dart';

class PdfWorkspaceScreen extends ConsumerStatefulWidget {
  final String pdfUrl;
  
  const PdfWorkspaceScreen({super.key, required this.pdfUrl});

  @override
  ConsumerState<PdfWorkspaceScreen> createState() => _PdfWorkspaceScreenState();
}

class _PdfWorkspaceScreenState extends ConsumerState<PdfWorkspaceScreen> {
  final GlobalKey<SfPdfViewerState> _pdfViewerKey = GlobalKey();
  final PdfViewerController _pdfViewerController = PdfViewerController();
  List<Offset> _currentStroke = [];
  
  void _onPanStart(DragStartDetails details) {
    final state = ref.read(workspaceProvider({'workspaceId': widget.pdfUrl, 'pageIndex': '1'}));
    if (state.currentTool == DrawingTool.select || state.currentTool == DrawingTool.eae) return;
    
    if (state.currentTool == DrawingTool.eraser) {
      ref.read(workspaceProvider({'workspaceId': widget.pdfUrl, 'pageIndex': '1'}).notifier).eraseAt(details.localPosition);
    } else {
      setState(() {
        _currentStroke = [details.localPosition];
      });
    }
  }

  void _onPanUpdate(DragUpdateDetails details) {
    final state = ref.read(workspaceProvider({'workspaceId': widget.pdfUrl, 'pageIndex': '1'}));
    if (state.currentTool == DrawingTool.select || state.currentTool == DrawingTool.eae) return;

    if (state.currentTool == DrawingTool.eraser) {
      ref.read(workspaceProvider({'workspaceId': widget.pdfUrl, 'pageIndex': '1'}).notifier).eraseAt(details.localPosition);
    } else if (_currentStroke.isNotEmpty) {
      setState(() {
        _currentStroke.add(details.localPosition);
      });
    }
  }

  void _onPanEnd(DragEndDetails details) {
    if (_currentStroke.isNotEmpty) {
      ref.read(workspaceProvider({'workspaceId': widget.pdfUrl, 'pageIndex': '1'}).notifier).addStroke(_currentStroke);
      setState(() {
        _currentStroke = [];
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final provider = workspaceProvider({'workspaceId': widget.pdfUrl, 'pageIndex': '1'});
    final state = ref.watch(provider);
    final notifier = ref.read(provider.notifier);

    if (state.isLoading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    // EAE (Educational Asset Engine) items
    final eaeWidgets = state.objects.where((o) => o.type == 'eae').map((o) {
       return EaeDraggableWidget(assetId: (o as dynamic).assetId, initialPosition: (o as dynamic).position);
    }).toList();

    return Scaffold(
      appBar: AppBar(
        title: const Text('PDF Workspace'),
        actions: [
          IconButton(
            icon: const Icon(Icons.undo),
            onPressed: state.undoHistory.isNotEmpty ? notifier.undo : null,
          ),
          IconButton(
            icon: const Icon(Icons.redo),
            onPressed: state.redoHistory.isNotEmpty ? notifier.redo : null,
          ),
          IconButton(
            icon: const Icon(Icons.map),
            tooltip: 'EAE Görseli Ekle',
            onPressed: () {
              // Simüle edilmiş EAE görseli ekleme (Örn: Türkiye Haritası)
              notifier.addEaeAsset('studyos://assets/geography/turkey_admin/v1', const Offset(100, 100));
            },
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
                    tooltip: 'Select / Pan (PDF Scroll)',
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
                ],
              ),
            ),
          ),
          // Canvas + PDF
          Expanded(
            child: Stack(
              children: [
                // 1. PDF Viewer Layer
                IgnorePointer(
                  // Ignore pointer unless we are in select tool mode
                  ignoring: state.currentTool != DrawingTool.select,
                  child: SfPdfViewer.network(
                    widget.pdfUrl,
                    key: _pdfViewerKey,
                    controller: _pdfViewerController,
                    canShowScrollHead: false,
                    canShowScrollStatus: false,
                  ),
                ),
                // 2. Annotation & Drawing Layer
                if (state.currentTool != DrawingTool.select)
                  GestureDetector(
                    onPanStart: _onPanStart,
                    onPanUpdate: _onPanUpdate,
                    onPanEnd: _onPanEnd,
                    behavior: HitTestBehavior.opaque,
                    child: CustomPaint(
                      painter: CanvasPainter(
                        objects: state.objects.where((o) => o.type != 'eae').toList(),
                        currentStroke: _currentStroke,
                        currentTool: state.currentTool,
                        currentColor: state.currentColor,
                        currentStrokeWidth: state.currentStrokeWidth,
                      ),
                      size: Size.infinite,
                    ),
                  ),
                // 3. EAE Widgets Layer
                ...eaeWidgets,
              ],
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
