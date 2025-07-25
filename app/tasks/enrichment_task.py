
from crewai import Task
from typing import List, Optional

class EnrichmentTask(Task):
    def __init__(self, agent, context: Optional[List[Task]] = None):
        super().__init__(
            description='根据前一步的分类结果，收集相关的上下文信息。如果告警类型是DATABASE，就去查询慢日志；如果是APPLICATION，就去搜索错误日志。将你收集到的所有信息整合成一份上下文报告。',
            expected_output='一份整合了所有相关日志、指标和配置的上下文报告。',
            agent=agent,
            context=context or []
        )
