"""
StudyOS — SQLAlchemy Modelleri
Alembic autogenerate'in tüm modelleri görebilmesi için burada içe aktarılır.
"""

from app.models.achievement import (
    Achievement,
    AchievementCategory,
    AchievementProgress,
    AchievementTier,
    UserAchievement,
)
from app.models.activity import Activity, ActivityEventType
from app.models.conversation import Conversation, Message, MessageRole
from app.models.exam import Exam, ExamResult
from app.models.exam_intelligence import EiExam, EiPack, EiSubject, EiTopic
from app.models.exam_style import ExamStyleProfile, ExamStyleStat
from app.models.goal import Goal, GoalPeriod, GoalPriority, GoalStatus, GoalType
from app.models.learning_profile import (
    BaselineLevel,
    ExamTarget,
    JourneyStage,
    Student,
    SubjectCatalog,
    TopicCatalog,
    UserSubject,
)
from app.models.memory import Memory, MemoryCategory, MemorySource
from app.models.notification_preference import NotificationPreference
from app.models.planner_draft import PlannerDraft, PlannerDraftStatus
from app.models.question_record import (
    ExamType,
    QuestionDifficulty,
    QuestionRecord,
    QuestionSource,
)
from app.models.refresh_token import RefreshToken
from app.models.revision import (
    RevisionGrade,
    RevisionItem,
    RevisionItemStatus,
    RevisionReview,
    RevisionSchedule,
    RevisionSourceType,
)
from app.models.study_plan import StudyPlan, StudyPlanStatus
from app.models.study_resource import ResourceStatus, ResourceType, StudyResource
from app.models.study_session import StudySession, StudySessionStatus
from app.models.behavioral_memory import BehavioralMemory
from app.models.generated_question import GeneratedQuestion
from app.models.topic_confidence import ConfidenceLevel, TopicConfidence
from app.models.topic_evidence import (
    EvidenceCategory,
    EvidenceHorizon,
    EvidenceSourceType,
    TopicEvidence,
)
from app.models.topic_quiz import TopicQuizGeneration, TopicQuizItem
from app.models.assessment import (
    AssessmentKind,
    AssessmentQuestion,
    AssessmentSession,
    AssessmentSessionStatus,
    DailyChallenge,
    DailyChallengeScore,
    EstimatedScoreSnapshot,
    SharedDailyBooklet,
    SharedDailyBookletQuestion,
)
from app.models.knowledge import (
    CitationUsedBy,
    KnowledgeChunk,
    KnowledgeCitation,
    KnowledgeHealth,
    KnowledgeNotebook,
    KnowledgeSource,
)
from app.models.beta_ops import AnalyticsEvent, AnalyticsEventName, BetaFeedback
from app.models.qie_eval import QieHumanEvaluation
from app.models.question_pool import QuestionPoolCard
from app.models.question_pool_inventory import (
    QuestionPoolGenerationHistory,
    QuestionPoolGenerationLock,
)
from app.models.educational_asset import (
    EducationalAsset,
    EducationalAssetNode,
    EducationalAssetVersion,
)
from app.models.user import User, UserRole, UserStatus

__all__ = [
    "Achievement",
    "AchievementCategory",
    "AchievementProgress",
    "AchievementTier",
    "UserAchievement",
    "Activity",
    "ActivityEventType",
    "Conversation",
    "Exam",
    "ExamResult",
    "EiExam",
    "EiPack",
    "EiSubject",
    "EiTopic",
    "ExamStyleProfile",
    "ExamStyleStat",
    "ExamType",
    "PlannerDraft",
    "PlannerDraftStatus",
    "Goal",
    "GoalPeriod",
    "GoalPriority",
    "GoalStatus",
    "GoalType",
    "BaselineLevel",
    "ExamTarget",
    "JourneyStage",
    "Student",
    "SubjectCatalog",
    "TopicCatalog",
    "UserSubject",
    "Memory",
    "MemoryCategory",
    "MemorySource",
    "Message",
    "MessageRole",
    "NotificationPreference",
    "QuestionDifficulty",
    "QuestionRecord",
    "QuestionSource",
    "RefreshToken",
    "RevisionGrade",
    "RevisionItem",
    "RevisionItemStatus",
    "RevisionReview",
    "RevisionSchedule",
    "RevisionSourceType",
    "StudyPlan",
    "StudyPlanStatus",
    "StudyResource",
    "ResourceStatus",
    "ResourceType",
    "BehavioralMemory",
    "StudySession",
    "StudySessionStatus",
    "EvidenceCategory",
    "EvidenceHorizon",
    "EvidenceSourceType",
    "TopicEvidence",
    "GeneratedQuestion",
    "TopicQuizGeneration",
    "TopicQuizItem",
    "AssessmentKind",
    "AssessmentQuestion",
    "AssessmentSession",
    "AssessmentSessionStatus",
    "DailyChallenge",
    "DailyChallengeScore",
    "EstimatedScoreSnapshot",
    "SharedDailyBooklet",
    "SharedDailyBookletQuestion",
    "CitationUsedBy",
    "KnowledgeChunk",
    "KnowledgeCitation",
    "KnowledgeHealth",
    "KnowledgeNotebook",
    "KnowledgeSource",
    "AnalyticsEvent",
    "AnalyticsEventName",
    "BetaFeedback",
    "QieHumanEvaluation",
    "QuestionPoolCard",
    "QuestionPoolGenerationHistory",
    "QuestionPoolGenerationLock",
    "PasswordResetToken",
    "EducationalAsset",
    "EducationalAssetNode",
    "EducationalAssetVersion",
    "User",
    "UserRole",
    "UserStatus",
]


from app.models.workspace import StudyWorkspace, AnnotationLayer
