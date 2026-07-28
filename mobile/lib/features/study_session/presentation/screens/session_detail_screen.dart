import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../domain/entities/study_session_entity.dart';
import '../../domain/entities/study_session_status.dart';
import '../providers/study_session_provider.dart';

class SessionDetailScreen extends ConsumerStatefulWidget {
  const SessionDetailScreen({super.key, required this.sessionId});

  final String sessionId;

  @override
  ConsumerState<SessionDetailScreen> createState() =>
      _SessionDetailScreenState();
}

class _SessionDetailScreenState extends ConsumerState<SessionDetailScreen> {
  StudySessionEntity? _session;
  String? _error;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final session = await ref
          .read(studySessionRepositoryProvider)
          .getById(widget.sessionId);
      if (!mounted) return;
      setState(() {
        _session = session;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Oturum Detayı')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(_error!),
                      FilledButton(onPressed: _load, child: const Text('Tekrar')),
                    ],
                  ),
                )
              : _DetailBody(session: _session!),
    );
  }
}

class _DetailBody extends StatelessWidget {
  const _DetailBody({required this.session});

  final StudySessionEntity session;

  @override
  Widget build(BuildContext context) {
    final fmt = DateFormat('dd MMMM yyyy HH:mm', 'tr_TR');
    final statusLabel = switch (session.status) {
      StudySessionStatus.completed => 'Tamamlandı',
      StudySessionStatus.running => 'Devam ediyor',
      StudySessionStatus.paused => 'Duraklatıldı',
    };

    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Text(
          session.planTitle ?? 'Serbest çalışma',
          style: Theme.of(context).textTheme.headlineSmall,
        ),
        if (session.planSubject != null) ...[
          const SizedBox(height: 4),
          Text(session.planSubject!),
        ],
        const SizedBox(height: 20),
        _row('Durum', statusLabel),
        _row('Başlangıç', fmt.format(session.startedAt.toLocal())),
        _row(
          'Bitiş',
          session.endedAt == null
              ? '—'
              : fmt.format(session.endedAt!.toLocal()),
        ),
        _row('Planlanan süre', '${session.plannedDurationMinutes} dk'),
        _row('Gerçek süre', '${session.actualDurationMinutes} dk'),
        _row('Çözülen soru', '${session.completedQuestions}'),
        _row('Tamamlanan konu', '${session.completedTopics}'),
      ],
    );
  }

  Widget _row(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 140,
            child: Text(label, style: const TextStyle(fontWeight: FontWeight.w600)),
          ),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }
}
