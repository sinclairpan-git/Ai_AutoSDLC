# 工程认知基线（Engineering Corpus）

---

## 1. 一页摘要

以 **python** 为主的项目，共 **1458** 个文件（65193 行），涉及 4 种语言。
依赖：5 | API：2 | 测试文件：985

---

## 2. 仓库地图

### 顶层目录

- `.codex/`
- `.github/`
- `.playwright-cli/`
- `.superpowers/`
- `.worktrees/`
- `config/`
- `cursor/`
- `deliverables/`
- `dist-offline/`
- `docs/`
- `packaging/`
- `presets/`
- `rules/`
- `scripts/`
- `specs/`
- `src/`
- `templates/`
- `tests/`

### 按语言分布

- python：171
- shell：6
- html：2
- javascript：1

---

## 3. 模块边界与职责

### `src/ai_sdlc/`

`ProjectNotInitializedError`, `StudioRoutingError`, `RefreshRequiredError`, `GovernanceNotFrozenError`

### `src/ai_sdlc/backends/`

`BackendProtocol`, `BackendDecisionKind`, `BackendCapabilityDeclaration`, `BackendSelectionPolicy`, `BackendFailureEvidence`, `BackendSelectionDecision`, `NativeBackend`, `BackendNotFoundError`, `BackendRegistry`, `BackendRoutingBlockedError`, `BackendRoutingExecutionError`, `BackendExecutionError`, `BackendRoutingOperation`, `RoutedDocument`, `BackendRoutingCoordinator`

### `src/ai_sdlc/branch/`

`BranchError`, `GovernanceNotFrozenError`, `BranchManager`, `ProtectedFileError`, `FileGuard`, `GitError`, `IndexLockState`, `IndexLockInspection`, `LocalBranchInspection`, `WorktreeInspection`, `BranchDivergence`, `GitClient`

### `src/ai_sdlc/context/`

`CheckpointLoadError`, `ResumePackError`, `ResumePackNotFoundError`

### `src/ai_sdlc/core/`

