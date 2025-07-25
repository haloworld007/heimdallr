
from crewai import Task

class TriageTask(Task):
    def __init__(self, agent, issue):
        super().__init__(
            description=f'分析以下告警信息，并以JSON格式输出其严重性(severity)，类型(type)和影响的组件(component_name):\n\n---告警信息---\n{issue}\n---\n\n你的最终输出必须是一个JSON对象。',
            expected_output='一个包含`severity`, `type`, 和 `component_name`字段的JSON对象。',
            agent=agent
        )

