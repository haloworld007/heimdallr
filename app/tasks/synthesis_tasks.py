from crewai import Task, Agent
from typing import Dict, Any, List
from .base_task_factory import BaseTaskFactory

class TimelineReconstructionTaskFactory(BaseTaskFactory):
    """时间线重建任务工厂 - 重建事件时间序列"""
    
    def create_task(self, agent: Agent, all_data: Dict[str, Any], **kwargs) -> Task:
        self._validate_required_params(['all_data'], {'all_data': all_data})
        
        all_data_text = str(all_data)
        
        json_schema = """{
    "timeline": [
        {
            "timestamp": "2024-01-15T14:20:00Z",
            "event": "首次错误出现",
            "source": "logs|alert|jira|monitoring",
            "details": "具体事件描述",
            "severity": "High|Medium|Low",
            "evidence": "支持证据"
        }
    ],
    "timeline_analysis": {
        "total_duration": "15 minutes",
        "key_inflection_points": ["关键转折点"],
        "escalation_pattern": "gradual|sudden|intermittent",
        "recovery_attempts": ["恢复尝试记录"]
    },
    "event_clusters": [
        {
            "time_range": "14:20-14:25",
            "event_count": 15,
            "cluster_type": "error_burst|normal_activity|recovery_phase",
            "primary_events": ["主要事件"]
        }
    ],
    "causality_analysis": {
        "root_event": "最初触发事件",
        "cascade_events": ["级联事件"],
        "parallel_events": ["并行事件"],
        "unrelated_events": ["无关事件"]
    },
    "timeline_confidence": 0.88,
    "data_gaps": ["时间线中的数据缺口"]
}"""
        
        description = f"""重建问题发生的完整时间线：

收集的所有数据：
{all_data_text}

请按时间顺序重建事件时间线：

1. 事件时间线构建：
   - 提取所有带时间戳的事件
   - 按时间顺序排列事件
   - 标注事件来源（日志/告警/Jira/监控等）
   - 评估每个事件的严重程度
   - 提供支持证据

2. 时间线分析：
   - 计算问题持续的总时长
   - 识别关键的转折点
   - 分析问题恶化的模式
   - 记录任何恢复尝试

3. 事件聚类：
   - 将相近时间的事件聚类
   - 识别错误突发期、正常期、恢复期
   - 统计各时间段的事件数量

4. 因果关系分析：
   - 识别最初的触发事件
   - 分析级联反应链条
   - 区分并行事件和因果事件
   - 排除无关事件

5. 质量评估：
   - 评估时间线重建的置信度
   - 识别数据缺口和不确定性

{self._build_json_output_instruction(json_schema)}"""
        
        return Task(
            description=description,
            expected_output="按时间排序的完整事件时间线JSON对象，包含因果分析和质量评估",
            agent=agent
        )

