import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../subjects/presentation/widgets/subject_code_chip.dart';
import '../../domain/entities/study_resource_entity.dart';
import '../providers/study_resource_provider.dart';
import '../providers/study_resource_state.dart';
import '../widgets/resource_card.dart';

/// Kaynak listesi — plan bağlı, konu bağlı veya global.
class ResourcesScreen extends ConsumerWidget {
  const ResourcesScreen({
    super.key,
    this.studyPlanId,
    this.planTitle,
    this.subjectCode,
    this.topicCode,
  });

  final String? studyPlanId;
  final String? planTitle;

  /// Subject bağlamı — null ise global (tüm kaynaklar).
  final String? subjectCode;

  /// Topic bağlamı — opsiyonel.
  final String? topicCode;

  ResourceKey get _key =>
      (planId: studyPlanId, subjectCode: subjectCode, topicCode: topicCode);

  String get _title {
    if (planTitle != null) return 'Kaynaklar · $planTitle';
    if (topicCode != null && topicCode!.isNotEmpty) {
      return 'Konu kaynakları';
    }
    if (subjectCode != null && subjectCode!.isNotEmpty) {
      return '${subjectCode!.toUpperCase()} Kaynakları';
    }
    return 'Kaynaklar';
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(studyResourceProvider(_key));

    return Scaffold(
      appBar: AppBar(
        title: Text(_title),
        actions: [
          if (subjectCode != null && subjectCode!.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(right: 4),
              child: SubjectCodeChip(subjectCode: subjectCode!),
            ),
          IconButton(
            tooltip: 'İstatistik',
            onPressed: () => Navigator.of(context).push(
              MaterialPageRoute<void>(
                builder: (_) => _StatsPlaceholder(resourceKey: _key),
              ),
            ),
            icon: const Icon(Icons.bar_chart_outlined),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showAddSheet(context, ref),
        icon: const Icon(Icons.add),
        label: const Text('Ekle'),
      ),
      body: switch (state) {
        StudyResourceInitial() || StudyResourceLoading() => const Center(
            child: CircularProgressIndicator(),
          ),
        StudyResourceError(:final message) => Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(message),
                const SizedBox(height: 12),
                FilledButton(
                  onPressed: () =>
                      ref.read(studyResourceProvider(_key).notifier).load(),
                  child: const Text('Tekrar Dene'),
                ),
              ],
            ),
          ),
        StudyResourceLoaded(
          :final items,
          :final errorMessage,
          :final statistics,
        ) =>
          RefreshIndicator(
            onRefresh: () =>
                ref.read(studyResourceProvider(_key).notifier).load(),
            child: ListView(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 96),
              children: [
                if (errorMessage != null)
                  Text(
                    errorMessage,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.error,
                    ),
                  ),
                if (statistics != null)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: Text(
                      'Toplam ${statistics.totalCount} · '
                      'Tamamlanan ${statistics.completedCount} · '
                      'Bugün açılan ${statistics.todayOpenedCount}',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ),
                if (items.isEmpty)
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: 48),
                    child: Center(
                      child: Text(
                        topicCode != null && topicCode!.isNotEmpty
                            ? 'Bu konu için henüz kaynak yok.\nEkle ile PDF, YouTube veya link ekleyebilirsin.'
                            : subjectCode != null
                                ? 'Bu ders için henüz kaynak yok.'
                                : 'Henüz kaynak yok.',
                        textAlign: TextAlign.center,
                      ),
                    ),
                  )
                else
                  ...items.map(
                    (r) => ResourceCard(
                      resource: r,
                      onOpen: () => ref
                          .read(studyResourceProvider(_key).notifier)
                          .open(r.id),
                      onComplete: () => ref
                          .read(studyResourceProvider(_key).notifier)
                          .setStatus(r.id, ResourceStatus.completed),
                      onDelete: () => ref
                          .read(studyResourceProvider(_key).notifier)
                          .delete(r.id),
                    ),
                  ),
              ],
            ),
          ),
      },
    );
  }

  Future<void> _showAddSheet(BuildContext context, WidgetRef ref) async {
    final titleCtrl = TextEditingController();
    final urlCtrl = TextEditingController();
    var inputMode = _ResourceInputMode.link;
    var type = ResourceType.youtube;
    PlatformFile? selectedFile;
    var isUploading = false;

    final finalUrl = await showModalBottomSheet<String>(
      context: context,
      isScrollControlled: true,
      builder: (ctx) {
        return Padding(
          padding: EdgeInsets.only(
            left: 16,
            right: 16,
            top: 16,
            bottom: MediaQuery.of(ctx).viewInsets.bottom + 16,
          ),
          child: StatefulBuilder(
            builder: (ctx, setLocal) {
              return SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      'Kaynak ekle',
                      style: Theme.of(ctx).textTheme.titleLarge,
                    ),
                    if (subjectCode != null && subjectCode!.isNotEmpty) ...[
                      const SizedBox(height: 4),
                      Text(
                        topicCode != null && topicCode!.isNotEmpty
                            ? '${subjectCode!.toUpperCase()} - ${topicCode!} konusuna eklenecek'
                            : '${subjectCode!.toUpperCase()} dersine eklenecek',
                        style: Theme.of(ctx).textTheme.bodySmall?.copyWith(
                              color: Theme.of(ctx).colorScheme.onSurfaceVariant,
                            ),
                      ),
                    ],
                    const SizedBox(height: 12),
                    SegmentedButton<_ResourceInputMode>(
                      segments: const [
                        ButtonSegment(
                          value: _ResourceInputMode.link,
                          icon: Icon(Icons.link),
                          label: Text('Bağlantı ekle'),
                        ),
                        ButtonSegment(
                          value: _ResourceInputMode.device,
                          icon: Icon(Icons.upload_file),
                          label: Text('Cihazdan ekle'),
                        ),
                      ],
                      selected: {inputMode},
                      onSelectionChanged: (selection) {
                        setLocal(() {
                          inputMode = selection.first;
                          type = inputMode == _ResourceInputMode.link
                              ? ResourceType.youtube
                              : ResourceType.pdf;
                          selectedFile = null;
                          urlCtrl.clear();
                        });
                      },
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: titleCtrl,
                      decoration: const InputDecoration(
                        labelText: 'Başlık',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 8),
                    DropdownButtonFormField<ResourceType>(
                      key: ValueKey((inputMode, type)),
                      initialValue: type,
                      decoration: const InputDecoration(
                        labelText: 'Tür',
                        border: OutlineInputBorder(),
                      ),
                      items: (inputMode == _ResourceInputMode.link
                              ? const [
                                  ResourceType.youtube,
                                  ResourceType.website,
                                ]
                              : const [
                                  ResourceType.pdf,
                                  ResourceType.audio,
                                  ResourceType.video,
                                  ResourceType.document,
                                  ResourceType.book,
                                  ResourceType.note,
                                  ResourceType.other,
                                ])
                          .map(
                            (t) => DropdownMenuItem(
                              value: t,
                              child: Text(t.label),
                            ),
                          )
                          .toList(),
                      onChanged: (v) {
                        if (v != null) {
                          setLocal(() {
                            type = v;
                            selectedFile = null;
                            urlCtrl.clear();
                          });
                        }
                      },
                    ),
                    const SizedBox(height: 12),
                    if (inputMode == _ResourceInputMode.link)
                      TextField(
                        controller: urlCtrl,
                        keyboardType: TextInputType.url,
                        autocorrect: false,
                        decoration: InputDecoration(
                          labelText: type == ResourceType.youtube
                              ? 'URL (YouTube linki)'
                              : 'Web URL',
                          prefixIcon: const Icon(Icons.link),
                          border: const OutlineInputBorder(),
                        ),
                      )
                    else
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          OutlinedButton.icon(
                            icon: const Icon(Icons.upload_file),
                            label: Text(
                              selectedFile?.name ?? _filePickerLabel(type),
                            ),
                            onPressed: () async {
                              final result = await FilePicker.pickFiles(
                                withData: true,
                              );
                              if (result != null && result.files.isNotEmpty) {
                                setLocal(
                                  () => selectedFile = result.files.first,
                                );
                              }
                            },
                          ),
                          if (selectedFile != null) ...[
                            const SizedBox(height: 6),
                            Text(
                              '${selectedFile!.name} · ${_formatFileSize(selectedFile!.size)}',
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: Theme.of(ctx).textTheme.bodySmall,
                            ),
                          ],
                        ],
                      ),
                    const SizedBox(height: 16),
                    FilledButton(
                      onPressed: isUploading
                          ? null
                          : () async {
                              var url = urlCtrl.text.trim();
                              if (inputMode == _ResourceInputMode.link &&
                                  url.isEmpty) {
                                ScaffoldMessenger.of(ctx).showSnackBar(
                                  const SnackBar(
                                    content:
                                        Text('Lütfen bir bağlantı girin.'),
                                  ),
                                );
                                return;
                              }
                              if (inputMode == _ResourceInputMode.device) {
                                if (selectedFile == null) {
                                  ScaffoldMessenger.of(ctx).showSnackBar(
                                    const SnackBar(
                                      content: Text('Lütfen bir dosya seçin.'),
                                    ),
                                  );
                                  return;
                                }
                                final hasBytes = selectedFile!.bytes != null;
                                final hasPath = selectedFile!.path != null &&
                                    selectedFile!.path!.isNotEmpty;
                                if (!hasBytes && !hasPath) {
                                  ScaffoldMessenger.of(ctx).showSnackBar(
                                    const SnackBar(
                                      content: Text(
                                        'Dosya okunamadı. Daha küçük bir dosya deneyin.',
                                      ),
                                    ),
                                  );
                                  return;
                                }
                                setLocal(() => isUploading = true);
                                try {
                                  final repo = ref.read(
                                    studyResourceRepositoryProvider,
                                  );
                                  url = await repo.uploadResourceFile(
                                    selectedFile!.bytes ?? const <int>[],
                                    selectedFile!.name,
                                    filePath: selectedFile!.path,
                                  );
                                } catch (e) {
                                  setLocal(() => isUploading = false);
                                  if (ctx.mounted) {
                                    ScaffoldMessenger.of(ctx).showSnackBar(
                                      SnackBar(
                                        content: Text('Yükleme hatası: $e'),
                                      ),
                                    );
                                  }
                                  return;
                                }
                              }

                              if (ctx.mounted) {
                                Navigator.pop(ctx, url);
                              }
                            },
                      child: isUploading
                          ? const SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Text('Kaydet'),
                    ),
                  ],
                ),
              );
            },
          ),
        );
      },
    );

    if (finalUrl != null && context.mounted) {
      await ref.read(studyResourceProvider(_key).notifier).create(
            title: titleCtrl.text.trim().isEmpty
                ? 'Kaynak'
                : titleCtrl.text.trim(),
            resourceType: type,
            url: finalUrl.isEmpty ? null : finalUrl,
          );
    }
    titleCtrl.dispose();
    urlCtrl.dispose();
  }
}

