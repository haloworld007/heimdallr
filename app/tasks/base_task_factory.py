from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from crewai import Task, Agent

class BaseTaskFactory(ABC):
    """Task工厂基类 - 定义task创建的统一接口"""
    
    @abstractmethod
    def create_task(self, agent: Agent, **kwargs) -> Task:
        """创建具体的任务"""
        pass
    
    def _format_description(self, template: str, **kwargs) -> str:
        """格式化任务描述"""
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required parameter for task description: {e}")
    
    def _validate_required_params(self, required_params: list, provided_params: dict):
        """验证必要参数是否提供"""
        missing_params = [param for param in required_params if param not in provided_params]
        if missing_params:
            raise ValueError(f"Missing required parameters: {missing_params}")
    
    def _build_json_output_instruction(self, schema_description: str) -> str:
        """构建JSON输出格式指令"""
        return f"""
请严格按照以下JSON格式输出结果：

{schema_description}

要求：
1. 输出必须是有效的JSON格式
2. 所有字段都必须包含
3. 不要添加任何额外的文本解释
4. 确保JSON格式正确，可以被解析
"""
    
    def _build_context_section(self, context_data: Dict[str, Any]) -> str:
        """构建上下文信息部分"""
        if not context_data:
            return ""
        
        context_lines = ["上下文信息："]
        for key, value in context_data.items():
            context_lines.append(f"- {key}: {value}")
        
        return "\n".join(context_lines) + "\n" 