class RootCauseHypothesisGenerationTaskFactory(BaseTaskFactory):
    """根因假设生成任务工厂 - 生成根本原因假设"""
    
    def create_task(self, agent: Agent, timeline: Dict[str, Any], patterns: Dict[str, Any], 
                   context: Dict[str, Any] = None, **kwargs) -> Task:
        self._validate_required_params(['timeline', 'patterns'], {
            'timeline': timeline,
            'patterns': patterns
        })
        
        timeline_text = str(timeline)
        patterns_text = str(patterns)
        context_text = str(context) if context else "无额外上下文"
        
        json_schema = """{
    "hypotheses": [
        {
            "hypothesis_id": "H001",
            "cause": "数据库连接池耗尽",
            "category": "infrastructure|application|network|external|human_error",
            "probability": 0.8,
            "evidence": [
                "连接超时错误增加",
                "数据库连接数监控异常"
            ],
            "contradicting_evidence": ["可能的反证"],
            "validation_method": "检查数据库连接池配置和监控",
            "supporting_timeline": ["相关时间线事件"],
            "technical_details": "详细技术说明",
            "impact_explanation": "如何导致观察到的症状"
        }
    ],
    "hypothesis_ranking": [
        {
            "rank": 1,
            "hypothesis_id": "H001",
            "score": 0.85,
            "ranking_criteria": "证据强度、概率、可验证性"
        }
    ],
    "excluded_hypotheses": [
        {
            "cause": "已排除的原因",
            "exclusion_reason": "排除理由",
            "exclusion_evidence": ["排除证据"]
        }
    ],
    "investigation_roadmap": {
        "immediate_checks": ["立即需要检查的项目"],
        "detailed_investigation": ["深入调查方向"],
        "experimental_validation": ["实验验证方法"]
    },
    "confidence_assessment": {
        "overall_confidence": 0.75,
        "evidence_strength": "strong|medium|weak",
        "data_completeness": "complete|partial|limited"
    }
}"""
        
        description = f"""基于时间线和模式分析生成根本原因假设：

事件时间线：
{timeline_text}

模式分析结果：
{patterns_text}

上下文信息：
{context_text}

请生成科学的根本原因假设：

1. 假设生成：
   - 基于证据生成3-5个可能的根本原因
   - 为每个假设分配概率评估（0-1）
   - 分类原因类型（基础设施/应用/网络/外部/人为）
   - 提供支持和反对证据
   - 说明如何验证每个假设

2. 假设分析：
   - 详细的技术解释
   - 解释如何导致观察到的症状
   - 分析与时间线的对应关系
   - 评估解决该假设的影响

3. 假设排名：
   - 按可能性和证据强度排序
   - 提供排名标准和评分
   - 突出最可能的根本原因

4. 排除分析：
   - 明确排除的可能原因
   - 提供排除的理由和证据

5. 调查路线图：
   - 建议立即检查的项目
   - 深入调查的方向
   - 实验验证的方法

6. 置信度评估：
   - 整体分析的置信度
   - 证据强度评估
   - 数据完整性评估

{self._build_json_output_instruction(json_schema)}"""
        
        return Task(
            description=description,
            expected_output="包含根因假设、概率评估、证据分析和调查路线图的详细JSON对象",
            agent=agent
        )

class HypothesisValidationTaskFactory(BaseTaskFactory):
    """假设验证任务工厂 - 验证根因假设"""
    
    def create_task(self, agent: Agent, hypotheses: Dict[str, Any], available_data: Dict[str, Any], **kwargs) -> Task:
        self._validate_required_params(['hypotheses', 'available_data'], {
            'hypotheses': hypotheses,
            'available_data': available_data
        })
        
        hypotheses_text = str(hypotheses)
        data_text = str(available_data)
        
        json_schema = """{
    "validation_results": [
        {
            "hypothesis_id": "H001",
            "validation_status": "confirmed|refuted|inconclusive|needs_more_data",
            "evidence_score": 0.85,
            "supporting_evidence": ["强支持证据"],
            "contradicting_evidence": ["反对证据"],
            "additional_evidence_found": ["新发现的证据"],
            "logical_consistency": "consistent|inconsistent|partially_consistent",
            "feasibility_check": "feasible|unlikely|impossible",
            "validation_confidence": 0.82
        }
    ],
    "cross_validation": {
        "consistent_hypotheses": ["相互支持的假设"],
        "conflicting_hypotheses": ["相互冲突的假设"],
        "complementary_hypotheses": ["可能同时成立的假设"]
    },
    "evidence_analysis": {
        "strong_evidence": ["强有力的证据"],
        "weak_evidence": ["薄弱的证据"],
        "missing_evidence": ["缺失的关键证据"],
        "contradictory_evidence": ["矛盾的证据"]
    },
    "updated_probabilities": [
        {
            "hypothesis_id": "H001",
            "original_probability": 0.8,
            "updated_probability": 0.9,
            "probability_change": 0.1,
            "change_reason": "新证据支持"
        }
    ],
    "validation_summary": {
        "most_likely_cause": "最可能的根本原因",
        "confidence_level": "High|Medium|Low",
        "validation_quality": "验证质量评估",
        "next_steps": ["后续验证步骤"]
    }
}"""
        
        description = f"""系统性验证根本原因假设：

待验证假设：
{hypotheses_text}

可用数据：
{data_text}

请进行严格的假设验证：

1. 假设验证：
   - 对每个假设进行独立验证
   - 评估现有证据的支持强度
   - 识别矛盾或反对证据
   - 检查逻辑一致性
   - 评估技术可行性

2. 交叉验证：
   - 分析假设之间的一致性
   - 识别相互冲突的假设
   - 找出可能同时成立的假设

3. 证据分析：
   - 分类证据强度（强/弱）
   - 识别缺失的关键证据
   - 处理矛盾的证据
   - 发现新的支持证据

4. 概率更新：
   - 基于验证结果更新假设概率
   - 记录概率变化和原因
   - 重新排序假设优先级

5. 验证总结：
   - 确定最可能的根本原因
   - 评估整体置信度
   - 评估验证质量
   - 建议后续验证步骤

验证原则：
- 客观公正，基于事实
- 考虑所有可能性
- 承认不确定性
- 提供明确的验证逻辑

{self._build_json_output_instruction(json_schema)}"""
        
        return Task(
            description=description,
            expected_output="包含验证结果、交叉验证、证据分析和更新概率的详细JSON对象",
            agent=agent
        )

