from crewai_tools import BaseTool
from typing import Type, Optional, Any
from pydantic import BaseModel, Field
import logging

class SearchInput(BaseModel):
    """Input schema for SearchTools"""
    query: str = Field(..., description="搜索查询关键词")
    search_type: str = Field(default="logs", description="搜索类型: logs, metrics, 或 config")
    time_range: str = Field(default="1h", description="时间范围，如 1h, 24h, 7d")

class SearchTools(BaseTool):
    name: str = "search_tool"
    description: str = "搜索日志、指标和配置信息的工具。可以根据关键词查找相关的系统信息。"
    args_schema: Type[BaseModel] = SearchInput

    def _run(self, query: str, search_type: str = "logs", time_range: str = "1h") -> str:
        """
        执行搜索操作
        
        Args:
            query: 搜索关键词
            search_type: 搜索类型 (logs, metrics, config)
            time_range: 时间范围
            
        Returns:
            搜索结果的字符串表示
        """
        try:
            # 模拟搜索功能 - 在实际环境中，这里会连接到真实的监控系统
            if search_type == "logs":
                return self._search_logs(query, time_range)
            elif search_type == "metrics":
                return self._search_metrics(query, time_range)
            elif search_type == "config":
                return self._search_config(query)
            else:
                return f"不支持的搜索类型: {search_type}"
        except Exception as e:
            logging.error(f"搜索工具执行失败: {e}")
            return f"搜索失败: {str(e)}"

    def _search_logs(self, query: str, time_range: str) -> str:
        """搜索日志"""
        # 模拟日志搜索结果
        mock_logs = f"""
=== 日志搜索结果 (关键词: {query}, 时间范围: {time_range}) ===

2024-01-20 10:30:15 [ERROR] 数据库连接超时: Connection timed out after 30 seconds
2024-01-20 10:29:45 [WARN]  连接池使用率过高: 95% usage detected
2024-01-20 10:28:30 [INFO]  尝试重新连接数据库
2024-01-20 10:27:20 [ERROR] 查询执行缓慢: SELECT * FROM users took 45 seconds

=== 总计找到 4 条相关日志 ===
        """
        return mock_logs.strip()

    def _search_metrics(self, query: str, time_range: str) -> str:
        """搜索指标"""
        # 模拟指标搜索结果
        mock_metrics = f"""
=== 指标搜索结果 (关键词: {query}, 时间范围: {time_range}) ===

CPU使用率: 85% (正常范围: 60-70%)
内存使用率: 78% (正常范围: 50-75%)
数据库连接数: 95/100 (警告阈值: 80)
响应时间: 2.5秒 (SLA要求: <1秒)
错误率: 12% (正常水平: <5%)

=== 所有指标均超出正常范围 ===
        """
        return mock_metrics.strip()

    def _search_config(self, query: str) -> str:
        """搜索配置"""
        # 模拟配置搜索结果
        mock_config = f"""
=== 配置搜索结果 (关键词: {query}) ===

数据库配置:
- max_connections: 100
- connection_timeout: 30s
- pool_size: 50
- query_timeout: 60s

应用配置:
- thread_pool_size: 20
- max_memory: 2GB
- gc_threshold: 80%

=== 配置项检查完成 ===
        """
        return mock_config.strip()

# 保持向后兼容
class SearchToolsLegacy:
    """为了兼容现有代码的遗留类"""
    def __init__(self):
        self.tool = SearchTools()
    
    def search(self, query: str, search_type: str = "logs", time_range: str = "1h") -> str:
        return self.tool._run(query, search_type, time_range)
