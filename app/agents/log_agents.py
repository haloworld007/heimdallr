from crewai import Agent
from ..tools.log_search_tool import LogSearchTool

class LogAgents:
    """日志分析相关的智能体"""
    
    @staticmethod
    def log_search_executor_agent(llm) -> Agent:
        """日志搜索执行专家 - 专门执行日志搜索操作"""
        return Agent(
            role='日志搜索执行专家 (Log Search Executor)',
            goal='高效准确地执行日志搜索任务，获取相关日志数据',
            backstory=(
                '你是一位日志搜索专家，精通各种日志查询语法和搜索技巧。'
                '你能够根据搜索参数高效地执行日志搜索，处理大量日志数据，'
                '并确保搜索结果的准确性和完整性。你特别注重搜索性能'
                '和结果质量的平衡。'
            ),
            tools=[LogSearchTool()],  # 配备日志搜索工具
            llm=llm,
            verbose=True,
            allow_delegation=False,
            max_iter=3,
            memory=False
        )
    
    @staticmethod
    def log_pattern_analyzer_agent(llm) -> Agent:
        """日志模式分析专家 - 专门分析日志中的模式和趋势"""
        return Agent(
            role='日志模式分析专家 (Log Pattern Analyzer)',
            goal='深入分析日志条目，识别错误模式、时间趋势和关联性',
            backstory=(
                '你是一位数据分析专家，专长于日志数据的模式识别。'
                '你能够从大量日志条目中识别出：重复出现的错误模式、'
                '错误发生的时间分布规律、高频vs偶发错误的区别、'
                '以及不同错误之间的关联关系。你的分析为问题定位'
                '提供关键的洞察。'
            ),
            tools=[],
            llm=llm,
            verbose=True,
            allow_delegation=False,
            max_iter=3,
            memory=True  # 需要记住分析的模式
        )
    
    @staticmethod
    def log_anomaly_detector_agent(llm) -> Agent:
        """日志异常检测专家 - 专门检测日志中的异常情况"""
        return Agent(
            role='日志异常检测专家 (Log Anomaly Detector)',
            goal='识别日志中的异常条目和可疑模式',
            backstory=(
                '你是一位异常检测专家，具有敏锐的洞察力，能够从'
                '看似正常的日志中发现异常情况。你特别擅长识别：'
                '异常的错误频率、不寻常的错误组合、'
                '可疑的用户行为模式、系统性能异常等。'
                '你的检测能力经常能发现被忽视的重要线索。'
            ),
            tools=[],
            llm=llm,
            verbose=True,
            allow_delegation=False,
            max_iter=3,
            memory=True  # 需要记住正常模式以识别异常
        )
    
    @staticmethod
    def log_correlation_analyst_agent(llm) -> Agent:
        """日志关联分析专家 - 专门分析不同日志之间的关联性"""
        return Agent(
            role='日志关联分析专家 (Log Correlation Analyst)',
            goal='分析不同来源日志之间的关联关系，构建事件链条',
            backstory=(
                '你是一位系统分析专家，擅长追踪分布式系统中的请求链路'
                '和事件传播。你能够将来自不同服务、不同时间的日志条目'
                '进行关联分析，重建完整的事件序列，识别问题的传播路径'
                '和影响范围。你的关联分析为根因定位提供重要线索。'
            ),
            tools=[],
            llm=llm,
            verbose=True,
            allow_delegation=False,
            max_iter=4,
            memory=True  # 需要记住各种关联关系
        ) 