class SolutionArchitectureTaskFactory(BaseTaskFactory):
    """解决方案架构任务工厂 - 设计解决方案"""
    
    def create_task(self, agent: Agent, validated_root_cause: Dict[str, Any], context: Dict[str, Any], **kwargs) -> Task:
        self._validate_required_params(['validated_root_cause'], {'validated_root_cause': validated_root_cause})
        
        root_cause_text = str(validated_root_cause)
        context_text = str(context) if context else "无额外上下文"
        
        json_schema = """{
    "immediate_actions": [
        {
            "action": "重启服务",
            "priority": "P0|P1|P2|P3",
            "estimated_time": "5 minutes",
            "risk_level": "High|Medium|Low",
            "required_resources": ["SRE engineer"],
            "dependencies": ["prerequisites"],
            "rollback_plan": "回滚方案",
            "success_criteria": "成功标准"
        }
    ],
    "short_term_solutions": [
        {
            "solution": "增加数据库连接池大小",
            "timeframe": "1-7 days",
            "effort_estimate": "2 person-days",
            "technical_approach": "详细技术方案",
            "testing_strategy": "测试策略",
            "deployment_plan": "部署计划",
            "monitoring_points": ["监控要点"]
        }
    ],
    "long_term_improvements": [
        {
            "improvement": "实施自动扩展机制",
            "timeframe": "1-3 months",
            "business_value": "业务价值",
            "technical_complexity": "High|Medium|Low",
            "cost_estimate": "成本估算",
            "success_metrics": ["成功指标"],
            "milestone_plan": ["里程碑计划"]
        }
    ],
    "prevention_measures": [
        {
            "measure": "加强监控告警",
            "category": "monitoring|process|training|technology",
            "implementation_effort": "effort estimate",
            "effectiveness_rating": "High|Medium|Low",
            "maintenance_requirement": "维护要求"
        }
    ],
    "implementation_roadmap": {
        "phase_1": "immediate_actions",
        "phase_2": "short_term_solutions", 
        "phase_3": "long_term_improvements",
        "critical_path": ["关键路径"],
        "resource_allocation": "资源分配建议"
    },
    "risk_assessment": {
        "implementation_risks": ["实施风险"],
        "mitigation_strategies": ["风险缓解策略"],
        "contingency_plans": ["应急计划"]
    }
}"""
        
        description = f"""基于验证的根本原因设计全面解决方案：

验证的根本原因：
{root_cause_text}

问题上下文：
{context_text}

请设计分层次的解决方案：

1. 即时措施（止损）：
   - 立即可执行的止损措施
   - 设置优先级（P0-P3）
   - 评估执行时间和风险
   - 明确所需资源和依赖
   - 提供回滚计划和成功标准

2. 短期解决方案（修复）：
   - 1-7天内的修复措施
   - 详细的技术实施方案
   - 工作量和时间估算
   - 测试和部署策略
   - 关键监控点

3. 长期改进（预防）：
   - 1-3个月的根本性改进
   - 业务价值和技术复杂度评估
   - 成本效益分析
   - 成功指标和里程碑
   - 长期维护考虑

4. 预防措施：
   - 防止类似问题再次发生
   - 分类：监控/流程/培训/技术
   - 实施难度和有效性评估
   - 维护要求

5. 实施路线图：
   - 分阶段实施计划
   - 关键路径分析
   - 资源分配建议
   - 时间安排

6. 风险评估：
   - 实施过程中的风险
   - 风险缓解策略
   - 应急计划

解决方案设计原则：
- 平衡快速修复和长期稳定
- 考虑技术可行性和业务价值
- 最小化对现有系统的影响
- 提供可衡量的成功标准

{self._build_json_output_instruction(json_schema)}"""
        
        return Task(
            description=description,
            expected_output="包含即时措施、短期方案、长期改进和实施路线图的完整解决方案JSON对象",
            agent=agent
        )

