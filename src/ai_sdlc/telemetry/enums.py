"""Frozen telemetry enums defined once for the V1 contract."""

from __future__ import annotations

from enum import Enum


class ScopeLevel(str, Enum):
    SESSION = "session"
    RUN = "run"
    STEP = "step"


class ActorType(str, Enum):
    FRAMEWORK_RUNTIME = "framework_runtime"
    AGENT = "agent"
    HUMAN = "human"
    OBSERVER = "observer"
    EXTERNAL_TOOL = "external_tool"


class CaptureMode(str, Enum):
    AUTO = "auto"
    AGENT_REPORTED = "agent_reported"
    HUMAN_REPORTED = "human_reported"
    INFERRED = "inferred"


class IngressKind(str, Enum):
    AUTO = "auto"
    INJECTED = "injected"
    INFERRED = "inferred"


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TelemetryProfile(str, Enum):
    SELF_HOSTING = "self_hosting"
    EXTERNAL_PROJECT = "external_project"


class TelemetryMode(str, Enum):
    LITE = "lite"
    STRICT = "strict"
    FORENSICS = "forensics"


class TraceLayer(str, Enum):
    WORKFLOW = "workflow"
    AGENT_ACTION = "agent_action"
    TOOL = "tool"
    HUMAN = "human"
    EVALUATION = "evaluation"


class TriggerPointType(str, Enum):
    COLLECTOR = "collector"
    OBSERVER_ASYNC = "observer_async"
    GATE_CONSUMPTION = "gate_consumption"


class TelemetryEventStatus(str, Enum):
    STARTED = "started"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class EvidenceStatus(str, Enum):
    AVAILABLE = "available"
    PARTIAL = "partial"
    MISSING = "missing"
    ARCHIVED = "archived"


class EvaluationResult(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    NOT_APPLICABLE = "not_applicable"


class EvaluationStatus(str, Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    WAIVED = "waived"


class ViolationStatus(str, Enum):
    OPEN = "open"
    TRIAGED = "triaged"
    ACCEPTED = "accepted"
    FIXED = "fixed"
    DISMISSED = "dismissed"


class ViolationRiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ArtifactStatus(str, Enum):
    DRAFT = "draft"
    GENERATED = "generated"
    REVIEWED = "reviewed"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ArtifactType(str, Enum):
    REPORT = "report"
    SNAPSHOT = "snapshot"
    BUNDLE = "bundle"
    ATTACHMENT = "attachment"
    DELIVERABLE = "deliverable"


class ArtifactRole(str, Enum):
    AUDIT = "audit"
    EVALUATION = "evaluation"
    VIOLATION_SUMMARY = "violation_summary"
    IMPROVEMENT_PROPOSAL = "improvement_proposal"
    DELIVERABLE = "deliverable"
    DEBUG_ATTACHMENT = "debug_attachment"


class ArtifactStorageScope(str, Enum):
    PROJECT_COMMITTABLE = "project_committable"
    PROJECT_LOCAL = "project_local"
    EXPORTABLE = "exportable"


class GovernanceReviewStatus(str, Enum):
    DRAFT = "draft"
    REVIEWED = "reviewed"
    ACCEPTED = "accepted"
    FIXED = "fixed"
    DISMISSED = "dismissed"
    WAIVED = "waived"


class SourceClosureStatus(str, Enum):
    UNKNOWN = "unknown"
    INCOMPLETE = "incomplete"
    CLOSED = "closed"


class ProvenanceChainStatus(str, Enum):
    CLOSED = "closed"
    PARTIAL = "partial"
    UNKNOWN = "unknown"


class ProvenanceNodeKind(str, Enum):
    TRIGGER_POINT = "trigger_point"
    CONVERSATION_MESSAGE = "conversation_message"
    SKILL_INVOCATION = "skill_invocation"
    EXEC_COMMAND_BRIDGE = "exec_command_bridge"
    RULE_REFERENCE = "rule_reference"


class ProvenanceRelationKind(str, Enum):
    TRIGGERED_BY = "triggered_by"
    INVOKED = "invoked"
    BRIDGED_TO = "bridged_to"
    CITES = "cites"
    DERIVED_FROM = "derived_from"
    SUPPORTS = "supports"
    PRODUCED = "produced"


class ProvenanceGapKind(str, Enum):
    UNKNOWN = "unknown"
    UNOBSERVED = "unobserved"
    INCOMPLETE = "incomplete"
    UNSUPPORTED = "unsupported"


class ProvenanceCandidateResult(str, Enum):
    ADVISORY = "advisory"
    WARNING = "warning"
    BLOCKER_CANDIDATE = "blocker_candidate"


class HardFailCategory(str, Enum):
    HARD_FAIL_DEFAULT = "hard_fail_default"
    POLICY_OVERRIDABLE_HARD_FAIL_CANDIDATE = "policy_overridable_hard_fail_candidate"


class RootCauseClass(str, Enum):
    PROMPT = "prompt"
    CONTEXT = "context"
    RULE_POLICY = "rule_policy"
    MIDDLEWARE = "middleware"
    WORKFLOW = "workflow"
    TOOL = "tool"
    EVAL = "eval"
    MODEL_BEHAVIOR = "model_behavior"
    HUMAN_PROCESS = "human_process"


class SuggestedChangeLayer(str, Enum):
    PROMPT = "prompt"
    CONTEXT = "context"
    RULE_POLICY = "rule_policy"
    MIDDLEWARE = "middleware"
    WORKFLOW = "workflow"
    TOOL = "tool"
    EVAL = "eval"


class GateDecisionResult(str, Enum):
    ADVISORY = "advisory"
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"


class TelemetryObjectCategory(str, Enum):
    APPEND_ONLY = "append_only"
    MUTABLE = "mutable"
