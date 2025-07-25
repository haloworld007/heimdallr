
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
import httpx

class HeimdallrCrew:

    def __init__(self, issue: str, response_url: str):
        self.issue = issue
        self.response_url = response_url
        self.fast_llm = llm_manager.get_fast_llm()
        self.smart_llm = llm_manager.get_smart_llm()

    def _create_callback(self):
        def post_report_callback(task_output):
            """任务完成后的回调函数，将报告发送到指定URL。"""
            report = task_output.raw_output
            print(f"执行回调，将报告发送到: {self.response_url}")
            try:
                with httpx.Client() as client:
                    response = client.post(self.response_url, json={"report": report}, timeout=10.0)
                    response.raise_for_status() # 如果响应状态码不是 2xx，则引发异常
                print(f"回调成功，响应状态: {response.status_code}")
            except httpx.RequestError as e:
                print(f"回调请求失败: {e}")
        return post_report_callback

    def setup_crew(self):
        # 为每个Agent分配最合适的LLM
        triage_agent = TriageAgent(llm=self.fast_llm)
        enrichment_agent = EnrichmentAgent(llm=self.smart_llm)
        rca_agent = RootCauseAnalysisAgent(llm=self.smart_llm)
        solution_agent = SolutionsArchitectAgent(llm=self.smart_llm)
        communication_agent = CommunicationsOfficerAgent(llm=self.fast_llm)

        # 创建任务，并为最终的报告任务附加回调函数
        triage_task = TriageTask(agent=triage_agent, issue=self.issue)
        enrichment_task = EnrichmentTask(agent=enrichment_agent, context=[triage_task])
        rca_task = RootCauseAnalysisTask(agent=rca_agent, context=[enrichment_task])
        solution_task = SolutionGenerationTask(agent=solution_agent, context=[rca_task])
        reporting_task = ReportingTask(
            agent=communication_agent, 
            context=[triage_task, enrichment_task, rca_task, solution_task],
            callback=self._create_callback()
        )

        # 组建Crew
        return Crew(
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
            verbose=2
        )