class ComprehensiveReportGenerationTaskFactory(BaseTaskFactory):
    """综合报告生成任务工厂 - 生成最终报告"""
    
    def create_task(self, agent: Agent, all_analysis_results: Dict[str, Any], **kwargs) -> Task:
        self._validate_required_params(['all_analysis_results'], {'all_analysis_results': all_analysis_results})
        
        results_text = str(all_analysis_results)
        
        description = f"""基于所有分析结果生成综合诊断报告：

所有分析结果：
{results_text}

请生成包含以下内容的综合报告：

## 1. 执行摘要
- 问题概述（1-2句话描述核心问题）
- 根本原因（明确的根因结论）
- 影响评估（业务和技术影响）
- 解决方案概要（主要解决措施）
- 时间线总结（关键时间节点）

## 2. 问题分析
### 2.1 输入分类和提取信息
- 输入类型和分类置信度
- 提取的关键信息（Jira号、组件、时间等）

### 2.2 详细分析过程
- 告警分析结果（如适用）
- Jira工单分析结果（如适用）
- 日志分析结果（如适用）
- 时间线重建结果

## 3. 根本原因分析
### 3.1 假设生成和验证
- 考虑的主要假设
- 验证过程和结果
- 最终确认的根本原因

### 3.2 因果关系链条
- 问题发生的完整链条
- 关键触发因素
- 问题扩散路径

## 4. 解决方案
### 4.1 即时措施
- 立即需要执行的止损措施
- 优先级和执行时间

### 4.2 短期修复
- 1周内的修复方案
- 技术实施要点

### 4.3 长期预防
- 长期改进措施
- 预防类似问题的建议

## 5. 实施建议
### 5.1 行动计划
- 分阶段实施步骤
- 责任分工建议
- 时间安排

### 5.2 监控和验证
- 关键监控指标
- 成功验证标准
- 风险监控点

## 6. 经验教训
- 这次事件的主要教训
- 流程改进建议
- 能力建设建议

## 7. 附录
- 详细的技术数据
- 关键日志片段
- 相关文档链接

报告要求：
- 结构清晰，逻辑严密
- 技术准确，易于理解
- 包含具体的行动指导
- 适合不同层级的读者
- 突出关键信息和建议"""
        
        return Task(
            description=description,
            expected_output="结构化的综合诊断报告，包含问题分析、根因、解决方案和实施建议",
            agent=agent
        ) 