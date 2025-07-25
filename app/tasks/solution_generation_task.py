
from crewai import Task
from typing import List, Optional

class SolutionGenerationTask(Task):
    def __init__(self, agent, context: Optional[List[Task]] = None):
        super().__init__(
            description='基于根本原因分析，设计具体的解决方案。包括即时解决方案、长期预防措施和监控建议。',
            expected_output='一份完整的解决方案文档，包含immediate actions、长期解决方案和预防措施。',
            agent=agent,
            context=context or []
        )
