
from crewai import Agent
from app.tools.search_tools import SearchTools

class EnrichmentAgent(Agent):
    def __init__(self, llm):
        super().__init__(
            role='信息富化专员 (Data Detective)',
            goal='根据告警的分类结果，收集所有相关的上下文信息，如日志、指标和配置。',
            backstory='你如同一个数据侦探，精通各种监控和日志系统。你的任务是为告警提供最全面的背景信息，帮助团队理解问题的全貌。',
            tools=[SearchTools()],
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
