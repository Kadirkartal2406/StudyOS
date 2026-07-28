import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../domain/entities/memory_entity.dart';
import '../providers/memory_provider.dart';
import '../providers/memory_state.dart';

/// Bellek ekle / düzenle — Sprint-2.3
class MemoryFormScreen extends ConsumerStatefulWidget {
  const MemoryFormScreen({super.key, this.memoryId});

  final String? memoryId;

  @override
  ConsumerState<MemoryFormScreen> createState() => _MemoryFormScreenState();
}

class _MemoryFormScreenState extends ConsumerState<MemoryFormScreen> {
  final _contentCtrl = TextEditingController();
  MemoryCategory _category = MemoryCategory.custom;
  double _importance = 0.5;
  bool _saving = false;
  bool _loaded = false;

  bool get _isEdit => widget.memoryId != null;

  @override
  void dispose() {
    _contentCtrl.dispose();
    super.dispose();
  }

  void _hydrateFromState() {
    if (_loaded || !_isEdit) return;
    final state = ref.read(memoryProvider);
    if (state is! MemoryLoaded) return;
    MemoryEntity? mem;
    for (final item in state.items) {
      if (item.id == widget.memoryId) {
        mem = item;
        break;
      }
    }
    if (mem == null) return;
    _contentCtrl.text = mem.content;
    _category = mem.category;
    _importance = mem.importance;
    _loaded = true;
  }

  Future<void> _save() async {
    final content = _contentCtrl.text.trim();
    if (content.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('İçerik zorunlu')),
      );
      return;
    }
    setState(() => _saving = true);
    final notifier = ref.read(memoryProvider.notifier);
    final ok = _isEdit
        ? await notifier.update(
            id: widget.memoryId!,
            category: _category,
            content: content,
            importance: _importance,
          )
        : await notifier.create(
            category: _category,
            content: content,
            importance: _importance,
          );
    if (!mounted) return;
    setState(() => _saving = false);
    if (ok) context.pop();
  }

  @override
  Widget build(BuildContext context) {
    _hydrateFromState();

    return Scaffold(
      appBar: AppBar(
        title: Text(_isEdit ? 'Belleği düzenle' : 'Bellek ekle'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          DropdownButtonFormField<MemoryCategory>(
            value: _category,
            decoration: const InputDecoration(
              labelText: 'Kategori',
              border: OutlineInputBorder(),
            ),
            items: MemoryCategory.values
                .map(
                  (c) => DropdownMenuItem(value: c, child: Text(c.label)),
                )
                .toList(),
            onChanged: (v) {
              if (v != null) setState(() => _category = v);
            },
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _contentCtrl,
            maxLines: 5,
            maxLength: 2000,
            decoration: const InputDecoration(
              labelText: 'İçerik',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 8),
          Text('Önem: ${(_importance * 100).round()}%'),
          Slider(
            value: _importance,
            onChanged: (v) => setState(() => _importance = v),
          ),
          const SizedBox(height: 16),
          FilledButton(
            onPressed: _saving ? null : _save,
            child: _saving
                ? const SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : Text(_isEdit ? 'Kaydet' : 'Oluştur'),
          ),
        ],
      ),
    );
  }
}
