from crewai import Task, Agent
from typing import Dict, Any
from .base_task_factory import BaseTaskFactory

class JiraIssueBasicInfoExtractionTaskFactory(BaseTaskFactory):
    """Jira工单基础信息提取任务工厂 - 只提取基本信息"""
    
    def create_task(self, agent: Agent, issue_key: str, **kwargs) -> Task:
        self._validate_required_params(['issue_key'], {'issue_key': issue_key})
        
        description = f"""获取Jira工单的基础信息：

Issue Key: {issue_key}

请使用Jira工具获取以下基础信息：
1. 工单标题和描述
2. 当前状态（Open/In Progress/Resolved/Closed等）
3. 优先级（Highest/High/Medium/Low/Lowest）
4. 工单类型（Bug/Task/Story/Epic等）
5. 创建时间和最后更新时间
6. 报告人和当前负责人
7. 关联的项目和组件
8. 当前的修复版本（如果有）

请确保获取的信息完整准确，为后续分析提供可靠的基础数据。

输出格式要求：
- 以JSON格式返回所有提取的信息
- 包含获取时间戳
- 如果某些字段为空，请明确标示为null
- 包含数据获取的状态（成功/失败）"""
        
        return Task(
            description=description,
            expected_output="包含工单完整基础信息的JSON对象，格式规范且易于解析",
            agent=agent
        )

class JiraIssueCategorizationTaskFactory(BaseTaskFactory):
    """Jira工单分类任务工厂 - 只做问题分类"""
    
    def create_task(self, agent: Agent, issue_content: str, **kwargs) -> Task:
        self._validate_required_params(['issue_content'], {'issue_content': issue_content})
        
        json_schema = """{
    "technical_category": "BUG|FEATURE|PERFORMANCE|SECURITY|INFRASTRUCTURE|ENHANCEMENT",
    "business_domain": "PAYMENT|USER_MANAGEMENT|CONTENT|API|DATABASE|UI_UX|INTEGRATION",
    "urgency": "CRITICAL|URGENT|NORMAL|LOW",
    "complexity": {
        "level": "HIGH|MEDIUM|LOW",
        "factors": ["技术复杂度因素"],
        "estimated_effort": "预估工作量"
    },
    "impact_scope": {
        "affected_users": "All|Many|Some|Few",
        "affected_features": ["功能列表"],
        "system_components": ["涉及组件"]
    },
    "classification_confidence": 0.92,
    "reasoning": "详细的分类判断理由"
}"""
        
        description = f"""分析Jira工单的问题类别和特征：

工单内容：
{issue_content}

请从以下维度进行精确分类：

1. 技术类别：
   - BUG: 软件缺陷和错误
   - FEATURE: 新功能需求  
   - PERFORMANCE: 性能优化
   - SECURITY: 安全相关问题
   - INFRASTRUCTURE: 基础设施相关
   - ENHANCEMENT: 功能改进

2. 业务领域：
   - PAYMENT: 支付相关
   - USER_MANAGEMENT: 用户管理
   - CONTENT: 内容管理
   - API: 接口相关
   - DATABASE: 数据库相关
   - UI_UX: 用户界面体验
   - INTEGRATION: 系统集成

3. 紧急程度：
   - CRITICAL: 生产环境严重问题
   - URGENT: 需要优先处理
   - NORMAL: 正常优先级
   - LOW: 可以延后处理

4. 复杂度评估：
   - 技术实现复杂度
   - 影响的复杂度因素
   - 预估的工作量

5. 影响范围：
   - 受影响的用户群体
   - 涉及的功能模块
   - 相关的系统组件

{self._build_json_output_instruction(json_schema)}"""
        
        return Task(
            description=description,
            expected_output="包含技术类别、业务领域、紧急程度、复杂度和影响范围的JSON对象",
            agent=agent
        )

