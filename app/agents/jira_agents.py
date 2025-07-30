from crewai import Agent
from ..tools.jira_search_tool import JiraSearchTool

class JiraAgents:
    """Jira分析相关的智能体"""
    
    @staticmethod
    def jira_fetcher_agent(llm) -> Agent:
        """Jira信息获取专家 - 专门负责获取Jira工单信息"""
        return Agent(
            role='Jira信息获取专家 (Jira Information Fetcher)',
            goal='准确快速地获取Jira工单的详细信息',
            backstory=(
                '你是一位精通Jira系统的专家，能够高效地从Jira中获取'
                '工单的完整信息：标题、描述、状态、优先级、报告人、'
                '负责人、创建时间、更新时间等。你确保获取的信息'
                '完整准确，为后续分析提供可靠的数据基础。'
            ),
            tools=[JiraSearchTool()],  # 配备Jira搜索工具
            llm=llm,
            verbose=True,
            allow_delegation=False,
            max_iter=3,
            memory=False
        )
    
    @staticmethod
    def jira_categorizer_agent(llm) -> Agent:
        """Jira工单分类专家 - 专门分析工单的问题类别"""
        return Agent(
            role='Jira工单分类专家 (Jira Issue Categorizer)',
            goal='准确分析Jira工单的问题类别、业务领域和复杂度',
            backstory=(
                '你是一位项目管理和需求分析专家，具有丰富的软件开发'
                '和运维经验。你能够从工单描述中准确识别问题的技术类别'
                '(BUG、FEATURE、PERFORMANCE、SECURITY等)、'
                '业务领域(PAYMENT、USER_MANAGEMENT、API等)、'
                '紧急程度和复杂度评估。你的分类为处理优先级'
                '和资源分配提供重要依据。'
            ),
            tools=[],
            llm=llm,
            verbose=True,
            allow_delegation=False,
            max_iter=2,
            memory=False
        )
    
    @staticmethod
    def jira_technical_analyzer_agent(llm) -> Agent:
        """Jira技术分析专家 - 专门分析工单涉及的技术组件"""
        return Agent(
            role='Jira技术分析专家 (Technical Component Analyzer)',
            goal='识别Jira工单涉及的技术组件和系统依赖',
            backstory=(
                '你是一位技术架构师，对各种技术栈和系统架构非常熟悉。'
                '你能够从工单描述中识别出涉及的具体技术组件：'
                '服务/应用名称、相关数据库、API接口、第三方依赖等。'
                '你还能推荐相应的日志搜索目标，为后续的技术调查'
                '提供精确的方向指导。'
            ),
            tools=[],
            llm=llm,
            verbose=True,
            allow_delegation=False,
            max_iter=3,
            memory=False
        )
    
    @staticmethod
    def jira_context_enricher_agent(llm) -> Agent:
        """Jira上下文富化专家 - 专门收集工单相关的上下文信息"""
        return Agent(
            role='Jira上下文富化专家 (Context Enricher)',
            goal='收集和整理与Jira工单相关的所有上下文信息',
            backstory=(
                '你是一位信息整合专家，擅长从各种渠道收集和关联信息。'
                '你能够将Jira工单信息与系统日志、监控数据、'
                '相关文档等进行关联，构建完整的问题上下文。'
                '你的信息整合能力为问题的全面理解提供重要支持。'
            ),
            tools=[],  # 可能需要多种工具，后续扩展
            llm=llm,
            verbose=True,
            allow_delegation=False,
            max_iter=3,
            memory=True  # 上下文富化需要记住相关信息
        ) 