from crewai import Agent
from typing import Optional

class ClassificationAgents:
    """输入分类相关的智能体"""
    
    @staticmethod
    def input_classifier_agent(llm) -> Agent:
        """输入分类专家 - 专门负责分析输入内容类型"""
        return Agent(
            role='输入分类专家 (Input Classifier)',
            goal='准确识别和分类各种类型的运维输入：告警、Jira工单、日志查询等',
            backstory=(
                '你是一位拥有10年以上运维经验的专家，见过各种类型的运维请求。'
                '你能够快速准确地识别输入内容的性质：是告警信息、Jira工单编号、'
                '日志查询请求，还是包含多种信息的混合类型。你的分类准确性极高，'
                '为后续的专业化处理提供可靠的依据。'
            ),
            tools=[],  # 分类不需要外部工具，纯AI分析
            llm=llm,
            verbose=True,
            allow_delegation=False,
            max_iter=3,
            memory=False  # 分类任务不需要记忆
        )
    
    @staticmethod
    def pattern_extraction_agent(llm) -> Agent:
        """模式提取专家 - 专门从输入中提取关键模式和信息"""
        return Agent(
            role='模式提取专家 (Pattern Extractor)',
            goal='从输入文本中精确提取关键信息：Jira Issue Key、错误码、时间戳、组件名称等',
            backstory=(
                '你是一位精通正则表达式和文本解析的专家，能够从非结构化文本中'
                '准确提取各种关键信息。你特别擅长识别Jira Issue Key格式、'
                '各种错误代码模式、时间戳格式、服务名称等技术标识。'
                '你的提取准确率接近100%，是信息处理流程的关键环节。'
            ),
            tools=[],
            llm=llm,
            verbose=True,
            allow_delegation=False,
            max_iter=2,
            memory=False
        ) 