import 'package:flutter/material.dart';

import '../../../../core/extensions/date_time_extensions.dart';

/// Gün seçici — seçilen tarihin etrafındaki 7 günü gösterir; "Bugün" butonu
/// seçili gün bugün değilse görünür.
class DateSelector extends StatelessWidget {
  const DateSelector({
    super.key,
    required this.selectedDate,
    required this.onDateSelected,
    required this.onTodayPressed,
  });

  final DateTime selectedDate;
  final ValueChanged<DateTime> onDateSelected;
  final VoidCallback onTodayPressed;

  static const _weekdayShort = ['Pt', 'Sa', 'Ça', 'Pe', 'Cu', 'Ct', 'Pz'];

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final days = List.generate(
      7,
      (i) => selectedDate.subtract(Duration(days: 3 - i)),
    );

    return Row(
      children: [
        Expanded(
          child: SizedBox(
            height: 68,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              itemCount: days.length,
              separatorBuilder: (_, __) => const SizedBox(width: 8),
              itemBuilder: (context, index) {
                final day = days[index];
                final isSelected = day.isSameDay(selectedDate);
                final isToday = day.isToday;

                return _DateChip(
                  day: day,
                  weekdayLabel: _weekdayShort[day.weekday - 1],
                  isSelected: isSelected,
                  isToday: isToday,
                  onTap: () => onDateSelected(day),
                );
              },
            ),
          ),
        ),
        if (!selectedDate.isToday) ...[
          const SizedBox(width: 8),
          IconButton.filledTonal(
            tooltip: 'Bugün',
            onPressed: onTodayPressed,
            icon: Icon(Icons.today_rounded, color: colorScheme.primary),
          ),
        ],
      ],
    );
  }
}

class _DateChip extends StatelessWidget {
  const _DateChip({
    required this.day,
    required this.weekdayLabel,
    required this.isSelected,
    required this.isToday,
    required this.onTap,
  });

  final DateTime day;
  final String weekdayLabel;
  final bool isSelected;
  final bool isToday;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(14),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        width: 52,
        padding: const EdgeInsets.symmetric(vertical: 10),
        decoration: BoxDecoration(
          color: isSelected
              ? colorScheme.primary
              : colorScheme.surfaceContainerHighest,
          borderRadius: BorderRadius.circular(14),
          border: isToday && !isSelected
              ? Border.all(color: colorScheme.primary, width: 1.5)
              : null,
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              weekdayLabel,
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: isSelected
                    ? colorScheme.onPrimary
                    : colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              '${day.day}',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w800,
                color:
                    isSelected ? colorScheme.onPrimary : colorScheme.onSurface,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