class JiraRelatedComponentsAnalysisTaskFactory(BaseTaskFactory):
    """Jira相关组件分析任务工厂 - 只分析技术组件"""
    
    def create_task(self, agent: Agent, issue_content: str, **kwargs) -> Task:
        self._validate_required_params(['issue_content'], {'issue_content': issue_content})
        
        json_schema = """{
    "services": [
        {
            "name": "user-service",
            "confidence": 0.95,
            "involvement": "primary|secondary|related"
        }
    ],
    "databases": [
        {
            "name": "user_db", 
            "type": "MySQL|PostgreSQL|MongoDB|Redis",
            "operations": ["read", "write", "migration"]
        }
    ],
    "apis": [
        {
            "endpoint": "/api/users/{id}",
            "method": "GET|POST|PUT|DELETE",
            "service": "user-service"
        }
    ],
    "dependencies": [
        {
            "name": "redis",
            "type": "cache|queue|storage",
            "purpose": "用户会话缓存"
        }
    ],
    "infrastructure": [
        {
            "component": "kubernetes",
            "aspect": "deployment|scaling|networking"
        }
    ],
    "log_targets": [
        {
            "application": "user-service-logs",
            "priority": "high|medium|low",
            "search_focus": "authentication errors"
        }
    ],
    "analysis_confidence": 0.88
}"""
        
        description = f"""分析工单涉及的技术组件和系统依赖：

工单内容：
{issue_content}

请识别以下技术组件：

1. 涉及的服务/应用：
   - 从描述中提取服务名称
   - 评估服务的参与程度（主要/次要/相关）
   - 提供识别置信度

2. 相关数据库：
   - 数据库名称和类型
   - 涉及的操作类型（读/写/迁移等）

3. API接口：
   - 具体的API端点路径
   - HTTP方法
   - 所属服务

4. 第三方依赖：
   - 外部服务和组件
   - 依赖类型（缓存/队列/存储等）
   - 用途说明

5. 基础设施组件：
   - 容器、调度器等基础设施
   - 涉及的方面（部署/扩展/网络等）

6. 建议的日志搜索目标：
   - 应该搜索的应用日志
   - 搜索优先级
   - 重点关注的问题类型

{self._build_json_output_instruction(json_schema)}"""
        
        return Task(
            description=description,
            expected_output="包含服务、数据库、API、依赖和日志目标的详细技术组件分析JSON对象",
            agent=agent
        )

class JiraContextEnrichmentTaskFactory(BaseTaskFactory):
    """Jira上下文富化任务工厂 - 收集相关上下文信息"""
    
    def create_task(self, agent: Agent, issue_info: Dict[str, Any], components: Dict[str, Any], **kwargs) -> Task:
        self._validate_required_params(['issue_info', 'components'], {
            'issue_info': issue_info,
            'components': components
        })
        
        issue_text = str(issue_info)
        components_text = str(components)
        
        json_schema = """{
    "related_issues": [
        {
            "issue_key": "PROJ-124",
            "relationship": "blocks|blocked_by|relates_to|duplicates",
            "summary": "相关工单摘要"
        }
    ],
    "historical_context": {
        "similar_issues_count": 3,
        "resolution_patterns": ["常见解决方案"],
        "recurring_problem": true
    },
    "environment_info": {
        "affected_environments": ["production", "staging"],
        "deployment_context": "recent deployment info",
        "configuration_changes": ["recent config changes"]
    },
    "stakeholder_context": {
        "affected_teams": ["backend", "frontend"],
        "key_contacts": ["team leads"],
        "escalation_path": ["escalation contacts"]
    },
    "timeline_context": {
        "created_date": "2024-01-15",
        "last_activity": "2024-01-16", 
        "time_in_current_status": "2 days",
        "deadline_info": "deadline if any"
    },
    "external_references": {
        "documentation": ["related docs"],
        "runbooks": ["related runbooks"],
        "monitoring_dashboards": ["relevant dashboards"]
    }
}"""
        
        description = f"""收集和整理Jira工单的相关上下文信息：

工单基础信息：
{issue_text}

技术组件分析：
{components_text}

请收集以下上下文信息：

1. 关联工单：
   - 查找相关的工单（阻塞、被阻塞、关联、重复等）
   - 分析工单之间的关系

2. 历史上下文：
   - 类似问题的历史记录
   - 常见的解决模式
   - 是否是重复出现的问题

3. 环境信息：
   - 受影响的环境（生产/测试等）
   - 最近的部署信息
   - 配置变更记录

4. 利益相关者：
   - 涉及的团队
   - 关键联系人
   - 升级路径

5. 时间线上下文：
   - 工单创建和活动时间
   - 在当前状态的时长
   - 截止日期信息

6. 外部资源：
   - 相关文档链接
   - 运维手册
   - 监控面板

{self._build_json_output_instruction(json_schema)}"""
        
        return Task(
            description=description,
            expected_output="包含关联工单、历史上下文、环境信息和利益相关者的完整上下文JSON对象",
            agent=agent
        ) 