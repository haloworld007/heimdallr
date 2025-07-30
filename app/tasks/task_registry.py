from typing import Dict, Type, Any
from crewai import Agent, Task

from .base_task_factory import BaseTaskFactory
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

class TaskRegistry:
    """精细化任务注册表 - 统一管理所有task工厂"""
    
    _factories: Dict[str, Type[BaseTaskFactory]] = {
        # 输入分类任务
        'input_classification': InputClassificationTaskFactory,
        'pattern_extraction': PatternExtractionTaskFactory,
        
        # 告警分析任务
        'alert_triage': AlertTriageTaskFactory,
        'alert_component_identification': AlertComponentIdentificationTaskFactory,
        'alert_log_search_params': AlertLogSearchParameterGenerationTaskFactory,
        'alert_business_impact': AlertBusinessImpactAssessmentTaskFactory,
        
        # Jira分析任务
        'jira_basic_info': JiraIssueBasicInfoExtractionTaskFactory,
        'jira_categorization': JiraIssueCategorizationTaskFactory,
        'jira_components_analysis': JiraRelatedComponentsAnalysisTaskFactory,
        'jira_context_enrichment': JiraContextEnrichmentTaskFactory,
        
        # 日志分析任务
        'log_search_execution': LogSearchExecutionTaskFactory,
        'log_pattern_analysis': LogPatternAnalysisTaskFactory,
        'log_anomaly_detection': LogAnomalyDetectionTaskFactory,
        'log_correlation_analysis': LogCorrelationAnalysisTaskFactory,
        
        # 综合分析任务
        'timeline_reconstruction': TimelineReconstructionTaskFactory,
        'root_cause_hypothesis': RootCauseHypothesisGenerationTaskFactory,
        'hypothesis_validation': HypothesisValidationTaskFactory,
        'solution_architecture': SolutionArchitectureTaskFactory,
        'comprehensive_report': ComprehensiveReportGenerationTaskFactory,
    }
    
    @classmethod
    def get_factory(cls, task_type: str) -> BaseTaskFactory:
        """获取任务工厂实例"""
        if task_type not in cls._factories:
            raise ValueError(f"Unknown task type: {task_type}. Available types: {list(cls._factories.keys())}")
        return cls._factories[task_type]()
    
    @classmethod
    def create_task(cls, task_type: str, agent: Agent, **kwargs) -> Task:
        """创建任务实例"""
        factory = cls.get_factory(task_type)
        try:
            return factory.create_task(agent, **kwargs)
        except Exception as e:
            raise ValueError(f"Failed to create task '{task_type}': {e}")
    
    @classmethod
    def get_available_task_types(cls) -> list:
        """获取所有可用的任务类型"""
        return list(cls._factories.keys())
    
    @classmethod
    def get_task_types_by_category(cls) -> Dict[str, list]:
        """按类别获取任务类型"""
        categories = {
            'classification': ['input_classification', 'pattern_extraction'],
            'alert': [
                'alert_triage', 
                'alert_component_identification',
                'alert_log_search_params', 
                'alert_business_impact'
            ],
            'jira': [
                'jira_basic_info',
                'jira_categorization', 
                'jira_components_analysis',
                'jira_context_enrichment'
            ],
            'log': [
                'log_search_execution',
                'log_pattern_analysis',
                'log_anomaly_detection', 
                'log_correlation_analysis'
            ],
            'synthesis': [
                'timeline_reconstruction',
                'root_cause_hypothesis',
                'hypothesis_validation',
                'solution_architecture',
                'comprehensive_report'
            ]
        }
        return categories
    
    @classmethod
    def validate_task_workflow(cls, workflow_tasks: list) -> bool:
        """验证任务工作流的有效性"""
        for task_type in workflow_tasks:
            if task_type not in cls._factories:
                return False
        return True

class WorkflowTemplates:
    """预定义的工作流模板"""
    
    ALERT_WORKFLOW = [
        'input_classification',
        'alert_triage',
        'alert_component_identification', 
        'alert_log_search_params',
        'log_search_execution',
        'log_pattern_analysis',
        'alert_business_impact',
        'timeline_reconstruction',
        'root_cause_hypothesis',
        'hypothesis_validation',
        'solution_architecture',
        'comprehensive_report'
    ]
    
    JIRA_WORKFLOW = [
        'input_classification',
        'jira_basic_info',
        'jira_categorization',
        'jira_components_analysis',
        'jira_context_enrichment',
        'timeline_reconstruction',
        'root_cause_hypothesis', 
        'hypothesis_validation',
        'solution_architecture',
        'comprehensive_report'
    ]
    
    LOG_WORKFLOW = [
        'input_classification',
        'log_search_execution',
        'log_pattern_analysis',
        'log_anomaly_detection',
        'log_correlation_analysis',
        'timeline_reconstruction',
        'root_cause_hypothesis',
        'hypothesis_validation',
        'solution_architecture',
        'comprehensive_report'
    ]
    
    HYBRID_WORKFLOW = [
        'input_classification',
        # 并行执行多种分析
        'alert_triage',
        'jira_basic_info',
        'log_search_execution',
        # 组件和模式分析
        'alert_component_identification',
        'jira_categorization',
        'log_pattern_analysis',
        # 综合分析
        'timeline_reconstruction',
        'root_cause_hypothesis',
        'hypothesis_validation', 
        'solution_architecture',
        'comprehensive_report'
    ]
    
    @classmethod
    def get_workflow_for_input_type(cls, input_type: str) -> list:
        """根据输入类型获取推荐的工作流"""
        workflow_map = {
            'alert': cls.ALERT_WORKFLOW,
            'jira_issue': cls.JIRA_WORKFLOW,
            'log_query': cls.LOG_WORKFLOW,
            'hybrid': cls.HYBRID_WORKFLOW,
            'unknown': cls.ALERT_WORKFLOW  # 默认使用告警工作流
        }
        return workflow_map.get(input_type, cls.ALERT_WORKFLOW) 