`FormalArtifactTargetValidation`, `MisplacedFormalArtifact`, `FormalArtifactTargetGuardResult`, `MissingBacklogReference`, `BacklogBreachGuardResult`, `BranchLifecycleKind`, `BranchInventoryEntry`, `CloseCheckResult`, `BranchCheckResult`, `YamlStoreError`, `YamlStore`, `ChecklistItem`, `StageManifest`, `StageResult`, `StageDispatcher`, `ExecuteAuthorizationResult`, `ExecutorSettings`, `TaskExecutionOutcome`, `ExecutionResult`, `CircuitBreakerError`, `BatchExecutor`, `ExecutionLogger`, `Executor`, `PageImplementationObservation`, `FrontendContractDriftRecord`, `ObservationProviderProvenance`, `ObservationFreshnessMarker`, `FrontendContractObservationArtifact`, `FrontendContractObservationSourceAssessment`, `FrontendContractRuntimeAttachmentScope`, `FrontendContractRuntimeAttachment`, `VerificationDiagnosticEvidence`, `VerificationDiagnosticPolicyProjection`, `VerificationDiagnosticRecord`, `FrontendContractVerificationReport`, `FrontendCrossProviderConsistencyValidationResult`, `FrontendGateVerificationReport`, `FrontendGateExecuteDecision`, `FrontendPageUiSchemaValidationResult`, `FrontendPageUiSchemaHandoffEntry`, `FrontendPageUiSchemaHandoff`, `FrontendProviderExpansionValidationResult`, `FrontendProviderRuntimeAdapterValidationResult`, `FrontendQualityPlatformValidationResult`, `FrontendThemeTokenGovernanceValidationResult`, `FrontendVisualA11yEvidenceProvenance`, `FrontendVisualA11yEvidenceFreshness`, `FrontendVisualA11yEvidenceEvaluation`, `FrontendVisualA11yEvidenceArtifact`, `HostRuntimeProbe`, `PlanCheckResult`, `ProgramValidationResult`, `ProgramFrontendReadiness`, `ProgramFrontendThemeTokenOverrideDiagnostic`, `ProgramFrontendThemeTokenGovernanceHandoff`, `ProgramFrontendQualityPlatformDiagnostic`, `ProgramFrontendQualityPlatformHandoff`, `ProgramFrontendProviderExpansionDiagnostic`, `ProgramFrontendProviderExpansionHandoff`, `ProgramFrontendProviderRuntimeAdapterDiagnostic`, `ProgramFrontendProviderRuntimeAdapterHandoff`, `ProgramFrontendCrossProviderConsistencyDiagnostic`, `ProgramFrontendCrossProviderConsistencyHandoff`, `ProgramFrontendEvidenceClassStatus`, `ProgramSpecStatus`, `ProgramFrontendRecheckHandoff`, `ProgramFrontendRemediationInput`, `ProgramFrontendRemediationRunbookStep`, `ProgramFrontendRemediationRunbook`, `ProgramFrontendRemediationCommandResult`, `ProgramFrontendRemediationExecutionResult`, `ProgramFrontendManagedDeliveryApplyRequest`, `ProgramFrontendManagedDeliveryApplyResult`, `ProgramFrontendBrowserGateProbeRequest`, `ProgramFrontendBrowserGateProbeResult`, `ProgramFrontendProviderHandoffStep`, `ProgramFrontendProviderHandoff`, `ProgramFrontendProviderRuntimeRequestStep`, `ProgramFrontendProviderRuntimeRequest`, `ProgramFrontendProviderRuntimeResult`, `ProgramFrontendProviderPatchHandoffStep`, `ProgramFrontendProviderPatchHandoff`, `ProgramFrontendProviderPatchApplyRequestStep`, `ProgramFrontendProviderPatchApplyRequest`, `ProgramFrontendProviderPatchApplyResult`, `ProgramFrontendCrossSpecWritebackRequestStep`, `ProgramFrontendCrossSpecWritebackRequest`, `ProgramFrontendCrossSpecWritebackResult`, `ProgramFrontendGuardedRegistryRequestStep`, `ProgramFrontendGuardedRegistryRequest`, `ProgramFrontendGuardedRegistryResult`, `ProgramFrontendBroaderGovernanceRequestStep`, `ProgramFrontendBroaderGovernanceRequest`, `ProgramFrontendBroaderGovernanceResult`, `ProgramFrontendFinalGovernanceRequestStep`, `ProgramFrontendFinalGovernanceRequest`, `ProgramFrontendFinalGovernanceResult`, `ProgramFrontendWritebackPersistenceRequestStep`, `ProgramFrontendWritebackPersistenceRequest`, `ProgramFrontendWritebackPersistenceResult`, `ProgramFrontendPersistedWriteProofRequestStep`, `ProgramFrontendPersistedWriteProofRequest`, `ProgramFrontendPersistedWriteProofResult`, `ProgramFrontendFinalProofPublicationRequestStep`, `ProgramFrontendFinalProofPublicationRequest`, `ProgramFrontendFinalProofPublicationResult`, `ProgramFrontendFinalProofClosureRequestStep`, `ProgramFrontendFinalProofClosureRequest`, `ProgramFrontendFinalProofClosureResult`, `ProgramFrontendFinalProofArchiveRequestStep`, `ProgramFrontendFinalProofArchiveRequest`, `ProgramFrontendFinalProofArchiveResult`, `ProgramFrontendFinalProofArchiveThreadArchiveRequestStep`, `ProgramFrontendFinalProofArchiveThreadArchiveRequest`, `ProgramFrontendFinalProofArchiveThreadArchiveResult`, `ProgramFrontendFinalProofArchiveProjectCleanupRequestStep`, `ProgramFrontendFinalProofArchiveProjectCleanupRequest`, `ProgramFrontendFinalProofArchiveProjectCleanupResult`, `ProgramIntegrationStep`, `ProgramIntegrationPlan`, `ProgramExecuteGates`, `ProgramFrontendEvidenceClassSyncResult`, `ProgramManifestSpecEntrySyncResult`, `ProgramSpecTruthReadinessResult`, `ProgramService`, `ReconcileHint`, `ReleaseGateParseError`, `ReleaseGateCheck`, `ReleaseGateReport`, `ReviewerGateOutcomeKind`, `ReviewerGateResult`, `PipelineHaltError`, `SDLCRunner`, `InvalidTransitionError`, `FeatureContractEvidence`, `FeatureContractSurface`, `ConstraintReport`, `FrontendSolutionConfirmationVerificationReport`, `FrontendThemeTokenGovernanceVerificationReport`, `FrontendQualityPlatformVerificationReport`, `FrontendProviderExpansionVerificationReport`, `FrontendProviderRuntimeAdapterVerificationReport`, `FrontendCrossProviderConsistencyVerificationReport`, `WorkitemScaffoldError`, `WorkitemScaffoldResult`, `WorkitemScaffolder`, `CompletionTruthResult`, `BranchDispositionTruth`, `WorkItemBranchLifecycleEntry`, `WorkItemBranchLifecycleResult`, `WorkitemTruthResult`

