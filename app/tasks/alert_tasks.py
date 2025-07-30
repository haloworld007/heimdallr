from crewai import Task, Agent
from typing import Dict, Any
from .base_task_factory import BaseTaskFactory

class AlertTriageTaskFactory(BaseTaskFactory):
    """告警分流任务工厂 - 只做严重性和基础分类"""
    
    def create_task(self, agent: Agent, alert_text: str, **kwargs) -> Task:
        self._validate_required_params(['alert_text'], {'alert_text': alert_text})
        
        json_schema = """{
    "severity": "Critical|High|Medium|Low",
    "alert_type": "DATABASE|APPLICATION|NETWORK|INFRASTRUCTURE|SECURITY",
    "urgency_level": "Immediate|High|Normal|Low",
    "reasoning": "详细的判断理由",
    "confidence": 0.95
}"""
        
        description = f"""分析告警的严重性和基础类型：

告警内容：
{alert_text}

请专注分析以下两个核心维度：

1. 严重程度评估：
   - Critical: 系统完全不可用，影响所有用户
   - High: 核心功能受损，影响大部分用户  
   - Medium: 部分功能异常，影响部分用户
   - Low: 轻微问题，几乎不影响用户

2. 告警类型分类：
   - DATABASE: 数据库相关问题
   - APPLICATION: 应用程序相关问题
   - NETWORK: 网络连接相关问题
   - INFRASTRUCTURE: 基础设施相关问题
   - SECURITY: 安全相关问题

3. 紧急程度：
   - Immediate: 需要立即处理
   - High: 1小时内处理
   - Normal: 4小时内处理
   - Low: 24小时内处理

{self._build_json_output_instruction(json_schema)}"""
        
        return Task(
            description=description,
            expected_output="包含严重程度、告警类型、紧急程度和判断理由的JSON对象",
            agent=agent
        )

class AlertComponentIdentificationTaskFactory(BaseTaskFactory):
    """告警组件识别任务工厂 - 只识别影响的系统组件"""
    
    def create_task(self, agent: Agent, alert_text: str, **kwargs) -> Task:
        self._validate_required_params(['alert_text'], {'alert_text': alert_text})
        
        json_schema = """{
    "primary_components": ["service-name", "database-cluster"],
    "secondary_components": ["cache-redis", "message-queue"],
    "affected_systems": ["user-management", "payment-system"],
    "versions_info": {
        "service-name": "v1.2.3",
        "database": "MySQL 8.0"
    },
    "dependency_map": {
        "service-name": ["database", "cache"]
    },
    "confidence_score": 0.88
}"""
        
        description = f"""精确识别告警影响的系统组件：

告警内容：
{alert_text}

请识别以下信息：

1. 主要影响组件：
   - 直接出现问题的组件（服务、数据库、中间件等）
   - 从告警信息中明确提到的组件名称

2. 次要影响组件：
   - 可能受到影响的依赖组件
   - 与主要组件有关联的系统

3. 影响的业务系统：
   - 受影响的业务功能模块
   - 可能涉及的用户流程

4. 版本信息：
   - 如果告警中包含版本号信息

5. 依赖关系映射：
   - 组件之间的依赖关系（如果可以推断）

{self._build_json_output_instruction(json_schema)}"""
        
        return Task(
            description=description,
            expected_output="包含主要组件、次要组件、影响系统和依赖关系的JSON对象",
            agent=agent
        )

class AlertLogSearchParameterGenerationTaskFactory(BaseTaskFactory):
    """告警日志搜索参数生成任务工厂 - 只生成搜索参数"""
    
    def create_task(self, agent: Agent, alert_info: str, components: Dict[str, Any], **kwargs) -> Task:
        self._validate_required_params(['alert_info', 'components'], {
            'alert_info': alert_info, 
            'components': components
        })
        
        components_text = str(components)
        
        json_schema = """{
    "applications": ["app1", "app2"],
    "search_queries": [
        {
            "query": "ERROR",
            "priority": "high",
            "description": "查找错误日志"
        },
        {
            "query": "timeout",
            "priority": "medium", 
            "description": "查找超时相关日志"
        }
    ],
    "time_range": "30m",
    "search_strategy": {
        "primary_search": "最重要的搜索",
        "secondary_search": "补充搜索"
    },
    "expected_patterns": ["异常模式", "错误代码"]
}"""
        
        description = f"""基于告警信息和组件分析生成精确的日志搜索参数：

告警信息：
{alert_info}

组件分析结果：
{components_text}

请生成优化的日志搜索策略：

1. 应用列表：
   - 根据组件信息确定需要搜索的应用名称
   - 优先搜索主要影响组件的日志

2. 搜索查询：
   - 设计有效的搜索关键词
   - 包含错误码、异常类型、函数名等
   - 为每个查询设置优先级和描述

3. 时间范围：
   - 基于告警发生时间推算合适的搜索范围
   - 考虑问题可能的发生和发展时间

4. 搜索策略：
   - 主要搜索：最重要的搜索目标
   - 次要搜索：补充和验证搜索

5. 预期模式：
   - 预测可能在日志中找到的错误模式

{self._build_json_output_instruction(json_schema)}"""
        
        return Task(
            description=description,
            expected_output="包含应用列表、搜索查询、时间范围和搜索策略的JSON对象",
            agent=agent
        )

class AlertBusinessImpactAssessmentTaskFactory(BaseTaskFactory):
    """告警业务影响评估任务工厂 - 只评估业务影响"""
    
    def create_task(self, agent: Agent, alert_text: str, components: Dict[str, Any], **kwargs) -> Task:
        self._validate_required_params(['alert_text', 'components'], {
            'alert_text': alert_text,
            'components': components
        })
        
        components_text = str(components)
        
        json_schema = """{
    "user_impact": {
        "level": "High|Medium|Low",
        "affected_functions": ["登录", "支付", "数据查询"],
        "user_count_estimate": "预估影响用户数"
    },
    "service_availability": {
        "status": "Down|Degraded|Normal",
        "availability_percentage": 85,
        "affected_endpoints": ["/api/users", "/api/payments"]
    },
    "data_risk": {
        "level": "High|Medium|Low",
        "risk_types": ["数据丢失", "数据泄露", "数据不一致"],
        "affected_data_types": ["用户数据", "交易数据"]
    },
    "financial_impact": {
        "level": "High|Medium|Low",
        "revenue_impact": "是否影响收入",
        "cost_estimate": "预估损失"
    },
    "recovery_urgency": "Critical|High|Medium|Low",
    "stakeholder_notification": ["technical_team", "management", "customers"]
}"""
        
        description = f"""评估告警对业务的全面影响：

告警内容：
{alert_text}

组件信息：
{components_text}

请从以下维度评估业务影响：

1. 用户影响：
   - 影响程度（High/Medium/Low）
   - 受影响的功能列表
   - 预估影响的用户数量

2. 服务可用性：
   - 服务状态（完全不可用/性能下降/正常）
   - 可用性百分比
   - 受影响的API端点

3. 数据风险：
   - 数据安全风险等级
   - 具体风险类型
   - 涉及的数据类型

4. 财务影响：
   - 对收入的影响程度
   - 是否直接影响付费功能
   - 预估的损失程度

5. 恢复紧急性：
   - 问题恢复的紧急程度

6. 利益相关者通知：
   - 需要通知哪些团队或人员

{self._build_json_output_instruction(json_schema)}"""
        
        return Task(
            description=description,
            expected_output="包含用户影响、服务可用性、数据风险和财务影响评估的JSON对象",
            agent=agent
        ) 