enum _ResourceInputMode { link, device }

String _filePickerLabel(ResourceType type) => switch (type) {
      ResourceType.pdf => 'Cihazdan PDF seç',
      ResourceType.audio => 'Cihazdan ses dosyası seç',
      ResourceType.video => 'Cihazdan video seç',
      ResourceType.document => 'Cihazdan doküman seç',
      _ => 'Cihazdan dosya seç',
    };

String _formatFileSize(int bytes) {
  if (bytes < 1024) return '$bytes B';
  final kilobytes = bytes / 1024;
  if (kilobytes < 1024) return '${kilobytes.toStringAsFixed(1)} KB';
  return '${(kilobytes / 1024).toStringAsFixed(1)} MB';
}

class _StatsPlaceholder extends ConsumerWidget {
  const _StatsPlaceholder({required ResourceKey resourceKey})
      : _key = resourceKey;

  final ResourceKey _key;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(studyResourceProvider(_key));
    final stats = state is StudyResourceLoaded ? state.statistics : null;

    return Scaffold(
      appBar: AppBar(title: const Text('Kaynak istatistikleri')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: stats == null
            ? const Text('Veri yok')
            : Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Toplam: ${stats.totalCount}'),
                  Text('Tamamlanan: ${stats.completedCount}'),
                  Text('Devam: ${stats.inProgressCount}'),
                  Text('Bugün açılan: ${stats.todayOpenedCount}'),
                  Text('Bugün tamamlanan: ${stats.todayCompletedCount}'),
                  Text('Video süresi (sn): ${stats.totalVideoDurationSeconds}'),
                  const SizedBox(height: 12),
                  const Text('Tür dağılımı:'),
                  ...stats.byType.entries.map(
                    (e) => Text('${e.key}: ${e.value}'),
                  ),
                ],
              ),
      ),
    );
  }
}