### `src/ai_sdlc/gates/`

`KnowledgeGate`, `ParallelGate`, `PostmortemGate`, `FrontendContractGate`, `GovernanceFreezeError`, `GovernanceGuard`, `InitGate`, `RefineGate`, `PRDGate`, `DesignGate`, `DecomposeGate`, `VerifyGate`, `VerificationGate`, `ReviewGate`, `ExecuteGate`, `CloseGate`, `DoneGate`, `GateProtocol`, `GateRegistry`, `TaskBlock`

### `src/ai_sdlc/generators/`

`ScaffoldRenderResult`, `RenderResult`, `DocScaffolder`, `TasksParser`, `TemplateGeneratorError`, `TemplateGenerator`

### `src/ai_sdlc/integrations/`

`IDEKind`, `ApplyResult`, `CanonicalConsumptionState`

### `src/ai_sdlc/models/`

`FrontendBrowserGateModel`, `BrowserQualityGateExecutionContext`, `BrowserGateProbeRuntimeSession`, `BrowserGateSharedRuntimeCapture`, `BrowserGateInteractionProbeCapture`, `BrowserGateProbeRunnerResult`, `BrowserProbeArtifactRecord`, `BrowserProbeExecutionReceipt`, `BrowserQualityBundleMaterializationInput`, `FrontendContractModel`, `ContractException`, `PageMetadata`, `RecipeDeclaration`, `I18nEntry`, `I18nContract`, `ValidationFieldRule`, `ValidationContract`, `WhitelistReference`, `TokenRulesReference`, `ContractRuleBundle`, `ContractLegacyContext`, `ModuleContract`, `PageContract`, `FrontendContractSet`, `FrontendCrossProviderConsistencyModel`, `ConsistencyStateVector`, `UxEquivalenceClause`, `ConsistencyDiffRecord`, `CoverageGapRecord`, `ProviderPairCertificationBundle`, `ProviderPairTruthSurfacingRecord`, `ReadinessGateRule`, `ConsistencyReadinessGate`, `ConsistencyHandoffContract`, `FrontendCrossProviderConsistencySet`, `FrontendGateModel`, `FrontendGateRule`, `CompatibilityExecutionPolicy`, `FrontendDiagnosticsCoverageEntry`, `FrontendDriftClassification`, `FrontendCompatibilityFeedbackBoundary`, `FrontendVisualFoundationCoverageEntry`, `FrontendA11yFoundationCoverageEntry`, `FrontendVisualA11yEvidenceBoundary`, `FrontendVisualA11yFeedbackBoundary`, `FrontendViolation`, `FrontendCoverageGap`, `FrontendDriftFinding`, `FrontendLegacyExpansionFinding`, `FrontendViolationReport`, `FrontendCoverageReport`, `FrontendDriftReport`, `FrontendLegacyExpansionReport`, `FrontendGatePolicySet`, `FrontendGenerationModel`, `RecipeGenerationConstraint`, `WhitelistGenerationConstraint`, `GenerationHardRule`, `GenerationHardRuleSet`, `TokenRuleSet`, `GenerationExceptionPolicy`, `FrontendGenerationConstraintSet`, `FrontendManagedDeliveryModel`, `DependencyInstallExecutionPayload`, `RuntimeRemediationExecutionPayload`, `GeneratedArtifactFile`, `ArtifactGenerateExecutionPayload`, `ManagedTargetPrepareExecutionPayload`, `WorkspaceIntegrationItem`, `WorkspaceIntegrationExecutionPayload`, `FrontendActionPlanAction`, `ConfirmedActionPlanExecutionView`, `DeliveryApplyDecisionReceipt`, `ManagedDeliveryExecutionSession`, `DeliveryActionLedgerEntry`, `ManagedDeliveryApplyResult`, `ManagedDeliveryExecutorContext`, `FrontendPageUiSchemaModel`, `SchemaVersioningContract`, `SectionAnchorDefinition`, `FieldBlockDefinition`, `PageSchemaDefinition`, `RenderSlotDefinition`, `UiSchemaDefinition`, `FrontendPageUiSchemaSet`, `FrontendProviderExpansionModel`, `PairCertificationReference`, `ProviderCertificationAggregate`, `ChoiceSurfacePolicy`, `ProviderAdmissionBundle`, `ReactExposureBoundary`, `ProviderExpansionTruthSurfacingRecord`, `ProviderExpansionHandoffContract`, `FrontendProviderExpansionSet`, `FrontendProviderProfileModel`, `ProviderMapping`, `ProviderWhitelistEntry`, `ProviderStyleSupportEntry`, `ProviderRiskIsolationPolicy`, `LegacyAdapterPolicy`, `EnterpriseVue2ProviderProfile`, `FrontendProviderRuntimeAdapterModel`, `AdapterScaffoldFile`, `AdapterScaffoldContract`, `RuntimeBoundaryReceipt`, `ProviderRuntimeAdapterTarget`, `ProviderRuntimeAdapterHandoffContract`, `FrontendProviderRuntimeAdapterSet`, `FrontendQualityPlatformModel`, `QualityCoverageMatrixEntry`, `QualityEvidenceContract`, `InteractionQualityFlow`, `QualityVerdictEnvelope`, `QualityTruthSurfacingRecord`, `QualityPlatformHandoffContract`, `FrontendQualityPlatformSet`, `FrontendSolutionConfirmationModel`, `AvailabilitySummary`, `StylePackManifest`, `InstallStrategy`, `FrontendSolutionSnapshot`, `FrontendThemeTokenGovernanceModel`, `ThemeTokenMapping`, `CustomThemeTokenOverride`, `StyleEditorBoundaryContract`, `ThemeGovernanceHandoffContract`, `FrontendThemeTokenGovernanceSet`, `FrontendUiKernelModel`, `UiProtocolComponent`, `PageRecipeStandard`, `KernelStateSemantic`, `KernelStateBaseline`, `KernelInteractionBaseline`, `FrontendUiKernelSet`, `GateVerdict`, `GateCheck`, `GateResult`, `GovernanceItem`, `GovernanceState`, `HostRuntimePlanModel`, `InstallerProfileRef`, `HostRuntimeReadiness`, `BootstrapAcquisitionFacet`, `RemediationFragmentFacet`, `HostRuntimePlan`, `ProgramGoal`, `ProgramRequiredEvidenceRefs`, `ProgramCapabilityRef`, `ProgramSpecRef`, `ProgramCapabilityClosureCluster`, `ProgramCapabilityClosureAudit`, `ProgramComputedCapabilityState`, `ProgramSourceRef`, `ProgramTruthSourceEntry`, `ProgramTruthSourceInventory`, `ProgramTruthSnapshot`, `ProgramManifest`, `ProjectStatus`, `ActivationState`, `AdapterSupportTier`, `AdapterIngressState`, `AdapterVerificationResult`, `ProjectState`, `ProjectConfig`, `FileInfo`, `DependencyInfo`, `ApiEndpoint`, `SymbolInfo`, `DiscoveredTestFile`, `RiskItem`, `ScanResult`, `RefreshLevel`, `KnowledgeBaselineState`, `RefreshEntry`, `KnowledgeRefreshLog`, `CompletedStage`, `FeatureInfo`, `MultiAgentInfo`, `ExecuteProgress`, `Checkpoint`, `RuntimeState`, `WorkingSet`, `ResumePack`, `TaskStatus`, `Task`, `ExecutionBatch`, `ExecutionPlan`, `ParallelPolicy`, `InterfaceContract`, `WorkerAssignment`, `OverlapResult`, `MergeSimulation`, `ParallelCoordinationArtifact`, `WorkType`, `Severity`, `WorkItemSource`, `Confidence`, `ClarificationStatus`, `WorkItemStatus`, `ClarificationState`, `WorkItem`, `PrdReadiness`, `PrdDocumentState`, `PrdReviewerCheckpoint`, `PrdReviewerDecisionKind`, `PrdDocument`, `DraftPrd`, `FinalPrd`, `PrdAuthoringResult`, `PrdReviewerDecision`, `IncidentBrief`, `IncidentAnalysis`, `IncidentTask`, `IncidentFixPlan`, `PostmortemRecord`, `FreezeSnapshot`, `ImpactAnalysis`, `RebaselineRecord`, `ResumePoint`, `ChangeRequest`, `MaintenanceTask`, `SmallTaskGraph`, `ExecutionPathStep`, `ExecutionPath`, `MaintenanceBrief`, `MaintenancePlan`

