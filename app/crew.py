import logging
from crewai import Crew, Process
from app.agents import (
    TriageAgent, 
    EnrichmentAgent, 
    RootCauseAnalysisAgent, 
    SolutionsArchitectAgent, 
    CommunicationsOfficerAgent
)
from app.tasks import (
    TriageTask, 
    EnrichmentTask, 
    RootCauseAnalysisTask, 
    SolutionGenerationTask, 
    ReportingTask
)
from app.llms import llm_manager

# 获取一个日志记录器实例
logger = logging.getLogger(__name__)

class HeimdallrCrew:

    def __init__(self, issue: str):
        self.issue = issue
        # 初始化一个通用的 LLM 实例
        self.llm = llm_manager.get_llm()

    def setup_crew(self):
        logger.info("开始组建 Crew...")
        # 为每一个 Agent 显式注入 LLM 实例
        triage_agent = TriageAgent(llm=self.llm)
        enrichment_agent = EnrichmentAgent(llm=self.llm)
        rca_agent = RootCauseAnalysisAgent(llm=self.llm)
        solution_agent = SolutionsArchitectAgent(llm=self.llm)
        communication_agent = CommunicationsOfficerAgent(llm=self.llm)
        logger.debug("所有 Agent 已使用通用 LLM 初始化。")

        # 创建任务
        triage_task = TriageTask(agent=triage_agent, issue=self.issue)
        enrichment_task = EnrichmentTask(agent=enrichment_agent, context=[triage_task])
        rca_task = RootCauseAnalysisTask(agent=rca_agent, context=[enrichment_task])
        solution_task = SolutionGenerationTask(agent=solution_agent, context=[rca_task])
        reporting_task = ReportingTask(
            agent=communication_agent, 
            context=[triage_task, enrichment_task, rca_task, solution_task]
        )
        logger.debug("所有 Task 已创建。")

        # 组建Crew
        crew = Crew(
            agents=[
                triage_agent, 
                enrichment_agent, 
                rca_agent, 
                solution_agent, 
                communication_agent
            ],
            tasks=[
                triage_task, 
                enrichment_task, 
                rca_task, 
                solution_task, 
                reporting_task
            ],
            process=Process.sequential,
            # 注意：当所有 agent 都被指定了 llm 时，这里的 llm 参数是可选的
            # 但为了清晰，我们仍然可以保留它作为备用
            llm=self.llm,
            verbose=True
        )
        logger.info("Crew 组建完成。")
        return crew
