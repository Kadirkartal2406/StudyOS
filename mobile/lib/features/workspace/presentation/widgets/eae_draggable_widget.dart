import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../asset_engine/providers/eae_render_provider.dart';
import '../../../../core/asset_engine/asset_bundle_decoder.dart';
import '../../../../shared/widgets/eae_vector_canvas_widget.dart';
import '../../../educational_assets/data/models/asset_search_query_dto.dart';
import '../../../educational_assets/providers/asset_search_provider.dart';

class EaeDraggableWidget extends ConsumerStatefulWidget {
  final String assetId;
  final Offset initialPosition;

  const EaeDraggableWidget({
    super.key,
    required this.assetId,
    required this.initialPosition,
  });

  @override
  ConsumerState<EaeDraggableWidget> createState() => _EaeDraggableWidgetState();
}

class _EaeDraggableWidgetState extends ConsumerState<EaeDraggableWidget> {
  Offset _position = Offset.zero;
  double _scale = 1.0;
  bool _loading = true;
  String? _svgContent;
  dynamic _manifest;

  @override
  void initState() {
    super.initState();
    _position = widget.initialPosition;
    _loadAsset();
  }

  Future<void> _loadAsset() async {
    try {
      final repo = ref.read(assetRepositoryProvider);
      final bytes = await repo.downloadBundle(widget.assetId);
      final decoded = EAEAssetBundleDecoder.decodeBundleBytes(bytes);
      
      if (mounted) {
        setState(() {
          _manifest = decoded.manifest;
          _svgContent = decoded.svgContent;
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _loading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return Positioned(
        left: _position.dx,
        top: _position.dy,
        child: const SizedBox(
          width: 50,
          height: 50,
          child: CircularProgressIndicator(),
        ),
      );
    }

    if (_manifest == null || _svgContent == null) {
      return Positioned(
        left: _position.dx,
        top: _position.dy,
        child: Container(
          color: Colors.red[100],
          padding: const EdgeInsets.all(8),
          child: const Text('EAE Yüklenemedi'),
        ),
      );
    }

    return Positioned(
      left: _position.dx,
      top: _position.dy,
      child: GestureDetector(
        onScaleUpdate: (details) {
          setState(() {
            _position += details.focalPointDelta;
            _scale *= details.scale;
            // Prevent going too small
            if (_scale < 0.2) _scale = 0.2;
          });
        },
        child: Transform.scale(
          scale: _scale,
          child: Container(
            width: 300, // Default bounding box for EAE
            height: 300,
            decoration: BoxDecoration(
              border: Border.all(color: Colors.blue.withOpacity(0.5), width: 2),
              color: Colors.white,
            ),
            child: EAEVectorCanvasWidget(
              manifest: _manifest,
              svgContent: _svgContent!,
              enableMultiSelect: false,
            ),
          ),
        ),
      ),
    );
  }
}
