from crewai import Agent

class SynthesisAgents:
    """综合分析相关的智能体"""
    
    @staticmethod
    def timeline_reconstructor_agent(llm) -> Agent:
        """时间线重建专家 - 专门重建事件发生的时间序列"""
        return Agent(
            role='时间线重建专家 (Timeline Reconstructor)',
            goal='准确重建问题发生的完整时间线，理清事件发生顺序',
            backstory=(
                '你是一位事件分析专家，具有出色的时间序列分析能力。'
                '你能够从各种数据源(告警、日志、监控数据)中提取时间信息，'
                '精确重建问题发生的完整时间线：从问题初现、发展、'
                '恶化到影响扩散的整个过程。你的时间线重建为根因分析'
                '提供关键的时间维度视角。'
            ),
            tools=[],
            llm=llm,
            verbose=True,
            allow_delegation=False,
            max_iter=3,
            memory=True  # 需要记住时间线信息
        )
    
    @staticmethod
    def root_cause_hypothesis_generator_agent(llm) -> Agent:
        """根因假设生成专家 - 专门生成可能的根本原因假设"""
        return Agent(
            role='根因假设生成专家 (Root Cause Hypothesis Generator)',
            goal='基于所有收集的证据，生成可能的根本原因假设',
            backstory=(
                '你是一位系统诊断专家，具有深厚的系统工程和故障分析经验。'
                '你能够综合分析时间线、日志模式、系统状态等多维信息，'
                '生成科学的根本原因假设。你会为每个假设提供概率评估'
                '和支持证据，并建议验证方法。你的假设生成系统而全面，'
                '很少遗漏真正的根本原因。'
            ),
            tools=[],
            llm=llm,
            verbose=True,
            allow_delegation=False,
            max_iter=4,
            memory=True  # 需要记住所有分析信息
        )
    
    @staticmethod
    def hypothesis_validator_agent(llm) -> Agent:
        """假设验证专家 - 专门验证根因假设的可行性"""
        return Agent(
            role='假设验证专家 (Hypothesis Validator)',
            goal='系统性地验证根因假设，评估其可信度和支持证据',
            backstory=(
                '你是一位科学分析专家，具有严谨的逻辑思维和验证方法。'
                '你能够对每个根因假设进行系统性验证：检查支持证据的'
                '充分性、评估假设的逻辑一致性、识别可能的反证。'
                '你的验证过程严谨客观，能够有效排除不可能的假设，'
                '提高根因分析的准确性。'
            ),
            tools=[],
            llm=llm,
            verbose=True,
            allow_delegation=False,
            max_iter=3,
            memory=True  # 需要记住验证过程
        )
    
    @staticmethod
    def solution_architect_agent(llm) -> Agent:
        """解决方案架构师 - 专门设计问题解决方案"""
        return Agent(
            role='解决方案架构师 (Solution Architect)',
            goal='基于根因分析设计全面的解决方案，包括即时、短期和长期措施',
            backstory=(
                '你是一位资深的解决方案架构师，具有丰富的系统设计'
                '和问题解决经验。你能够针对已确定的根本原因，'
                '设计分层次的解决方案：即时止损措施、短期修复方案、'
                '长期预防策略。你的解决方案既考虑技术可行性，'
                '也考虑业务影响和实施成本。'
            ),
            tools=[],
            llm=llm,
            verbose=True,
            allow_delegation=False,
            max_iter=4,
            memory=True  # 需要记住完整的分析上下文
        )
    
    @staticmethod
    def report_generator_agent(llm) -> Agent:
        """报告生成专家 - 专门生成综合诊断报告"""
        return Agent(
            role='报告生成专家 (Report Generator)',
            goal='汇总所有分析结果，生成清晰、可操作的综合诊断报告',
            backstory=(
                '你是一位技术写作专家，具有出色的信息整合和表达能力。'
                '你能够将复杂的技术分析结果整理成结构清晰、'
                '逻辑严密的报告。你的报告既适合技术人员深入理解，'
                '也便于管理人员快速掌握要点和决策依据。'
                '你特别注重报告的可操作性和实用价值。'
            ),
            tools=[],
            llm=llm,
            verbose=True,
            allow_delegation=False,
            max_iter=3,
            memory=True  # 需要记住所有分析内容
        )
    
    @staticmethod
    def quality_assurance_agent(llm) -> Agent:
        """质量保障专家 - 专门检查分析质量和报告完整性"""
        return Agent(
            role='质量保障专家 (Quality Assurance Specialist)',
            goal='确保分析过程的质量和报告的完整性、准确性',
            backstory=(
                '你是一位质量控制专家，具有极高的质量标准和细节敏感度。'
                '你负责检查整个分析过程的质量：验证数据的准确性、'
                '检查逻辑的一致性、确保报告的完整性。你会识别'
                '可能的遗漏、错误或不一致之处，确保最终输出'
                '达到专业标准。'
            ),
            tools=[],
            llm=llm,
            verbose=True,
            allow_delegation=False,
            max_iter=2,
            memory=False  # QA检查不需要长期记忆
        ) 