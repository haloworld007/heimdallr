import logging
import uuid
import time
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

from crewai.flow.flow import Flow, listen, router, start
from crewai import Agent, Task, Crew, Process, LLM

from .flow_state import DiagnosisState, InputType, ClassificationResult, AnalysisResult
from .llms import llm_registry
from .classification_engine import ClassificationEngine, PatternExtractor
from .dynamic_workflow_router import DynamicWorkflowRouter

logger = logging.getLogger(__name__)

class HeimdallrFlow(Flow[DiagnosisState]):
    """Heimdallr AI诊断助手主流程"""
    
    def __init__(self, input_text: str = ""):
        super().__init__()
        
        # 保存输入文本
        self.input_text = input_text
        
        # 初始化LLM
        self.llm = llm_registry.get("default")
        
        # 初始化分类引擎和模式提取器
        self.classification_engine = ClassificationEngine(self.llm)
        self.pattern_extractor = PatternExtractor(self.llm)
        
        # 初始化动态工作流路由器
        self.workflow_router = DynamicWorkflowRouter(self.llm)
        
        logger.info(f"初始化HeimdallrFlow，输入文本长度: {len(input_text)}")
    
    @start()
    def classify_input(self):
        """Step 1: 输入分类 - 分析输入内容并确定处理策略"""
        input_text = self.input_text
        logger.info(f"开始输入分类，输入内容: {input_text[:100]}...")
        start_time = time.time()
        
        # 初始化状态
        self.state.input_text = input_text
        self.state.flow_id = str(uuid.uuid4())
        self.state.input_timestamp = datetime.now()
        
        try:
            # 使用新的分类引擎进行分类
            classification_result = self.classification_engine.classify(input_text)
            self.state.classification = classification_result
            self.state.current_workflow = classification_result.input_type.value
            
            # 执行模式提取，丰富分类信息
            extracted_patterns = self.pattern_extractor.extract_patterns(
                self.state.input_text, 
                classification_result
            )
            
            # 将提取的模式信息合并到状态中
            if extracted_patterns:
                self.state.classification.extracted_data.update(extracted_patterns)
            
            # 根据分类结果更新状态中的特定信息
            self._update_state_from_classification(classification_result)
            
            execution_time = time.time() - start_time
            logger.info(f"输入分类完成: {classification_result.input_type.value}, "
                       f"置信度: {classification_result.confidence:.2f}, "
                       f"耗时: {execution_time:.2f}s")
            
            return classification_result.input_type.value
            
        except Exception as e:
            logger.error(f"输入分类失败: {e}")
            # 默认当作未知类型处理
            fallback_result = ClassificationResult(
                input_type=InputType.UNKNOWN,
                confidence=0.1,
                reasoning=f"分类过程出错: {str(e)}"
            )
            self.state.classification = fallback_result
            self.state.current_workflow = "unknown"
            return "unknown"
    
    @router(classify_input)
    def route_by_input_type(self, input_type: str):
        """Step 2: 路由决策 - 根据输入类型选择处理流程"""
        logger.info(f"路由到工作流: {input_type}")
        
        # 根据分类结果路由到不同的处理流程
        return "input_classified"
    
    @listen("input_classified")
    def execute_dynamic_workflow(self, input_type: str):
        """Step 2: 执行动态工作流 - 根据输入类型选择并执行相应的处理流程"""
        logger.info(f"开始执行动态工作流，输入类型: {input_type}")
        
        try:
            # 使用动态工作流路由器执行分析
            self.workflow_router.route_and_execute(self.state)
            
            # 检查是否有最终报告
            final_report_result = self.state.get_analysis_result('comprehensive_report')
            if final_report_result and final_report_result.success:
                self.state.final_report = final_report_result.result_data.get('raw_output', str(final_report_result.result_data))
            else:
                # 如果没有生成综合报告，生成基础报告
                self.state.final_report = self._get_basic_summary()
            
            # 记录总执行时间
            total_time = time.time() - self.state.input_timestamp.timestamp()
            self.state.total_execution_time = total_time
            
            logger.info(f"动态工作流执行完成，总耗时: {total_time:.2f}s")
            return self.state.final_report
            
        except Exception as e:
            logger.error(f"动态工作流执行失败: {e}", exc_info=True)
            error_report = f"工作流执行失败: {str(e)}\n\n基础分析结果:\n{self._get_basic_summary()}"
            self.state.final_report = error_report
            return error_report
    
    def _update_state_from_classification(self, classification_result: ClassificationResult):
        """根据分类结果更新状态中的特定信息"""
        extracted_data = classification_result.extracted_data
        
        # 更新Jira issues信息
        if 'jira_issues' in extracted_data:
            self.state.jira_issues = extracted_data['jira_issues']
        
        # 更新告警信息
        if classification_result.input_type in [InputType.ALERT, InputType.HYBRID]:
            alert_info = {
                'severity_hints': extracted_data.get('severity_indicators', []),
                'matched_keywords': extracted_data.get('matched_keywords', []),
                'alert_score': extracted_data.get('alert_score', 0.0)
            }
            self.state.alert_info.update(alert_info)
        
        # 更新日志搜索参数
        if classification_result.input_type in [InputType.LOG_QUERY, InputType.HYBRID]:
            log_params = {
                'target_applications': extracted_data.get('application_names', []),
                'suggested_queries': extracted_data.get('log_keywords', []),
                'log_score': extracted_data.get('log_score', 0.0)
            }
            self.state.log_search_params.update(log_params)
    
    def _collect_analysis_results(self) -> Dict[str, Any]:
        """收集所有分析结果"""
        return {
            "classification": self.state.classification.dict() if self.state.classification else {},
            "workflow": self.state.current_workflow,
            "completed_tasks": self.state.completed_tasks,
            "failed_tasks": self.state.failed_tasks,
            "analysis_results": {k: v.dict() for k, v in self.state.analysis_results.items()},
            "execution_time": self.state.total_execution_time
        }
    

    
    def _get_basic_summary(self) -> str:
        """获取基础摘要"""
        classification = self.state.classification
        return f"""
# Heimdallr 诊断报告

## 输入信息
- 输入内容: {self.state.input_text[:200]}...
- 分类结果: {classification.input_type.value if classification else '未知'}
- 置信度: {classification.confidence if classification else 0.0}
- 执行工作流: {self.state.current_workflow}

## 执行状态
- 完成任务: {len(self.state.completed_tasks)}
- 失败任务: {len(self.state.failed_tasks)}
- 总执行时间: {self.state.total_execution_time:.2f}秒

## 基础建议
请查看具体的分析结果以获取详细信息。
        """.strip() 