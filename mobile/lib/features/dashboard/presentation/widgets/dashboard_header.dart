import 'package:flutter/material.dart';

import '../../../../core/utils/date_time_helper.dart';

/// Dashboard üst bölümü — saat bazlı karşılama mesajı ve bugünün tarihi.
class DashboardHeader extends StatelessWidget {
  const DashboardHeader({super.key, required this.firstName});

  final String firstName;

  @override
  Widget build(BuildContext context) {
    final now = DateTime.now();
    final colorScheme = Theme.of(context).colorScheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '${DateTimeHelper.greetingFor(now)}, $firstName',
          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.w800,
                color: colorScheme.onSurface,
              ),
        ),
        const SizedBox(height: 4),
        Text(
          DateTimeHelper.formatFullDate(now),
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: colorScheme.onSurfaceVariant,
              ),
        ),
      ],
    );
  }
}
