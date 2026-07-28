import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// Sprint-3.1.B/C — Preview chips navigate by subject_code.
class DashboardSubjectPreview extends StatelessWidget {
  const DashboardSubjectPreview({
    super.key,
    required this.subjectNames,
    this.subjectCodes = const [],
    this.focusLabels = const [],
  });

  final List<String> subjectNames;
  final List<String> subjectCodes;
  final List<String> focusLabels;

  @override
  Widget build(BuildContext context) {
    final count = subjectNames.length < 5 ? subjectNames.length : 5;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text(
                  'Dersler',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                ),
                const Spacer(),
                TextButton(
                  onPressed: () => context.push('/subjects'),
                  child: const Text('Tüm Dersler'),
                ),
              ],
            ),
            if (focusLabels.isNotEmpty) ...[
              const SizedBox(height: 4),
              Text(
                focusLabels.join(' · '),
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
            const SizedBox(height: 8),
            if (count == 0)
              Text(
                'Henüz ders yok',
                style: Theme.of(context).textTheme.bodyMedium,
              )
            else
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  for (var i = 0; i < count; i++)
                    ActionChip(
                      label: Text(subjectNames[i]),
                      onPressed: () {
                        final code = i < subjectCodes.length
                            ? subjectCodes[i]
                            : null;
                        if (code != null && code.isNotEmpty) {
                          context.push('/subjects/$code');
                        } else {
                          context.push('/subjects');
                        }
                      },
                    ),
                  if (subjectNames.length > count)
                    Chip(
                      label: Text('+${subjectNames.length - count}'),
                    ),
                ],
              ),
          ],
        ),
      ),
    );
  }
}
