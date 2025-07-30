import logging
import asyncio
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from crewai import Agent, Task, Crew, Process

from .flow_state import DiagnosisState, InputType, AnalysisResult
from .agents import AlertAgents, JiraAgents, LogAgents, SynthesisAgents
from .tasks import TaskRegistry, WorkflowTemplates, TaskDependencyManager, ParallelTaskCoordinator

logger = logging.getLogger(__name__)

class DynamicWorkflowRouter:
    """动态工作流路由器 - 根据输入类型选择和执行最优的处理流程"""
    
    def __init__(self, llm, max_parallel_tasks: int = 3):
        self.llm = llm
        self.max_parallel_tasks = max_parallel_tasks
        self.task_registry = TaskRegistry
        self.workflow_templates = WorkflowTemplates
        self.dependency_manager = TaskDependencyManager
        
        # 初始化agent池
        self._init_agent_pool()
        
    def _init_agent_pool(self):
        """初始化专门化的agent池"""
        self.agents = {
            # 告警分析agents
            'alert_triage': AlertAgents.alert_triage_agent(self.llm),
            'alert_component': AlertAgents.alert_component_identifier_agent(self.llm),
            'alert_log_strategy': AlertAgents.alert_log_search_strategist_agent(self.llm),
            'alert_log_executor': AlertAgents.alert_log_searcher_agent(self.llm),
            'alert_business_impact': AlertAgents.alert_business_impact_assessor_agent(self.llm),
            
            # Jira分析agents
            'jira_fetcher': JiraAgents.jira_fetcher_agent(self.llm),
            'jira_categorizer': JiraAgents.jira_categorizer_agent(self.llm),
            'jira_tech_analyzer': JiraAgents.jira_technical_analyzer_agent(self.llm),
            'jira_context_enricher': JiraAgents.jira_context_enricher_agent(self.llm),
            
            # 日志分析agents
            'log_executor': LogAgents.log_search_executor_agent(self.llm),
            'log_pattern': LogAgents.log_pattern_analyzer_agent(self.llm),
            'log_anomaly': LogAgents.log_anomaly_detector_agent(self.llm),
            'log_correlation': LogAgents.log_correlation_analyst_agent(self.llm),
            
            # 综合分析agents
            'timeline_reconstructor': SynthesisAgents.timeline_reconstructor_agent(self.llm),
            'root_cause_generator': SynthesisAgents.root_cause_hypothesis_generator_agent(self.llm),
            'hypothesis_validator': SynthesisAgents.hypothesis_validator_agent(self.llm),
            'solution_architect': SynthesisAgents.solution_architect_agent(self.llm),
            'report_generator': SynthesisAgents.report_generator_agent(self.llm),
            'qa_specialist': SynthesisAgents.quality_assurance_agent(self.llm)
        }
        
    def route_and_execute(self, state: DiagnosisState) -> DiagnosisState:
        """根据分类结果路由到相应的工作流并执行"""
        if not state.classification:
            logger.error("状态中没有分类结果，无法路由")
            return state
        
        input_type = state.classification.input_type
        logger.info(f"路由到工作流: {input_type.value}")
        
        try:
            # 根据输入类型获取工作流模板
            workflow_tasks = self.workflow_templates.get_workflow_for_input_type(input_type.value)
            
            # 计算任务执行顺序
            execution_levels = self.dependency_manager.get_task_execution_order(workflow_tasks)
            
            logger.info(f"工作流包含 {len(workflow_tasks)} 个任务，分 {len(execution_levels)} 个执行层级")
            
            # 逐层执行任务
            for level_index, tasks_in_level in enumerate(execution_levels):
                logger.info(f"执行第 {level_index + 1} 层任务: {tasks_in_level}")
                
                if len(tasks_in_level) == 1:
                    # 单个任务，直接执行
                    task_type = tasks_in_level[0]
                    result = self._execute_single_task(task_type, state)
                    if result:
                        state.add_analysis_result(task_type, result)
                else:
                    # 多个任务，并行执行
                    parallel_results = self._execute_parallel_tasks(tasks_in_level, state)
                    for task_type, result in parallel_results.items():
                        if result:
                            state.add_analysis_result(task_type, result)
            
            logger.info(f"工作流执行完成，共完成 {len(state.completed_tasks)} 个任务")
            return state
            
        except Exception as e:
            logger.error(f"工作流执行失败: {e}", exc_info=True)
            return state
    
    def _execute_single_task(self, task_type: str, state: DiagnosisState) -> Optional[AnalysisResult]:
        """执行单个任务"""
        logger.info(f"执行单个任务: {task_type}")
        
        try:
            # 根据任务类型选择合适的agent
            agent = self._select_agent_for_task(task_type)
            if not agent:
                logger.warning(f"未找到适合任务 {task_type} 的agent")
                return None
            
            # 准备任务参数
            task_params = self._prepare_task_parameters(task_type, state)
            
            # 创建任务
            task = self.task_registry.create_task(task_type, agent, **task_params)
            
            # 执行任务
            crew = Crew(
                agents=[agent],
                tasks=[task],
                process=Process.sequential,
                verbose=False
            )
            
            start_time = time.time()
            result = crew.kickoff()
            execution_time = time.time() - start_time
            
            # 包装结果
            return AnalysisResult(
                task_type=task_type,
                result_data=self._parse_task_result(result.raw),
                execution_time=execution_time,
                success=True
            )
            
        except Exception as e:
            logger.error(f"任务 {task_type} 执行失败: {e}")
            return AnalysisResult(
                task_type=task_type,
                result_data={},
                execution_time=0.0,
                success=False,
                error_message=str(e)
            )
    
    def _execute_parallel_tasks(self, task_types: List[str], state: DiagnosisState) -> Dict[str, Optional[AnalysisResult]]:
        """并行执行多个任务"""
        logger.info(f"并行执行任务: {task_types}")
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=min(len(task_types), self.max_parallel_tasks)) as executor:
            # 提交所有任务
            future_to_task = {
                executor.submit(self._execute_single_task, task_type, state): task_type
                for task_type in task_types
            }
            
            # 收集结果
            for future in as_completed(future_to_task):
                task_type = future_to_task[future]
                try:
                    result = future.result()
                    results[task_type] = result
                    if result and result.success:
                        logger.info(f"并行任务 {task_type} 完成，耗时: {result.execution_time:.2f}s")
                    else:
                        logger.warning(f"并行任务 {task_type} 失败")
                except Exception as e:
                    logger.error(f"并行任务 {task_type} 异常: {e}")
                    results[task_type] = AnalysisResult(
                        task_type=task_type,
                        result_data={},
                        execution_time=0.0,
                        success=False,
                        error_message=str(e)
                    )
        
        return results
    
    def _select_agent_for_task(self, task_type: str) -> Optional[Agent]:
        """为任务选择合适的agent"""
        agent_mapping = {
            # 分类任务使用通用的智能agent（在分类阶段已处理）
            'input_classification': None,  # 已在分类阶段处理
            'pattern_extraction': None,    # 已在分类阶段处理
            
            # 告警分析任务
            'alert_triage': self.agents['alert_triage'],
            'alert_component_identification': self.agents['alert_component'],
            'alert_log_search_params': self.agents['alert_log_strategy'],
            'alert_business_impact': self.agents['alert_business_impact'],
            
            # Jira分析任务
            'jira_basic_info': self.agents['jira_fetcher'],
            'jira_categorization': self.agents['jira_categorizer'],
            'jira_components_analysis': self.agents['jira_tech_analyzer'],
            'jira_context_enrichment': self.agents['jira_context_enricher'],
            
            # 日志分析任务
            'log_search_execution': self.agents['log_executor'],
            'log_pattern_analysis': self.agents['log_pattern'],
            'log_anomaly_detection': self.agents['log_anomaly'],
            'log_correlation_analysis': self.agents['log_correlation'],
            
            # 综合分析任务
            'timeline_reconstruction': self.agents['timeline_reconstructor'],
            'root_cause_hypothesis': self.agents['root_cause_generator'],
            'hypothesis_validation': self.agents['hypothesis_validator'],
            'solution_architecture': self.agents['solution_architect'],
            'comprehensive_report': self.agents['report_generator']
        }
        
        return agent_mapping.get(task_type)
    
    def _prepare_task_parameters(self, task_type: str, state: DiagnosisState) -> Dict[str, Any]:
        """为任务准备参数"""
        base_params = {}
        
        # 根据任务类型准备特定参数
        if task_type.startswith('alert_'):
            base_params['alert_text'] = state.input_text
            if task_type == 'alert_component_identification':
                # 可以使用之前的分析结果
                pass
            elif task_type == 'alert_log_search_params':
                component_result = state.get_analysis_result('alert_component_identification')
                if component_result:
                    base_params['components'] = component_result.result_data
                else:
                    base_params['components'] = {}
            elif task_type == 'alert_business_impact':
                component_result = state.get_analysis_result('alert_component_identification')
                if component_result:
                    base_params['components'] = component_result.result_data
                else:
                    base_params['components'] = {}
                    
        elif task_type.startswith('jira_'):
            if state.jira_issues:
                base_params['issue_key'] = state.jira_issues[0]  # 使用第一个Issue Key
            if task_type == 'jira_categorization':
                info_result = state.get_analysis_result('jira_basic_info')
                if info_result:
                    base_params['issue_content'] = str(info_result.result_data)
                else:
                    base_params['issue_content'] = state.input_text
            elif task_type == 'jira_components_analysis':
                info_result = state.get_analysis_result('jira_basic_info')
                if info_result:
                    base_params['issue_content'] = str(info_result.result_data)
                else:
                    base_params['issue_content'] = state.input_text
            elif task_type == 'jira_context_enrichment':
                info_result = state.get_analysis_result('jira_basic_info')
                components_result = state.get_analysis_result('jira_components_analysis')
                base_params['issue_info'] = info_result.result_data if info_result else {}
                base_params['components'] = components_result.result_data if components_result else {}
                
        elif task_type.startswith('log_'):
            if task_type == 'log_search_execution':
                # 从告警分析结果或默认参数获取搜索参数
                search_params_result = state.get_analysis_result('alert_log_search_params')
                if search_params_result and search_params_result.result_data:
                    params_data = search_params_result.result_data
                    base_params['applications'] = params_data.get('applications', ['default-app'])
                    base_params['query'] = params_data.get('search_queries', [{'query': 'ERROR'}])[0]['query']
                else:
                    base_params['applications'] = ['default-app']
                    base_params['query'] = 'ERROR'
            else:
                # 其他日志分析任务需要日志条目
                log_result = state.get_analysis_result('log_search_execution')
                if log_result:
                    base_params['log_entries'] = str(log_result.result_data)
                else:
                    base_params['log_entries'] = 'No log data available'
                    
        elif task_type.startswith('timeline_') or task_type.startswith('root_cause_') or task_type.startswith('hypothesis_') or task_type.startswith('solution_') or task_type.startswith('comprehensive_'):
            # 综合分析任务需要之前的所有结果
            if task_type == 'timeline_reconstruction':
                all_results = {}
                for task_name, result in state.analysis_results.items():
                    if result.success:
                        all_results[task_name] = result.result_data
                base_params['all_data'] = all_results
            elif task_type == 'root_cause_hypothesis':
                timeline_result = state.get_analysis_result('timeline_reconstruction')
                patterns_result = state.get_analysis_result('log_pattern_analysis')
                base_params['timeline'] = timeline_result.result_data if timeline_result else {}
                base_params['patterns'] = patterns_result.result_data if patterns_result else {}
            elif task_type == 'hypothesis_validation':
                hypothesis_result = state.get_analysis_result('root_cause_hypothesis')
                all_data = {task: result.result_data for task, result in state.analysis_results.items() if result.success}
                base_params['hypotheses'] = hypothesis_result.result_data if hypothesis_result else {}
                base_params['available_data'] = all_data
            elif task_type == 'solution_architecture':
                validated_result = state.get_analysis_result('hypothesis_validation')
                all_data = {task: result.result_data for task, result in state.analysis_results.items() if result.success}
                base_params['validated_root_cause'] = validated_result.result_data if validated_result else {}
                base_params['context'] = all_data
            elif task_type == 'comprehensive_report':
                all_results = {task: result.result_data for task, result in state.analysis_results.items() if result.success}
                base_params['all_analysis_results'] = all_results
        
        return base_params
    
    def _parse_task_result(self, raw_result: str) -> Dict[str, Any]:
        """解析任务结果"""
        try:
            # 尝试解析JSON结果
            import json
            if '{' in raw_result and '}' in raw_result:
                start_idx = raw_result.find('{')
                end_idx = raw_result.rfind('}') + 1
                json_str = raw_result[start_idx:end_idx]
                return json.loads(json_str)
        except Exception as e:
            logger.warning(f"结果解析失败: {e}")
        
        # 解析失败，返回原始文本
        return {'raw_output': raw_result}

import time 