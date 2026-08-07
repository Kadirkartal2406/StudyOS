import 'package:flutter/material.dart';

abstract class AnnotationObject {
  final String id;
  
  AnnotationObject({required this.id});
  
  String get type;
  
  Map<String, dynamic> toJson();
  
  static AnnotationObject fromJson(Map<String, dynamic> json) {
    final type = json['type'] as String?;
    switch (type) {
      case 'stroke':
        return StrokeObject.fromJson(json);
      case 'text':
        return TextObject.fromJson(json);
      case 'eae':
        return EaeObject.fromJson(json);
      default:
        throw Exception('Unknown AnnotationObject type: $type');
    }
  }
}

class StrokeObject extends AnnotationObject {
  final List<Offset> points;
  final Color color;
  final double strokeWidth;

  StrokeObject({
    required super.id,
    required this.points,
    required this.color,
    required this.strokeWidth,
  });

  @override
  String get type => 'stroke';

  @override
  Map<String, dynamic> toJson() => {
        'id': id,
        'type': 'stroke',
        'points': points.map((p) => {'x': p.dx, 'y': p.dy}).toList(),
        'color': color.value,
        'strokeWidth': strokeWidth,
      };

  factory StrokeObject.fromJson(Map<String, dynamic> json) {
    final pts = (json['points'] as List).map((p) => Offset((p['x'] as num).toDouble(), (p['y'] as num).toDouble())).toList();
    return StrokeObject(
      id: json['id'] as String,
      points: pts,
      color: Color(json['color'] as int),
      strokeWidth: (json['strokeWidth'] as num).toDouble(),
    );
  }
}

class TextObject extends AnnotationObject {
  final String text;
  final Offset position;
  final Color color;
  final double fontSize;

  TextObject({
    required super.id,
    required this.text,
    required this.position,
    required this.color,
    required this.fontSize,
  });

  @override
  String get type => 'text';

  @override
  Map<String, dynamic> toJson() => {
        'id': id,
        'type': 'text',
        'text': text,
        'position': {'x': position.dx, 'y': position.dy},
        'color': color.value,
        'fontSize': fontSize,
      };

  factory TextObject.fromJson(Map<String, dynamic> json) {
    final p = json['position'] as Map<String, dynamic>;
    return TextObject(
      id: json['id'] as String,
      text: json['text'] as String,
      position: Offset((p['x'] as num).toDouble(), (p['y'] as num).toDouble()),
      color: Color(json['color'] as int),
      fontSize: (json['fontSize'] as num).toDouble(),
    );
  }
}

class EaeObject extends AnnotationObject {
  final String assetId;
  final Offset position;
  final double scale;

  EaeObject({
    required super.id,
    required this.assetId,
    required this.position,
    this.scale = 1.0,
  });

  @override
  String get type => 'eae';

  @override
  Map<String, dynamic> toJson() => {
        'id': id,
        'type': 'eae',
        'assetId': assetId,
        'position': {'x': position.dx, 'y': position.dy},
        'scale': scale,
      };

  factory EaeObject.fromJson(Map<String, dynamic> json) {
    final p = json['position'] as Map<String, dynamic>;
    return EaeObject(
      id: json['id'] as String,
      assetId: json['assetId'] as String,
      position: Offset((p['x'] as num).toDouble(), (p['y'] as num).toDouble()),
      scale: (json['scale'] as num).toDouble(),
    );
  }
}
