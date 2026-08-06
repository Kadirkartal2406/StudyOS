/// DTO for asset search queries on Flutter mobile app.

class AssetSearchQueryDTO {
  final String? query;
  final String? domain;
  final String? tag;
  final int page;
  final int pageSize;

  const AssetSearchQueryDTO({
    this.query,
    this.domain,
    this.tag,
    this.page = 1,
    this.pageSize = 20,
  });

  Map<String, String> toQueryParameters() {
    final params = <String, String>{
      'page': page.toString(),
      'page_size': pageSize.toString(),
    };
    if (query != null && query!.isNotEmpty) params['q'] = query!;
    if (domain != null && domain!.isNotEmpty) params['domain'] = domain!;
    if (tag != null && tag!.isNotEmpty) params['tag'] = tag!;
    return params;
  }
}