### `src/ai_sdlc/routers/`

`WorkIntakeProtocol`, `KeywordWorkIntakeRouter`

### `src/ai_sdlc/rules/`

`RulesLoader`

### `src/ai_sdlc/scanners/`

`FrontendContractScannerResult`

### `src/ai_sdlc/studios/`

`ChangeStudio`, `IncidentStudio`, `MaintenanceStudio`, `PrdStudio`, `PrdStudioAdapter`, `StudioProtocol`, `StudioRouter`

### `src/ai_sdlc/telemetry/`

`CollectedTrace`, `DeterministicCollectors`, `TelemetryRecord`, `TelemetryScope`, `TraceContext`, `ModeChangeRecord`, `GateDecisionPayload`, `TelemetryEvent`, `Evidence`, `Evaluation`, `Violation`, `Artifact`, `MismatchFinding`, `GovernanceViolationCandidate`, `ViolationHit`, `ScopeLevel`, `ActorType`, `CaptureMode`, `IngressKind`, `Confidence`, `TelemetryProfile`, `TelemetryMode`, `TraceLayer`, `TriggerPointType`, `TelemetryEventStatus`, `EvidenceStatus`, `EvaluationResult`, `EvaluationStatus`, `ViolationStatus`, `ViolationRiskLevel`, `ArtifactStatus`, `ArtifactType`, `ArtifactRole`, `ArtifactStorageScope`, `GovernanceReviewStatus`, `SourceClosureStatus`, `ProvenanceChainStatus`, `ProvenanceNodeKind`, `ProvenanceRelationKind`, `ProvenanceGapKind`, `ProvenanceCandidateResult`, `HardFailCategory`, `RootCauseClass`, `SuggestedChangeLayer`, `GateDecisionResult`, `TelemetryObjectCategory`, `ObserverEvaluationFinding`, `GovernancePublisher`, `ObserverConditions`, `ObserverTrigger`, `StepObserverResult`, `TelemetryObserver`, `ResolvedRuntimeTelemetryPolicy`, `ProvenanceContract`, `ProvenanceFact`, `ProvenanceMutableRecord`, `ProvenanceNodeFact`, `ProvenanceEdgeFact`, `ProvenanceAssessment`, `ProvenanceGapFinding`, `ProvenanceGovernanceHook`, `PendingProvenanceNode`, `PendingProvenanceEdge`, `ProvenanceParseFailure`, `ProvenanceIngressResult`, `ProvenanceIngressWriteResult`, `ProvenanceChainModeView`, `ProvenanceBlockingGapView`, `ProvenanceAssessmentView`, `ProvenanceInspectionView`, `ProvenanceObserverResult`, `ProvenanceResolutionFailure`, `ProvenanceResolutionReport`, `ProvenanceResolver`, `ProvenanceStore`, `CriticalControlPoint`, `CCPRegistry`, `ResolvedSource`, `SourceResolver`, `WorkflowRunContext`, `RuntimeTelemetry`, `TelemetryStore`, `SourceClosureAssessment`, `TelemetryWriter`

