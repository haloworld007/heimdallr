
from crewai import Agent

class CommunicationsOfficerAgent(Agent):
    def __init__(self, llm):
        super().__init__(
            role='沟通联络官 (Communications Officer)',
            goal='将整个分析过程和最终结论，汇总成一份清晰、简洁的报告。',
            backstory='你是一位出色的沟通专家，擅长将复杂的技术问题，用通俗易懂的语言呈现给不同的干系人。你的报告是团队与外界沟通的关键桥梁。',
            tools=[],
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
