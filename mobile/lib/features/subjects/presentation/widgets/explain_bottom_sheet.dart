import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/network/dio_client.dart';

final explainProvider = FutureProvider.autoDispose.family<String, ({String subjectCode, String topicCode})>(
  (ref, key) async {
    final dio = ref.watch(dioClientProvider);
    final response = await dio.post<Map<String, dynamic>>(
      ApiEndpoints.topicExplain(key.subjectCode, key.topicCode),
      data: {'trigger': 'user_request'},
    );
    final data = response.data;
    if (data == null || data['data'] == null) {
      throw Exception('Invalid Explain response');
    }
    return data['data']['explanation'] as String;
  },
);

class ExplainBottomSheet extends ConsumerWidget {
  const ExplainBottomSheet({
    super.key,
    required this.subjectCode,
    required this.topicCode,
  });

  final String subjectCode;
  final String topicCode;

  static Future<void> show(BuildContext context, String subjectCode, String topicCode) {
    return showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => ExplainBottomSheet(
        subjectCode: subjectCode,
        topicCode: topicCode,
      ),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final key = (subjectCode: subjectCode, topicCode: topicCode);
    final async = ref.watch(explainProvider(key));

    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.auto_awesome, color: Colors.blue),
                const SizedBox(width: 8),
                Text(
                  'Konu Açıklaması',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                ),
                const Spacer(),
                CloseButton(onPressed: () => Navigator.pop(context)),
              ],
            ),
            const SizedBox(height: 16),
            async.when(
              loading: () => const Center(
                child: Padding(
                  padding: EdgeInsets.all(32),
                  child: CircularProgressIndicator(),
                ),
              ),
              error: (e, _) => Padding(
                padding: const EdgeInsets.all(16),
                child: Text('Açıklama üretilemedi: $e',
                    style: TextStyle(color: Theme.of(context).colorScheme.error)),
              ),
              data: (explanation) => Container(
                constraints: BoxConstraints(
                  maxHeight: MediaQuery.of(context).size.height * 0.6,
                ),
                child: SingleChildScrollView(
                  child: Text(
                    explanation,
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                          height: 1.5,
                        ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