---

## 4. 关键入口与核心文件

### 入口

- `src/ai_sdlc/__main__.py`（6 行）
- `src/ai_sdlc/cli/main.py`（79 行）

### 配置文件

- `pyproject.toml`
---

## 5. 核心数据模型 / 领域模型

- `BackendProtocol`（`src/ai_sdlc/backends/native.py:28`） — Interface that all SDLC backends must implement.
- `BackendDecisionKind`（`src/ai_sdlc/backends/native.py:39`） — Outcome of backend selection.
- `BackendCapabilityDeclaration`（`src/ai_sdlc/backends/native.py:48`） — Formal backend capability declaration contract.
- `BackendSelectionPolicy`（`src/ai_sdlc/backends/native.py:74`） — Policy gates that influence backend selection.
- `BackendFailureEvidence`（`src/ai_sdlc/backends/native.py:82`） — Structured failure evidence for a plugin backend attempt.
- `BackendSelectionDecision`（`src/ai_sdlc/backends/native.py:92`） — Structured backend selection result readable by later gates.
- `NativeBackend`（`src/ai_sdlc/backends/native.py:136`） — Default backend using file-system-based generators.
- `BackendNotFoundError`（`src/ai_sdlc/backends/native.py:205`） — Raised when a requested backend is not registered.
- `BackendRegistry`（`src/ai_sdlc/backends/native.py:209`） — Registry for SDLC execution backends.
- `BackendRoutingBlockedError`（`src/ai_sdlc/backends/routing.py:20`） — Raised when backend selection blocks a routed document generation request.
- `BackendRoutingExecutionError`（`src/ai_sdlc/backends/routing.py:28`） — Raised when the selected backend fails during routed document generation.
- `BackendExecutionError`（`src/ai_sdlc/backends/routing.py:37`） — Typed backend execution failure that may safely fall back.
- `BackendRoutingOperation`（`src/ai_sdlc/backends/routing.py:54`） — Supported routed document generation operations.
- `RoutedDocument`（`src/ai_sdlc/backends/routing.py:63`） — Rendered document content and its backend decision.
- `BackendRoutingCoordinator`（`src/ai_sdlc/backends/routing.py:70`） — Coordinate runtime backend selection for document generation.
- `BranchError`（`src/ai_sdlc/branch/branch_manager.py:21`） — Raised when a branch operation violates policy.
- `GovernanceNotFrozenError`（`src/ai_sdlc/branch/branch_manager.py:25`） — Raised when governance has not been frozen for docs/dev entry.
- `BranchManager`（`src/ai_sdlc/branch/branch_manager.py:29`） — Manages the docs/dev dual-branch model for work items.
- `ProtectedFileError`（`src/ai_sdlc/branch/file_guard.py:15`） — Raised when a write to a protected file is attempted.
- `FileGuard`（`src/ai_sdlc/branch/file_guard.py:19`） — Track and enforce file-level write protection.
- `GitError`（`src/ai_sdlc/branch/git_client.py:18`） — Raised when a git operation fails.
- `IndexLockState`（`src/ai_sdlc/branch/git_client.py:22`） — Classification of the repository's ``.git/index.lock`` state.
- `IndexLockInspection`（`src/ai_sdlc/branch/git_client.py:31`） — Structured result for ``.git/index.lock`` preflight checks.
- `LocalBranchInspection`（`src/ai_sdlc/branch/git_client.py:40`） — Read-only snapshot of one local branch.
- `WorktreeInspection`（`src/ai_sdlc/branch/git_client.py:51`） — Read-only snapshot of one registered worktree.
- `BranchDivergence`（`src/ai_sdlc/branch/git_client.py:60`） — Ahead/behind counts for ``branch`` relative to ``base``.
- `GitClient`（`src/ai_sdlc/branch/git_client.py:69`） — Thin wrapper around git CLI commands.
- `CheckpointLoadError`（`src/ai_sdlc/context/state.py:41`） — Raised when checkpoint.yml is missing or violates recovery contracts.
- `ResumePackError`（`src/ai_sdlc/context/state.py:45`） — Raised when resume-pack.yaml cannot be loaded safely.
- `ResumePackNotFoundError`（`src/ai_sdlc/context/state.py:49`） — Raised when resume-pack.yaml is required but missing.
---

