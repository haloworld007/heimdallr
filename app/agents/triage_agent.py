from crewai import Agent

class TriageAgent(Agent):
    def __init__(self, llm):
        super().__init__(
            role='告警分类专家 (Triage Specialist)',
            goal='分析并分类传入的告警，确定其严重性、类型和影响的组件。',
            backstory='你是一位经验丰富的运维工程师，擅长快速从大量告警中识别出关键问题并进行分类，为后续的分析提供清晰的指引。',
            tools=[],
            llm=llm,
            verbose=True,
            allow_delegation=False,
        )
