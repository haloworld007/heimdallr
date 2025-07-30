# 新的精细化tasks模块

from .base_task_factory import BaseTaskFactory
from .task_registry import TaskRegistry, WorkflowTemplates
from .conditional_tasks import ConditionalTaskFactory, ParallelTaskCoordinator, TaskDependencyManager

# 各类任务工厂
from .classification_tasks import InputClassificationTaskFactory, PatternExtractionTaskFactory
from .alert_tasks import (
    AlertTriageTaskFactory,
    AlertComponentIdentificationTaskFactory,
    AlertLogSearchParameterGenerationTaskFactory,
    AlertBusinessImpactAssessmentTaskFactory
)
from .jira_tasks import (
    JiraIssueBasicInfoExtractionTaskFactory,
    JiraIssueCategorizationTaskFactory,
    JiraRelatedComponentsAnalysisTaskFactory,
    JiraContextEnrichmentTaskFactory
)
from .log_tasks import (
    LogSearchExecutionTaskFactory,
    LogPatternAnalysisTaskFactory,
    LogAnomalyDetectionTaskFactory,
    LogCorrelationAnalysisTaskFactory
)
from .synthesis_tasks import (
    TimelineReconstructionTaskFactory,
    RootCauseHypothesisGenerationTaskFactory,
    HypothesisValidationTaskFactory,
    SolutionArchitectureTaskFactory,
    ComprehensiveReportGenerationTaskFactory
)

__all__ = [
    # 核心类
    'BaseTaskFactory',
    'TaskRegistry', 
    'WorkflowTemplates',
    'ConditionalTaskFactory',
    'ParallelTaskCoordinator',
    'TaskDependencyManager',
    
    # 分类任务工厂
    'InputClassificationTaskFactory',
    'PatternExtractionTaskFactory',
    
    # 告警任务工厂
    'AlertTriageTaskFactory',
    'AlertComponentIdentificationTaskFactory',
    'AlertLogSearchParameterGenerationTaskFactory',
    'AlertBusinessImpactAssessmentTaskFactory',
    
    # Jira任务工厂
    'JiraIssueBasicInfoExtractionTaskFactory',
    'JiraIssueCategorizationTaskFactory', 
    'JiraRelatedComponentsAnalysisTaskFactory',
    'JiraContextEnrichmentTaskFactory',
    
    # 日志任务工厂
    'LogSearchExecutionTaskFactory',
    'LogPatternAnalysisTaskFactory',
    'LogAnomalyDetectionTaskFactory',
    'LogCorrelationAnalysisTaskFactory',
    
    # 综合分析任务工厂
    'TimelineReconstructionTaskFactory',
    'RootCauseHypothesisGenerationTaskFactory',
    'HypothesisValidationTaskFactory',
    'SolutionArchitectureTaskFactory',
    'ComprehensiveReportGenerationTaskFactory'
] 