## 6. 架构决策与取舍

<!-- TODO：记录关键架构决策及理由 -->

---

## 7. 隐式约定与代码规范

<!-- TODO：记录命名习惯、模式等未成文约定 -->

---

## 8. 外部集成

### 已检测 API 端点

- `GET /path`（flask，`src/ai_sdlc/scanners/api_scanner.py:13`）
- `GET /path`（flask，`src/ai_sdlc/scanners/api_scanner.py:19`）
---

## 9. 已知风险与技术债

- **large_file** [medium]：`src/ai_sdlc/backends/native.py` — File has 583 lines (threshold: 500)
- **large_file** [medium]：`src/ai_sdlc/branch/git_client.py` — File has 551 lines (threshold: 500)
- **large_file** [medium]：`src/ai_sdlc/cli/commands.py` — File has 785 lines (threshold: 500)
- **large_file** [high]：`src/ai_sdlc/cli/program_cmd.py` — File has 5521 lines (threshold: 500)
- **large_file** [medium]：`src/ai_sdlc/cli/sub_apps.py` — File has 617 lines (threshold: 500)
- **large_file** [medium]：`src/ai_sdlc/context/state.py` — File has 587 lines (threshold: 500)
- **large_file** [medium]：`src/ai_sdlc/core/close_check.py` — File has 954 lines (threshold: 500)
- **large_file** [medium]：`src/ai_sdlc/core/executor.py` — File has 763 lines (threshold: 500)
- **large_file** [medium]：`src/ai_sdlc/core/frontend_browser_gate_runtime.py` — File has 969 lines (threshold: 500)
- **large_file** [medium]：`src/ai_sdlc/core/frontend_gate_verification.py` — File has 887 lines (threshold: 500)
- **large_file** [medium]：`src/ai_sdlc/core/managed_delivery_apply.py` — File has 937 lines (threshold: 500)
- **large_file** [high]：`src/ai_sdlc/core/program_service.py` — File has 12330 lines (threshold: 500)
- **large_file** [medium]：`src/ai_sdlc/core/reconcile.py` — File has 512 lines (threshold: 500)
- **large_file** [medium]：`src/ai_sdlc/core/runner.py` — File has 532 lines (threshold: 500)
- **large_file** [high]：`src/ai_sdlc/core/verify_constraints.py` — File has 4044 lines (threshold: 500)
- **large_file** [medium]：`src/ai_sdlc/gates/pipeline_gates.py` — File has 971 lines (threshold: 500)
- **large_file** [medium]：`src/ai_sdlc/integrations/ide_adapter.py` — File has 806 lines (threshold: 500)
- **large_file** [medium]：`src/ai_sdlc/models/frontend_cross_provider_consistency.py` — File has 749 lines (threshold: 500)
- **large_file** [high]：`src/ai_sdlc/models/frontend_gate_policy.py` — File has 1111 lines (threshold: 500)
- **large_file** [medium]：`src/ai_sdlc/models/frontend_page_ui_schema.py` — File has 564 lines (threshold: 500)
- **large_file** [medium]：`src/ai_sdlc/models/frontend_ui_kernel.py` — File has 653 lines (threshold: 500)
- **large_file** [medium]：`src/ai_sdlc/telemetry/contracts.py` — File has 523 lines (threshold: 500)
- **large_file** [medium]：`src/ai_sdlc/telemetry/evaluators.py` — File has 538 lines (threshold: 500)
- **large_file** [medium]：`src/ai_sdlc/telemetry/readiness.py` — File has 921 lines (threshold: 500)
- **large_file** [medium]：`src/ai_sdlc/telemetry/runtime.py` — File has 716 lines (threshold: 500)
- **large_file** [medium]：`src/ai_sdlc/telemetry/store.py` — File has 558 lines (threshold: 500)
- **todo_density** [low]：`src/ai_sdlc/generators/corpus_gen.py` — Contains 7 TODO/FIXME/HACK markers
- **todo_density** [low]：`src/ai_sdlc/scanners/risk_scanner.py` — Contains 9 TODO/FIXME/HACK markers
- **todo_density** [low]：`src/ai_sdlc/studios/incident_studio.py` — Contains 5 TODO/FIXME/HACK markers
- **high_coupling** [medium]：`__future__` — Imported by 150 other files (threshold: 36)
- **high_coupling** [medium]：`pathlib` — Imported by 97 other files (threshold: 36)
- **high_coupling** [medium]：`ai_sdlc` — Imported by 126 other files (threshold: 36)
- **high_coupling** [medium]：`typing` — Imported by 56 other files (threshold: 36)
- **high_coupling** [medium]：`dataclasses` — Imported by 47 other files (threshold: 36)
- **no_tests** [medium]：`dist-offline/ai-sdlc-offline-0.5.1` — Source directory 'dist-offline/ai-sdlc-offline-0.5.1' has no corresponding test directory
- **no_tests** [medium]：`src/ai_sdlc/branch` — Source directory 'src/ai_sdlc/branch' has no corresponding test directory
- **no_tests** [medium]：`src/ai_sdlc/stages` — Source directory 'src/ai_sdlc/stages' has no corresponding test directory
- **no_tests** [medium]：`.superpowers/brainstorm/31873-1775640624` — Source directory '.superpowers/brainstorm/31873-1775640624' has no corresponding test directory
- **no_tests** [medium]：`src/ai_sdlc/gates` — Source directory 'src/ai_sdlc/gates' has no corresponding test directory
- **no_tests** [medium]：`dist-offline/ai-sdlc-offline-0.5.0` — Source directory 'dist-offline/ai-sdlc-offline-0.5.0' has no corresponding test directory
- **no_tests** [medium]：`src/ai_sdlc/core` — Source directory 'src/ai_sdlc/core' has no corresponding test directory
- **no_tests** [medium]：`src/ai_sdlc/backends` — Source directory 'src/ai_sdlc/backends' has no corresponding test directory
- **no_tests** [medium]：`src/ai_sdlc/generators` — Source directory 'src/ai_sdlc/generators' has no corresponding test directory
- **no_tests** [medium]：`src/ai_sdlc/knowledge` — Source directory 'src/ai_sdlc/knowledge' has no corresponding test directory
- **no_tests** [medium]：`src/ai_sdlc` — Source directory 'src/ai_sdlc' has no corresponding test directory
- **no_tests** [medium]：`src/ai_sdlc/models` — Source directory 'src/ai_sdlc/models' has no corresponding test directory
- **no_tests** [medium]：`src/ai_sdlc/parallel` — Source directory 'src/ai_sdlc/parallel' has no corresponding test directory
- **no_tests** [medium]：`.superpowers/brainstorm/83637-1774953116` — Source directory '.superpowers/brainstorm/83637-1774953116' has no corresponding test directory
- **no_tests** [medium]：`dist-offline/ai-sdlc-offline-0.2.5` — Source directory 'dist-offline/ai-sdlc-offline-0.2.5' has no corresponding test directory
- **no_tests** [medium]：`src/ai_sdlc/scanners` — Source directory 'src/ai_sdlc/scanners' has no corresponding test directory
- **no_tests** [medium]：`src/ai_sdlc/context` — Source directory 'src/ai_sdlc/context' has no corresponding test directory
- **no_tests** [medium]：`src/ai_sdlc/telemetry` — Source directory 'src/ai_sdlc/telemetry' has no corresponding test directory
- **no_tests** [medium]：`src/ai_sdlc/rules` — Source directory 'src/ai_sdlc/rules' has no corresponding test directory
- **no_tests** [medium]：`src/ai_sdlc/integrations` — Source directory 'src/ai_sdlc/integrations' has no corresponding test directory
- **no_tests** [medium]：`packaging/offline` — Source directory 'packaging/offline' has no corresponding test directory
- **no_tests** [medium]：`src/ai_sdlc/studios` — Source directory 'src/ai_sdlc/studios' has no corresponding test directory
- **no_tests** [medium]：`src/ai_sdlc/adapters` — Source directory 'src/ai_sdlc/adapters' has no corresponding test directory
- **no_tests** [medium]：`dist-offline/ai-sdlc-offline-0.3.1` — Source directory 'dist-offline/ai-sdlc-offline-0.3.1' has no corresponding test directory
- **no_tests** [medium]：`src/ai_sdlc/routers` — Source directory 'src/ai_sdlc/routers' has no corresponding test directory
- **no_tests** [medium]：`src/ai_sdlc/cli` — Source directory 'src/ai_sdlc/cli' has no corresponding test directory
- **no_tests** [medium]：`src/ai_sdlc/utils` — Source directory 'src/ai_sdlc/utils' has no corresponding test directory
- **no_tests** [medium]：`scripts` — Source directory 'scripts' has no corresponding test directory
---

## 10. 待澄清问题

<!-- TODO：列出对代码库仍存疑的问题 -->
