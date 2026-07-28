// StudyOS — Topic Notebook Entity (AI Sprint FAZ 2)
// Karar vermez; LOS verilerini sunar.
class NotebookResourceItem {
  final String title;
  final String resourceType;
  final String status;
  final String? url;
  final String? provider;

  const NotebookResourceItem({
    required this.title,
    required this.resourceType,
    required this.status,
    this.url,
    this.provider,
  });

  factory NotebookResourceItem.fromJson(Map<String, dynamic> json) =>
      NotebookResourceItem(
        title: json['title'] as String? ?? '',
        resourceType: json['resource_type'] as String? ?? 'other',
        status: json['status'] as String? ?? 'not_started',
        url: json['url'] as String?,
        provider: json['provider'] as String?,
      );
}

class TopicNotebookEntity {
  final String topicCode;
  final String subjectCode;
  final String? topicName;
  final String confidenceLevel;
  final double beliefPct;
  final String trend;
  final bool needsExplain;
  final int sampleCount;
  final double? accuracyPct;
  final double effortMinutes;
  final int resourceCount;
  final List<NotebookResourceItem> resources;
  final bool explainAvailable;
  final bool quizAvailable;
  final String quizDifficulty;
  final bool knowledgeReady;
  final String? knowledgeSummary;
  final int knowledgeChunkCount;
  final int knowledgeCitationCount;
  final String displayTitle;

  const TopicNotebookEntity({
    required this.topicCode,
    required this.subjectCode,
    this.topicName,
    required this.confidenceLevel,
    required this.beliefPct,
    required this.trend,
    required this.needsExplain,
    required this.sampleCount,
    this.accuracyPct,
    required this.effortMinutes,
    required this.resourceCount,
    required this.resources,
    required this.explainAvailable,
    required this.quizAvailable,
    required this.quizDifficulty,
    this.knowledgeReady = false,
    this.knowledgeSummary,
    this.knowledgeChunkCount = 0,
    this.knowledgeCitationCount = 0,
    this.displayTitle = 'Kaynak özeti',
  });

  factory TopicNotebookEntity.fromJson(Map<String, dynamic> json) =>
      TopicNotebookEntity(
        topicCode: json['topic_code'] as String? ?? '',
        subjectCode: json['subject_code'] as String? ?? '',
        topicName: json['topic_name'] as String?,
        confidenceLevel: json['confidence_level'] as String? ?? 'unknown',
        beliefPct: (json['belief_pct'] as num?)?.toDouble() ?? 50.0,
        trend: json['trend'] as String? ?? 'stable',
        needsExplain: json['needs_explain'] as bool? ?? false,
        sampleCount: json['sample_count'] as int? ?? 0,
        accuracyPct: (json['accuracy_pct'] as num?)?.toDouble(),
        effortMinutes: (json['effort_minutes'] as num?)?.toDouble() ?? 0.0,
        resourceCount: json['resource_count'] as int? ?? 0,
        resources: (json['resources'] as List<dynamic>? ?? [])
            .map((e) => NotebookResourceItem.fromJson(e as Map<String, dynamic>))
            .toList(),
        explainAvailable: json['explain_available'] as bool? ?? false,
        quizAvailable: json['quiz_available'] as bool? ?? false,
        quizDifficulty: json['quiz_difficulty'] as String? ?? 'easy',
        knowledgeReady: json['knowledge_ready'] as bool? ?? false,
        knowledgeSummary: json['knowledge_summary'] as String?,
        knowledgeChunkCount: json['knowledge_chunk_count'] as int? ?? 0,
        knowledgeCitationCount: json['knowledge_citation_count'] as int? ?? 0,
        displayTitle: json['display_title'] as String? ?? 'Kaynak özeti',
      );
}
