from pydantic import BaseModel, Field
from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime

class InputType(Enum):
    """输入类型枚举"""
    ALERT = "alert"           # 告警信息
    JIRA_ISSUE = "jira_issue" # Jira Issue Key
    LOG_QUERY = "log_query"   # 日志查询请求
    HYBRID = "hybrid"         # 混合类型（包含多种信息）
    UNKNOWN = "unknown"       # 未知类型

class ClassificationResult(BaseModel):
    """分类结果模型"""
    input_type: InputType
    confidence: float = Field(ge=0.0, le=1.0, description="分类置信度")
    extracted_data: Dict[str, Any] = Field(default_factory=dict)
    reasoning: str = ""

class AnalysisResult(BaseModel):
    """分析结果模型"""
    task_type: str
    result_data: Dict[str, Any] = Field(default_factory=dict)
    execution_time: float = 0.0
    success: bool = True
    error_message: Optional[str] = None

class DiagnosisState(BaseModel):
    """诊断流程状态模型"""
    
    # 输入信息
    input_text: str = ""
    input_timestamp: datetime = Field(default_factory=datetime.now)
    
    # 分类结果
    classification: Optional[ClassificationResult] = None
    
    # 提取的关键信息
    jira_issues: List[str] = Field(default_factory=list)
    alert_info: Dict[str, Any] = Field(default_factory=dict)
    log_search_params: Dict[str, Any] = Field(default_factory=dict)
    
    # 分析结果存储
    analysis_results: Dict[str, AnalysisResult] = Field(default_factory=dict)
    
    # 工作流控制
    current_workflow: str = ""
    completed_tasks: List[str] = Field(default_factory=list)
    failed_tasks: List[str] = Field(default_factory=list)
    
    # 最终输出
    final_report: str = ""
    recommendations: List[str] = Field(default_factory=list)
    
    # 元数据
    flow_id: str = ""
    total_execution_time: float = 0.0
    
    def add_analysis_result(self, task_type: str, result: AnalysisResult):
        """添加分析结果"""
        self.analysis_results[task_type] = result
        if result.success:
            self.completed_tasks.append(task_type)
        else:
            self.failed_tasks.append(task_type)
    
    def get_analysis_result(self, task_type: str) -> Optional[AnalysisResult]:
        """获取分析结果"""
        return self.analysis_results.get(task_type)
    
    def is_task_completed(self, task_type: str) -> bool:
        """检查任务是否完成"""
        return task_type in self.completed_tasks
    
    def get_workflow_progress(self) -> Dict[str, Any]:
        """获取工作流进度"""
        return {
            "current_workflow": self.current_workflow,
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "total_results": len(self.analysis_results),
            "classification": self.classification.dict() if self.classification else None
        } 