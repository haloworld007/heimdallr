from typing import Callable, List, Dict, Any
from crewai.tasks.conditional_task import ConditionalTask
from crewai.tasks.task_output import TaskOutput
from crewai import Agent

from .task_registry import TaskRegistry

class ConditionalTaskFactory:
    """条件任务工厂 - 创建基于条件执行的任务"""
    
    @staticmethod
    def create_conditional_log_search(agent: Agent, applications: List[str], 
                                    search_query: str, condition_data: Dict[str, Any] = None) -> ConditionalTask:
        """创建条件日志搜索任务"""
        
        def should_search_logs(output: TaskOutput) -> bool:
            """判断是否需要搜索日志"""
            if not output or not output.raw:
                return False
                
            content = output.raw.lower()
            
            # 检查是否包含需要日志搜索的关键词
            log_triggers = [
                'error', 'exception', 'timeout', 'failure', 'crash',
                '错误', '异常', '超时', '失败', '崩溃',
                'database', 'connection', 'network', 'api',
                '数据库', '连接', '网络', '接口'
            ]
            
            trigger_found = any(trigger in content for trigger in log_triggers)
            
            # 检查是否明确指出需要日志分析
            explicit_log_needs = [
                'check logs', 'search logs', 'log analysis',
                '检查日志', '搜索日志', '日志分析'
            ]
            
            explicit_need = any(need in content for need in explicit_log_needs)
            
            return trigger_found or explicit_need
        
        # 创建基础的日志搜索任务
        base_task = TaskRegistry.create_task(
            'log_search_execution',
            agent=agent,
            applications=applications,
            query=search_query
        )
        
        return ConditionalTask(
            description=base_task.description,
            expected_output=base_task.expected_output,
            condition=should_search_logs,
            agent=agent
        )
    
    @staticmethod
    def create_conditional_jira_fetch(agent: Agent, condition_data: Dict[str, Any] = None) -> ConditionalTask:
        """创建条件Jira获取任务"""
        
        def should_fetch_jira(output: TaskOutput) -> bool:
            """判断是否需要获取Jira信息"""
            if not output or not output.raw:
                return False
            
            # 检查是否包含Jira Issue Key模式
            import re
            jira_pattern = re.compile(r'\b([A-Z][A-Z0-9_]*-\d+)\b')
            jira_matches = jira_pattern.findall(output.raw)
            
            return len(jira_matches) > 0
        
        # 这里需要从output中提取Jira Issue Key，简化处理
        # 在实际使用时需要动态提取issue_key
        dummy_task = TaskRegistry.create_task(
            'jira_basic_info',
            agent=agent,
            issue_key='TEMP-000'  # 占位符，实际使用时需要动态替换
        )
        
        return ConditionalTask(
            description=dummy_task.description,
            expected_output=dummy_task.expected_output,
            condition=should_fetch_jira,
            agent=agent
        )
    
    @staticmethod
    def create_conditional_business_impact_assessment(agent: Agent, threshold_severity: str = "Medium") -> ConditionalTask:
        """创建条件业务影响评估任务"""
        
        def should_assess_business_impact(output: TaskOutput) -> bool:
            """判断是否需要进行业务影响评估"""
            if not output or not output.raw:
                return False
            
            content = output.raw.lower()
            
            # 检查严重性级别
            high_severity_indicators = [
                'critical', 'high', 'severe', 'urgent',
                '严重', '紧急', '高', '关键'
            ]
            
            # 检查业务相关关键词
            business_indicators = [
                'user', 'customer', 'payment', 'revenue', 'service',
                '用户', '客户', '支付', '收入', '服务', '业务'
            ]
            
            has_high_severity = any(indicator in content for indicator in high_severity_indicators)
            has_business_impact = any(indicator in content for indicator in business_indicators)
            
            return has_high_severity or has_business_impact
        
        # 创建基础的业务影响评估任务
        dummy_task = TaskRegistry.create_task(
            'alert_business_impact',
            agent=agent,
            alert_text='TEMP',  # 占位符
            components={}  # 占位符
        )
        
        return ConditionalTask(
            description=dummy_task.description,
            expected_output=dummy_task.expected_output,
            condition=should_assess_business_impact,
            agent=agent
        )

