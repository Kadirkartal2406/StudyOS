import 'package:flutter/material.dart';

/// Sprint-3.1.C — visual filter cue when opened from Subject Hub.
class SubjectCodeChip extends StatelessWidget {
  const SubjectCodeChip({super.key, required this.subjectCode});

  final String subjectCode;

  @override
  Widget build(BuildContext context) {
    if (subjectCode.isEmpty) return const SizedBox.shrink();
    return Chip(
      visualDensity: VisualDensity.compact,
      label: Text(subjectCode),
      avatar: const Icon(Icons.menu_book_outlined, size: 16),
    );
  }
}
