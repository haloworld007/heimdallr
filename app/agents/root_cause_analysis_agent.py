
from crewai import Agent

class RootCauseAnalysisAgent(Agent):
    def __init__(self, llm):
        super().__init__(
            role='根因分析师 (Root Cause Analyst)',
            goal='深入分析富化后的信息，找出问题的根本原因。',
            backstory='你是一位逻辑缜密、经验丰富的系统分析师。你能够从纷繁复杂的数据中，通过推理和关联，定位到问题的核心。',
            tools=[],
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
