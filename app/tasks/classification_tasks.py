from crewai import Task, Agent
from .base_task_factory import BaseTaskFactory

class InputClassificationTaskFactory(BaseTaskFactory):
    """输入分类任务工厂"""
    
    def create_task(self, agent: Agent, input_text: str, **kwargs) -> Task:
        """创建输入分类任务"""
        self._validate_required_params(['input_text'], {'input_text': input_text})
        
        json_schema = """{
    "input_type": "alert|jira_issue|log_query|hybrid|unknown",
    "confidence": 0.95,
    "extracted_data": {
        "jira_issues": ["PROJ-123"],
        "alert_keywords": ["error", "timeout"],
        "log_keywords": ["search", "application"],
        "other_patterns": {}
    },
    "reasoning": "详细的分类判断理由"
}"""
        
        description = f"""分析以下输入内容，确定其类型和提取关键信息：

输入内容：
{input_text}

请精确判断输入类型：
1. alert - 告警信息（包含错误、异常、监控相关内容）
2. jira_issue - Jira工单（包含类似PROJ-123格式的Issue Key）
3. log_query - 日志查询请求（包含日志搜索、查询相关内容）
4. hybrid - 混合类型（包含多种上述类型的信息）
5. unknown - 无法明确分类

分析要求：
- 检查是否包含Jira Issue Key格式（字母-数字）
- 识别告警相关关键词
- 识别日志查询相关关键词
- 评估分类置信度
- 提取所有识别到的关键信息

{self._build_json_output_instruction(json_schema)}"""
        
        return Task(
            description=description,
            expected_output="包含输入类型、置信度、提取数据和判断理由的JSON对象",
            agent=agent
        )

class PatternExtractionTaskFactory(BaseTaskFactory):
    """模式提取任务工厂"""
    
    def create_task(self, agent: Agent, input_text: str, target_patterns: list = None, **kwargs) -> Task:
        """创建模式提取任务"""
        self._validate_required_params(['input_text'], {'input_text': input_text})
        
        if target_patterns is None:
            target_patterns = ['jira_issues', 'error_codes', 'timestamps', 'service_names', 'ip_addresses']
        
        patterns_description = ", ".join(target_patterns)
        
        json_schema = """{
    "extracted_patterns": {
        "jira_issues": ["PROJ-123", "TASK-456"],
        "error_codes": ["HTTP_500", "TIMEOUT_ERROR"],
        "timestamps": ["2024-01-15 14:30:00"],
        "service_names": ["user-service", "payment-api"],
        "ip_addresses": ["192.168.1.100"],
        "other_identifiers": ["custom patterns found"]
    },
    "confidence_scores": {
        "jira_issues": 0.95,
        "error_codes": 0.88
    },
    "extraction_summary": "提取结果的简要说明"
}"""
        
        description = f"""从以下文本中精确提取指定的模式和标识符：

输入文本：
{input_text}

目标提取模式：{patterns_description}

提取要求：
1. Jira Issue Key - 格式如PROJ-123, TASK-456等
2. 错误代码 - HTTP状态码、异常类型、错误标识
3. 时间戳 - 各种格式的时间信息
4. 服务名称 - 应用名、服务名、组件名
5. IP地址 - IPv4和IPv6地址
6. 其他重要标识符

为每个提取结果提供置信度评分（0-1）。

{self._build_json_output_instruction(json_schema)}"""
        
        return Task(
            description=description,
            expected_output="包含提取模式、置信度评分和提取摘要的JSON对象",
            agent=agent
        ) 