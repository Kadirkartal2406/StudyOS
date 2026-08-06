import 'package:dio/dio.dart';
import 'package:flutter/services.dart';

import '../../../../core/asset_contracts/asset_manifest_contract.dart';
import '../models/asset_search_query_dto.dart';

import '../../../../core/asset_engine/cache/eae_local_cache_service.dart';

abstract class AssetRepository {
  Future<List<EAEAssetManifestContract>> searchAssets(
      AssetSearchQueryDTO query);
  Future<EAEAssetManifestContract> getAssetDetail(String assetDbId);
  Future<List<int>> downloadBundle(String assetDbId);
}

class AssetRepositoryImpl implements AssetRepository {
  final Dio _dio;
  final EAELocalCacheService _cacheService;

  AssetRepositoryImpl(this._dio, this._cacheService);

  @override
  Future<List<EAEAssetManifestContract>> searchAssets(
      AssetSearchQueryDTO query) async {
    final response = await _dio.get(
      '/assets/search',
      queryParameters: query.toQueryParameters(),
    );

    final data = response.data['data'] as List<dynamic>? ?? [];
    // Search returns list DTOs without layers/viewport — map to minimal manifests.
    return data.map((e) {
      final m = Map<String, dynamic>.from(e as Map<String, dynamic>);
      m.putIfAbsent('schema_version', () => '1.0');
      m.putIfAbsent(
        'viewport',
        () => {
          'width': 1000.0,
          'height': 480.0,
          'default_scale': 1.0,
          'max_scale': 12.0,
        },
      );
      m.putIfAbsent('layers', () => <dynamic>[]);
      m.putIfAbsent('format', () => 'svg');
      return EAEAssetManifestContract.fromJson(m);
    }).toList();
  }

  @override
  Future<EAEAssetManifestContract> getAssetDetail(String assetDbId) async {
    final key = Uri.encodeComponent(assetDbId);
    final response = await _dio.get('/assets/$key');
    final data = response.data['data'] as Map<String, dynamic>;
    return EAEAssetManifestContract.fromJson(data);
  }

  @override
  Future<List<int>> downloadBundle(String assetDbId) async {
    // 0. Try to load from offline embedded assets (geography maps)
    if (assetDbId.startsWith('studyos://assets/geography/')) {
      final parts = assetDbId.split('/');
      if (parts.length >= 5) {
        final mapName = parts[4]; // e.g., 'turkey_admin'
        try {
          final byteData = await rootBundle.load('assets/geography/$mapName.eae');
          return byteData.buffer.asUint8List();
        } catch (_) {
          // Ignore and fallback to cache or API
        }
      }
    }

    // 1. Try to read from local cache first
    final cachedBytes = await _cacheService.getCachedBundle(assetDbId);
    if (cachedBytes != null) {
      return cachedBytes;
    }

    // 2. If not in cache, download from API
    final key = Uri.encodeComponent(assetDbId);
    final response = await _dio.get<List<int>>(
      '/assets/$key/bundle',
      options: Options(responseType: ResponseType.bytes),
    );
    
    final bytes = response.data ?? <int>[];
    
    // 3. Save to cache asynchronously
    if (bytes.isNotEmpty) {
      _cacheService.saveBundleToCache(assetDbId, bytes);
    }
    
    return bytes;
  }
}
