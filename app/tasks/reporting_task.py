from crewai import Task
from typing import List, Optional, Callable

class ReportingTask(Task):
    def __init__(self, agent, context: Optional[List[Task]] = None, callback: Optional[Callable] = None):
        super().__init__(
            description='将整个分析过程的结果汇总成一份清晰、简洁的报告。报告应包含告警分类、根本原因、解决方案和后续建议。',
            expected_output='一份完整的告警分析报告，格式清晰，内容详实，便于相关人员理解和执行。',
            agent=agent,
            context=context or [],
            callback=callback
        )