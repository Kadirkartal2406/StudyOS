import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/theme/app_spacing.dart';

class MapsListScreen extends StatelessWidget {
  const MapsListScreen({super.key});

  static const Map<String, String> _availableMaps = {
    'Siyasi Harita (İdari)': 'studyos://assets/geography/turkey_admin/v1',
    'Fiziki Harita': 'studyos://assets/geography/turkey_physical/v1',
    'Hidrografya (Akarsular)': 'studyos://assets/geography/turkey_hydrography/v1',
    'İklim': 'studyos://assets/geography/turkey_climate/v1',
    'Bitki Örtüsü': 'studyos://assets/geography/turkey_vegetation/v1',
    'Tarım': 'studyos://assets/geography/turkey_agriculture/v1',
    'Madencilik': 'studyos://assets/geography/turkey_minerals/v1',
    'Enerji': 'studyos://assets/geography/turkey_energy/v1',
    'Nüfus': 'studyos://assets/geography/turkey_population/v1',
    'Ulaşım': 'studyos://assets/geography/turkey_transport/v1',
    'Turizm': 'studyos://assets/geography/turkey_tourism/v1',
    'Afetler': 'studyos://assets/geography/turkey_hazards/v1',
  };

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Haritalar'),
      ),
      body: ListView.builder(
        padding: AppSpacing.pageWide,
        itemCount: _availableMaps.length,
        itemBuilder: (context, index) {
          final entry = _availableMaps.entries.elementAt(index);
          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            child: ListTile(
              leading: Icon(
                Icons.folder_shared_outlined,
                color: Theme.of(context).colorScheme.primary,
                size: 28,
              ),
              title: Text(
                entry.key,
                style: const TextStyle(fontWeight: FontWeight.w600),
              ),
              trailing: const Icon(Icons.chevron_right_rounded),
              onTap: () {
                context.push('/maps/view?uri=${Uri.encodeComponent(entry.value)}&title=${Uri.encodeComponent(entry.key)}');
              },
            ),
          );
        },
      ),
    );
  }
}
