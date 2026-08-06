import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/asset_contracts/asset_manifest_contract.dart';
import '../../../../core/network/dio_client.dart';
import '../../data/models/asset_search_query_dto.dart';
import '../../data/repositories/asset_repository.dart';

final assetRepositoryProvider = Provider<AssetRepository>((ref) {
  final dio = ref.watch(dioClientProvider);
  return AssetRepositoryImpl(dio);
});

final assetSearchQueryProvider = StateProvider<AssetSearchQueryDTO>((ref) {
  return const AssetSearchQueryDTO();
});

final assetSearchResultsProvider =
    FutureProvider<List<EAEAssetManifestContract>>((ref) async {
  final repository = ref.watch(assetRepositoryProvider);
  final query = ref.watch(assetSearchQueryProvider);
  return repository.searchAssets(query);
});

final assetDetailProvider =
    FutureProvider.family<EAEAssetManifestContract, String>(
        (ref, assetDbId) async {
  final repository = ref.watch(assetRepositoryProvider);
  return repository.getAssetDetail(assetDbId);
});
