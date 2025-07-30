from crewai import Task, Agent
from typing import List, Dict, Any
from .base_task_factory import BaseTaskFactory

class LogSearchExecutionTaskFactory(BaseTaskFactory):
    """日志搜索执行任务工厂 - 只执行搜索"""
    
    def create_task(self, agent: Agent, applications: List[str], query: str, 
                   time_range: str = "1h", **kwargs) -> Task:
        self._validate_required_params(['applications', 'query'], {
            'applications': applications,
            'query': query
        })
        
        applications_str = ", ".join(applications)
        
        description = f"""执行日志搜索任务：

搜索参数：
- 应用列表: {applications_str}
- 搜索查询: {query}
- 时间范围: {time_range}

请使用日志搜索工具执行以下操作：

1. 执行日志搜索：
   - 在指定应用中搜索相关日志
   - 使用提供的查询参数
   - 限制在指定的时间范围内

2. 收集搜索结果：
   - 记录搜索命中的总数量
   - 获取代表性的日志条目（最多10-20条）
   - 记录搜索执行状态

3. 初步数据整理：
   - 按时间排序日志条目
   - 标记特别重要的日志
   - 记录搜索性能信息

注意：
- 只执行搜索和数据收集，不进行深度分析
- 确保返回的日志条目完整且格式正确
- 如果搜索失败，请详细记录失败原因

输出格式：
请返回原始搜索结果，包含：
- 搜索状态（成功/失败/超时）
- 命中数量
- 日志条目列表
- 搜索执行时间
- 任何错误信息"""
        
        return Task(
            description=description,
            expected_output="包含搜索状态、命中数量和日志条目的原始搜索结果",
            agent=agent
        )

class LogPatternAnalysisTaskFactory(BaseTaskFactory):
    """日志模式分析任务工厂 - 只做模式分析"""
    
    def create_task(self, agent: Agent, log_entries: str, **kwargs) -> Task:
        self._validate_required_params(['log_entries'], {'log_entries': log_entries})
        
        json_schema = """{
    "error_patterns": [
        {
            "pattern": "TimeoutException",
            "count": 15,
            "frequency": "high|medium|low",
            "sample_entries": ["日志样例"],
            "first_occurrence": "14:20:00",
            "last_occurrence": "14:35:00"
        }
    ],
    "time_distribution": {
        "pattern": "concentrated|scattered|periodic",
        "peak_times": ["14:20-14:25", "14:30-14:35"],
        "description": "时间分布描述"
    },
    "severity_distribution": {
        "ERROR": 25,
        "WARN": 10,
        "INFO": 5
    },
    "correlation_analysis": [
        {
            "correlated_patterns": ["error1", "error2"],
            "correlation_strength": "strong|medium|weak",
            "time_gap": "2 seconds",
            "description": "关联描述"
        }
    ],
    "anomaly_indicators": {
        "unusual_frequency": ["pattern with unusual frequency"],
        "new_patterns": ["previously unseen patterns"],
        "pattern_changes": ["patterns that changed behavior"]
    },
    "analysis_summary": "模式分析的总结"
}"""
        
        description = f"""深入分析日志条目中的模式和趋势：

日志条目：
{log_entries}

请进行以下维度的模式分析：

1. 错误模式识别：
   - 重复出现的错误类型
   - 每种错误的出现次数
   - 错误频率分类（高频/中频/低频）
   - 错误的首次和最后出现时间
   - 代表性的日志样例

2. 时间分布模式：
   - 错误发生的时间分布特征
   - 是否有明显的高峰时段
   - 时间模式的类型（集中型/分散型/周期性）

3. 严重性分布：
   - 不同日志级别的数量统计
   - ERROR、WARN、INFO等的分布情况

4. 关联性分析：
   - 识别同时出现的错误模式
   - 分析错误之间的时间关联
   - 评估关联强度

5. 异常指标：
   - 频率异常的模式
   - 新出现的错误模式
   - 行为发生变化的模式

{self._build_json_output_instruction(json_schema)}"""
        
        return Task(
            description=description,
            expected_output="包含错误模式、时间分布、关联分析和异常指标的详细JSON对象",
            agent=agent
        )

