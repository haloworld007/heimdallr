
from crewai import Task
from typing import List, Optional

class RootCauseAnalysisTask(Task):
    def __init__(self, agent, context: Optional[List[Task]] = None):
        super().__init__(
            description='基于富化的上下文信息，分析问题的根本原因。从技术层面和业务层面进行深度分析，找出导致告警的真正原因。',
            expected_output='一份详细的根本原因分析报告，包含问题的技术原因和影响分析。',
            agent=agent,
            context=context or []
        )
