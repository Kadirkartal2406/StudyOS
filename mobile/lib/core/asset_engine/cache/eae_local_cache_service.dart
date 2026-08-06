import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:path_provider/path_provider.dart';
import 'package:logger/logger.dart';

class EAELocalCacheService {
  final Logger _logger = Logger();
  
  String _sanitizeKey(String uri) {
    return uri.replaceAll(RegExp(r'[^a-zA-Z0-9_-]'), '_');
  }

  Future<File?> _getCacheFile(String uri) async {
    if (kIsWeb) return null; // dart:io File unsupported on Web
    try {
      final dir = await getApplicationDocumentsDirectory();
      final sanitized = _sanitizeKey(uri);
      return File('${dir.path}/eae_cache_$sanitized.zlib');
    } catch (e) {
      return null;
    }
  }

  Future<List<int>?> getCachedBundle(String uri) async {
    if (kIsWeb) return null;
    
    try {
      final file = await _getCacheFile(uri);
      if (file != null && await file.exists()) {
        _logger.i('EAE Cache HIT: $uri');
        return await file.readAsBytes();
      }
    } catch (e) {
      _logger.e('Failed to read cached EAE bundle for $uri', error: e);
    }
    return null;
  }

  Future<void> saveBundleToCache(String uri, List<int> bytes) async {
    if (kIsWeb) return;
    
    try {
      final file = await _getCacheFile(uri);
      if (file != null) {
        await file.writeAsBytes(bytes);
        _logger.i('EAE Cache SAVED: $uri (${bytes.length} bytes)');
      }
    } catch (e) {
      _logger.e('Failed to save EAE bundle to cache for $uri', error: e);
    }
  }
}
