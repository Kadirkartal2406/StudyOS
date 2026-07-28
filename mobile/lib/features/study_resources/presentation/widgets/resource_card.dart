import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../domain/entities/study_resource_entity.dart';

class ResourceCard extends StatelessWidget {
  const ResourceCard({
    super.key,
    required this.resource,
    required this.onOpen,
    required this.onComplete,
    required this.onDelete,
    this.onEdit,
  });

  final StudyResourceEntity resource;
  final VoidCallback onOpen;
  final VoidCallback onComplete;
  final VoidCallback onDelete;
  final VoidCallback? onEdit;

  IconData get _icon => switch (resource.resourceType) {
        ResourceType.youtube || ResourceType.video => Icons.play_circle_outline,
        ResourceType.pdf || ResourceType.document => Icons.picture_as_pdf_outlined,
        ResourceType.book => Icons.menu_book_outlined,
        ResourceType.audio => Icons.headphones_outlined,
        ResourceType.website => Icons.language,
        ResourceType.note => Icons.sticky_note_2_outlined,
        ResourceType.other => Icons.link,
      };

  String get _durationLabel {
    final s = resource.durationSeconds;
    if (s == null || s <= 0) return '—';
    final m = s ~/ 60;
    final r = s % 60;
    return m > 0 ? '${m}dk ${r}sn' : '${r}sn';
  }

  Future<void> _launch() async {
    final raw = resource.url;
    if (raw == null || raw.isEmpty) return;
    onOpen();
    final uri = Uri.tryParse(raw);
    if (uri == null) return;
    await launchUrl(uri, mode: LaunchMode.externalApplication);
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(_icon, color: scheme.primary),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    resource.title,
                    style: Theme.of(context).textTheme.titleMedium,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                PopupMenuButton<String>(
                  onSelected: (v) {
                    if (v == 'complete') onComplete();
                    if (v == 'delete') onDelete();
                    if (v == 'edit') onEdit?.call();
                  },
                  itemBuilder: (_) => [
                    const PopupMenuItem(value: 'complete', child: Text('Tamamla')),
                    if (onEdit != null)
                      const PopupMenuItem(value: 'edit', child: Text('Düzenle')),
                    const PopupMenuItem(value: 'delete', child: Text('Sil')),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 6),
            Text(
              '${resource.resourceType.label} · ${resource.status.label}'
              ' · $_durationLabel'
              '${resource.provider != null ? ' · ${resource.provider}' : ''}',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            if (resource.url != null && resource.url!.isNotEmpty) ...[
              const SizedBox(height: 8),
              Align(
                alignment: Alignment.centerLeft,
                child: FilledButton.tonalIcon(
                  onPressed: _launch,
                  icon: Icon(
                    resource.isYoutube ? Icons.play_arrow : Icons.open_in_new,
                  ),
                  label: Text(resource.isYoutube ? 'İzle' : 'Aç'),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
