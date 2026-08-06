import 'package:dio/dio.dart';

import '../../../../core/asset_contracts/asset_manifest_contract.dart';
import '../models/asset_search_query_dto.dart';

abstract class AssetRepository {
  Future<List<EAEAssetManifestContract>> searchAssets(
      AssetSearchQueryDTO query);
  Future<EAEAssetManifestContract> getAssetDetail(String assetDbId);
  Future<List<int>> downloadBundle(String assetDbId);
}

class AssetRepositoryImpl implements AssetRepository {
  final Dio _dio;

  AssetRepositoryImpl(this._dio);

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
    final key = Uri.encodeComponent(assetDbId);
    final response = await _dio.get<List<int>>(
      '/assets/$key/bundle',
      options: Options(responseType: ResponseType.bytes),
    );
    return response.data ?? <int>[];
  }
}