class ParallelTaskCoordinator:
    """并行任务协调器"""
    
    @staticmethod
    def create_parallel_analysis_group(task_configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """创建并行分析任务组"""
        parallel_tasks = []
        
        for config in task_configs:
            task_info = {
                'task_type': config['task_type'],
                'agent': config['agent'],
                'parameters': config.get('parameters', {}),
                'priority': config.get('priority', 'normal'),
                'timeout': config.get('timeout', 300),  # 5分钟默认超时
                'retry_count': config.get('retry_count', 2)
            }
            parallel_tasks.append(task_info)
        
        return parallel_tasks
    
    @staticmethod
    def create_alert_parallel_group(agents: Dict[str, Agent], alert_text: str) -> List[Dict[str, Any]]:
        """创建告警分析的并行任务组"""
        return ParallelTaskCoordinator.create_parallel_analysis_group([
            {
                'task_type': 'alert_triage',
                'agent': agents['triage'],
                'parameters': {'alert_text': alert_text},
                'priority': 'high'
            },
            {
                'task_type': 'alert_component_identification', 
                'agent': agents['component'],
                'parameters': {'alert_text': alert_text},
                'priority': 'high'
            },
            {
                'task_type': 'pattern_extraction',
                'agent': agents['pattern'],
                'parameters': {'input_text': alert_text},
                'priority': 'medium'
            }
        ])
    
    @staticmethod
    def create_jira_parallel_group(agents: Dict[str, Agent], issue_key: str) -> List[Dict[str, Any]]:
        """创建Jira分析的并行任务组"""
        return ParallelTaskCoordinator.create_parallel_analysis_group([
            {
                'task_type': 'jira_basic_info',
                'agent': agents['jira_fetcher'],
                'parameters': {'issue_key': issue_key},
                'priority': 'high'
            }
        ])
    
    @staticmethod
    def create_log_analysis_parallel_group(agents: Dict[str, Agent], log_entries: str) -> List[Dict[str, Any]]:
        """创建日志分析的并行任务组"""
        return ParallelTaskCoordinator.create_parallel_analysis_group([
            {
                'task_type': 'log_pattern_analysis',
                'agent': agents['pattern_analyzer'],
                'parameters': {'log_entries': log_entries},
                'priority': 'high'
            },
            {
                'task_type': 'log_anomaly_detection',
                'agent': agents['anomaly_detector'],
                'parameters': {'log_entries': log_entries},
                'priority': 'medium'
            },
            {
                'task_type': 'log_correlation_analysis',
                'agent': agents['correlation_analyst'],
                'parameters': {'log_entries': log_entries},
                'priority': 'medium'
            }
        ])

class TaskDependencyManager:
    """任务依赖管理器"""
    
    @staticmethod
    def define_task_dependencies() -> Dict[str, List[str]]:
        """定义任务之间的依赖关系"""
        dependencies = {
            # 基础分类任务没有依赖
            'input_classification': [],
            'pattern_extraction': ['input_classification'],
            
            # 告警分析任务链
            'alert_triage': ['input_classification'],
            'alert_component_identification': ['alert_triage'],
            'alert_log_search_params': ['alert_component_identification'],
            'alert_business_impact': ['alert_component_identification'],
            
            # Jira分析任务链
            'jira_basic_info': ['input_classification'],
            'jira_categorization': ['jira_basic_info'],
            'jira_components_analysis': ['jira_basic_info'],
            'jira_context_enrichment': ['jira_basic_info', 'jira_categorization'],
            
            # 日志分析任务链
            'log_search_execution': ['alert_log_search_params'],
            'log_pattern_analysis': ['log_search_execution'],
            'log_anomaly_detection': ['log_search_execution'],
            'log_correlation_analysis': ['log_search_execution'],
            
            # 综合分析任务（依赖前面的分析结果）
            'timeline_reconstruction': [
                'alert_triage', 'jira_basic_info', 'log_pattern_analysis'
            ],
            'root_cause_hypothesis': ['timeline_reconstruction'],
            'hypothesis_validation': ['root_cause_hypothesis'],
            'solution_architecture': ['hypothesis_validation'],
            'comprehensive_report': ['solution_architecture']
        }
        return dependencies
    
    @staticmethod
    def get_task_execution_order(task_list: List[str]) -> List[List[str]]:
        """根据依赖关系计算任务执行顺序（返回可并行执行的任务组）"""
        dependencies = TaskDependencyManager.define_task_dependencies()
        
        # 简化实现：按依赖层级分组
        execution_levels = []
        remaining_tasks = set(task_list)
        completed_tasks = set()
        
        while remaining_tasks:
            current_level = []
            
            for task in list(remaining_tasks):
                task_deps = dependencies.get(task, [])
                # 检查所有依赖是否都已完成
                if all(dep in completed_tasks or dep not in task_list for dep in task_deps):
                    current_level.append(task)
            
            if not current_level:
                # 避免无限循环，如果没有可执行的任务，添加剩余任务
                current_level = list(remaining_tasks)
            
            execution_levels.append(current_level)
            completed_tasks.update(current_level)
            remaining_tasks -= set(current_level)
        
        return execution_levels 