class LogAnomalyDetectionTaskFactory(BaseTaskFactory):
    """日志异常检测任务工厂 - 专门检测异常"""
    
    def create_task(self, agent: Agent, log_entries: str, baseline_info: Dict[str, Any] = None, **kwargs) -> Task:
        self._validate_required_params(['log_entries'], {'log_entries': log_entries})
        
        baseline_context = ""
        if baseline_info:
            baseline_context = f"\n基线信息：\n{str(baseline_info)}\n"
        
        json_schema = """{
    "anomalies_detected": [
        {
            "type": "frequency_anomaly|pattern_anomaly|timing_anomaly|content_anomaly",
            "description": "异常描述",
            "severity": "High|Medium|Low",
            "evidence": ["支持证据"],
            "affected_timeframe": "14:20-14:25",
            "confidence": 0.85
        }
    ],
    "frequency_analysis": {
        "normal_patterns": ["正常频率的模式"],
        "high_frequency_patterns": ["异常高频的模式"],
        "low_frequency_patterns": ["异常低频的模式"],
        "missing_patterns": ["预期但缺失的模式"]
    },
    "content_anomalies": {
        "unusual_error_messages": ["异常的错误信息"],
        "new_error_types": ["新出现的错误类型"],
        "malformed_entries": ["格式异常的日志"]
    },
    "timing_anomalies": {
        "burst_events": ["突发事件时间段"],
        "unusual_quiet_periods": ["异常安静时段"],
        "irregular_intervals": ["不规律间隔"]
    },
    "risk_assessment": {
        "overall_risk": "High|Medium|Low",
        "potential_impacts": ["可能的影响"],
        "investigation_priority": "Immediate|High|Medium|Low"
    }
}"""
        
        description = f"""检测日志中的异常情况和可疑模式：

日志条目：
{log_entries}{baseline_context}

请进行异常检测分析：

1. 异常类型检测：
   - 频率异常：错误出现频率异常高或低
   - 模式异常：新的错误模式或模式变化
   - 时间异常：错误发生时间的异常
   - 内容异常：日志内容的异常

2. 频率分析：
   - 识别正常频率的模式
   - 发现异常高频的错误
   - 注意异常低频或缺失的预期模式

3. 内容异常：
   - 不寻常的错误信息
   - 新出现的错误类型
   - 格式异常的日志条目

4. 时间异常：
   - 错误突发的时间段
   - 异常安静的时段
   - 不规律的发生间隔

5. 风险评估：
   - 整体异常风险等级
   - 可能的业务影响
   - 调查优先级建议

{self._build_json_output_instruction(json_schema)}"""
        
        return Task(
            description=description,
            expected_output="包含异常检测结果、频率分析、内容异常和风险评估的JSON对象",
            agent=agent
        )

class LogCorrelationAnalysisTaskFactory(BaseTaskFactory):
    """日志关联分析任务工厂 - 分析日志关联性"""
    
    def create_task(self, agent: Agent, log_entries: str, multiple_sources: bool = False, **kwargs) -> Task:
        self._validate_required_params(['log_entries'], {'log_entries': log_entries})
        
        analysis_scope = "跨服务关联分析" if multiple_sources else "单一来源关联分析"
        
        json_schema = """{
    "correlation_chains": [
        {
            "chain_id": "chain_001",
            "events": [
                {
                    "timestamp": "14:20:30",
                    "source": "user-service",
                    "event": "authentication_failed",
                    "details": "用户登录失败"
                },
                {
                    "timestamp": "14:20:32", 
                    "source": "auth-service",
                    "event": "token_validation_error",
                    "details": "令牌验证错误"
                }
            ],
            "chain_type": "causal|temporal|functional",
            "confidence": 0.92
        }
    ],
    "request_traces": [
        {
            "trace_id": "trace_123",
            "services_involved": ["user-service", "auth-service", "db"],
            "total_duration": "2.5s",
            "error_points": ["auth failure at user-service"],
            "propagation_path": ["user-service -> auth-service -> database"]
        }
    ],
    "temporal_correlations": {
        "simultaneous_events": ["同时发生的事件"],
        "sequence_patterns": ["事件序列模式"],
        "cascade_failures": ["级联失败模式"]
    },
    "cross_service_impacts": {
        "initiating_service": "问题发起服务",
        "affected_services": ["受影响的服务"],
        "impact_propagation": "影响传播路径",
        "isolation_points": ["隔离点"]
    },
    "correlation_summary": "关联分析总结"
}"""
        
        description = f"""分析不同日志之间的关联关系：

日志条目：
{log_entries}

分析范围：{analysis_scope}

请进行以下关联分析：

1. 关联链条构建：
   - 识别相关的事件序列
   - 构建事件之间的因果关系
   - 分析事件的时间关联性
   - 评估关联的置信度

2. 请求链路追踪：
   - 识别完整的请求链路
   - 跟踪请求在各服务间的传播
   - 定位错误发生的节点
   - 计算请求总耗时

3. 时间关联模式：
   - 同时发生的事件
   - 固定序列的事件模式
   - 级联失败的模式

4. 跨服务影响分析：
   - 识别问题的发起服务
   - 分析影响的传播路径
   - 找到可能的隔离点
   - 评估服务间的依赖关系

5. 根因线索提取：
   - 基于关联分析提供根因线索
   - 识别最可能的问题起点
   - 分析问题扩散的原因

{self._build_json_output_instruction(json_schema)}"""
        
        return Task(
            description=description,
            expected_output="包含关联链条、请求追踪、时间关联和跨服务影响的详细JSON对象",
            agent=agent
        ) 