import logging
import re
import json
from typing import Dict, Any, List, Optional
from crewai import Agent, Task, Crew, Process

from .flow_state import InputType, ClassificationResult
from .agents import ClassificationAgents
from .tasks import TaskRegistry

logger = logging.getLogger(__name__)

class ClassificationEngine:
    """高级输入分类引擎 - 整合规则和AI分类"""
    
    def __init__(self, llm):
        self.llm = llm
        self.rule_classifier = RuleBasedClassifier()
        self.ai_classifier = AIBasedClassifier(llm)
        
    def classify(self, input_text: str) -> ClassificationResult:
        """执行完整的输入分类流程"""
        logger.info(f"开始分类输入文本，长度: {len(input_text)}")
        
        try:
            # 1. 规则分类 - 快速初步判断
            rule_result = self.rule_classifier.classify(input_text)
            logger.debug(f"规则分类结果: {rule_result.input_type.value}, 置信度: {rule_result.confidence}")
            
            # 2. 如果规则分类置信度高，直接返回
            if rule_result.confidence >= 0.85:
                logger.info(f"规则分类置信度足够高 ({rule_result.confidence:.2f})，直接使用结果")
                return rule_result
            
            # 3. 置信度不够高，使用AI增强分类
            ai_result = self.ai_classifier.classify(input_text, rule_result)
            logger.info(f"AI增强分类结果: {ai_result.input_type.value}, 置信度: {ai_result.confidence}")
            
            return ai_result
            
        except Exception as e:
            logger.error(f"分类过程出错: {e}", exc_info=True)
            # 返回默认分类结果
            return ClassificationResult(
                input_type=InputType.UNKNOWN,
                confidence=0.1,
                extracted_data={},
                reasoning=f"分类失败: {str(e)}"
            )

class RuleBasedClassifier:
    """基于规则的快速分类器"""
    
    def __init__(self):
        # Jira Issue Key 正则模式
        self.jira_pattern = re.compile(r'\b([A-Z][A-Z0-9_]*-\d+)\b')
        
        # 告警关键词 - 扩展和优化
        self.alert_keywords = {
            'error_terms': ['error', 'exception', 'fail', 'timeout', 'crash', 'down'],
            'chinese_error_terms': ['错误', '异常', '失败', '超时', '崩溃', '宕机'],
            'severity_terms': ['critical', 'urgent', 'severe', 'warning', 'alert'],
            'chinese_severity_terms': ['严重', '紧急', '告警', '警告', '关键'],
            'system_terms': ['cpu', 'memory', 'disk', 'network', 'database', 'service'],
            'chinese_system_terms': ['内存', '磁盘', '数据库', '服务', '网络', '系统'],
        }
        
        # 日志查询关键词
        self.log_keywords = {
            'log_terms': ['log', 'logs', 'search', 'query', 'grep', 'tail', 'find'],
            'chinese_log_terms': ['日志', '查询', '搜索', '查找'],
            'app_terms': ['application', 'app', 'service', 'system'],
            'chinese_app_terms': ['应用', '应用程序', '服务', '系统'],
        }
        
        # 混合类型指示词
        self.hybrid_indicators = [
            'check', 'investigate', 'analyze', 'debug', 'troubleshoot',
            '检查', '调查', '分析', '调试', '排查'
        ]
    
    def classify(self, input_text: str) -> ClassificationResult:
        """执行规则分类"""
        text_lower = input_text.lower()
        
        # 检测Jira Issue Key
        jira_matches = self.jira_pattern.findall(input_text)
        has_jira = len(jira_matches) > 0
        
        # 计算各类型的匹配分数
        alert_score = self._calculate_alert_score(text_lower)
        log_score = self._calculate_log_score(text_lower)
        hybrid_score = self._calculate_hybrid_score(text_lower)
        
        # 基于匹配情况进行分类决策
        if has_jira and (alert_score > 0.2 or log_score > 0.2 or hybrid_score > 0.3):
            # 混合类型：包含 Jira Issue 且有其他类型特征
            return ClassificationResult(
                input_type=InputType.HYBRID,
                confidence=min(0.9, 0.7 + (alert_score + log_score + hybrid_score) / 3),
                extracted_data={
                    'jira_issues': jira_matches,
                    'alert_score': alert_score,
                    'log_score': log_score,
                    'hybrid_score': hybrid_score,
                    'has_alert_context': alert_score > 0.2,
                    'has_log_context': log_score > 0.2
                },
                reasoning="检测到Jira Issue Key且包含其他诊断类型特征"
            )
        
        elif has_jira:
            # 纯 Jira Issue 分析
            return ClassificationResult(
                input_type=InputType.JIRA_ISSUE,
                confidence=0.95,
                extracted_data={
                    'jira_issues': jira_matches,
                    'primary_issue': jira_matches[0] if jira_matches else None
                },
                reasoning="检测到Jira Issue Key格式，无其他明显类型特征"
            )
        
        elif alert_score > log_score and alert_score > 0.3:
            # 告警类型
            return ClassificationResult(
                input_type=InputType.ALERT,
                confidence=min(0.9, alert_score),
                extracted_data={
                    'alert_score': alert_score,
                    'matched_keywords': self._get_matched_alert_keywords(text_lower)
                },
                reasoning=f"告警关键词匹配分数: {alert_score:.2f}"
            )
        
        elif log_score > 0.3:
            # 日志查询类型
            return ClassificationResult(
                input_type=InputType.LOG_QUERY,
                confidence=min(0.9, log_score),
                extracted_data={
                    'log_score': log_score,
                    'matched_keywords': self._get_matched_log_keywords(text_lower)
                },
                reasoning=f"日志查询关键词匹配分数: {log_score:.2f}"
            )
        
        else:
            # 未知类型
            return ClassificationResult(
                input_type=InputType.UNKNOWN,
                confidence=0.4,
                extracted_data={
                    'alert_score': alert_score,
                    'log_score': log_score,
                    'text_length': len(input_text)
                },
                reasoning="无明确的类型特征匹配"
            )
    
    def _calculate_alert_score(self, text: str) -> float:
        """计算告警匹配分数"""
        total_keywords = 0
        matched_keywords = 0
        
        for category, keywords in self.alert_keywords.items():
            total_keywords += len(keywords)
            matched_keywords += sum(1 for kw in keywords if kw in text)
        
        # 基础分数
        base_score = matched_keywords / total_keywords if total_keywords > 0 else 0
        
        # 权重调整：错误和严重性词汇权重更高
        weight_bonus = 0
        critical_terms = self.alert_keywords['error_terms'] + self.alert_keywords['chinese_error_terms']
        critical_matches = sum(1 for term in critical_terms if term in text)
        weight_bonus += critical_matches * 0.1
        
        return min(1.0, base_score + weight_bonus)
    
    def _calculate_log_score(self, text: str) -> float:
        """计算日志查询匹配分数"""
        total_keywords = 0
        matched_keywords = 0
        
        for category, keywords in self.log_keywords.items():
            total_keywords += len(keywords)
            matched_keywords += sum(1 for kw in keywords if kw in text)
        
        base_score = matched_keywords / total_keywords if total_keywords > 0 else 0
        
        # 明确的日志操作词汇加权
        explicit_log_ops = ['search', 'query', 'grep', 'tail', '搜索', '查询']
        explicit_matches = sum(1 for op in explicit_log_ops if op in text)
        weight_bonus = explicit_matches * 0.15
        
        return min(1.0, base_score + weight_bonus)
    
    def _calculate_hybrid_score(self, text: str) -> float:
        """计算混合类型指示分数"""
        hybrid_matches = sum(1 for indicator in self.hybrid_indicators if indicator in text)
        return min(1.0, hybrid_matches / len(self.hybrid_indicators))
    
    def _get_matched_alert_keywords(self, text: str) -> List[str]:
        """获取匹配的告警关键词"""
        matched = []
        for category, keywords in self.alert_keywords.items():
            matched.extend([kw for kw in keywords if kw in text])
        return matched
    
    def _get_matched_log_keywords(self, text: str) -> List[str]:
        """获取匹配的日志关键词"""
        matched = []
        for category, keywords in self.log_keywords.items():
            matched.extend([kw for kw in keywords if kw in text])
        return matched

class AIBasedClassifier:
    """基于AI的智能分类器"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def classify(self, input_text: str, rule_result: ClassificationResult) -> ClassificationResult:
        """使用AI进行增强分类"""
        logger.info("执行AI增强分类...")
        
        try:
            # 创建分类专家agent
            classifier_agent = ClassificationAgents.input_classifier_agent(self.llm)
            
            # 创建分类任务
            classification_task = TaskRegistry.create_task(
                'input_classification',
                agent=classifier_agent,
                input_text=input_text
            )
            
            # 创建crew执行分类
            crew = Crew(
                agents=[classifier_agent],
                tasks=[classification_task],
                process=Process.sequential,
                verbose=False
            )
            
            # 执行分类
            result = crew.kickoff()
            
            # 解析AI返回的结果
            ai_result = self._parse_ai_result(result.raw, rule_result)
            
            return ai_result
            
        except Exception as e:
            logger.warning(f"AI分类失败: {e}")
            # 使用规则分类结果作为fallback
            return rule_result
    
    def _parse_ai_result(self, ai_output: str, rule_result: ClassificationResult) -> ClassificationResult:
        """解析AI分类结果"""
        try:
            # 尝试解析JSON格式的AI输出
            if '{' in ai_output and '}' in ai_output:
                # 提取JSON部分
                start_idx = ai_output.find('{')
                end_idx = ai_output.rfind('}') + 1
                json_str = ai_output[start_idx:end_idx]
                
                ai_data = json.loads(json_str)
                
                # 验证和映射输入类型
                input_type_str = ai_data.get('input_type', 'unknown').lower()
                input_type_map = {
                    'alert': InputType.ALERT,
                    'jira_issue': InputType.JIRA_ISSUE,
                    'log_query': InputType.LOG_QUERY,
                    'hybrid': InputType.HYBRID,
                    'unknown': InputType.UNKNOWN
                }
                
                input_type = input_type_map.get(input_type_str, InputType.UNKNOWN)
                confidence = min(1.0, max(0.0, ai_data.get('confidence', 0.5)))
                
                # 合并规则分类和AI分类的提取数据
                combined_extracted_data = rule_result.extracted_data.copy()
                combined_extracted_data.update(ai_data.get('extracted_data', {}))
                
                return ClassificationResult(
                    input_type=input_type,
                    confidence=confidence,
                    extracted_data=combined_extracted_data,
                    reasoning=f"AI分类: {ai_data.get('reasoning', 'AI增强分类结果')}"
                )
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"AI结果解析失败: {e}")
        
        # 解析失败，返回规则分类结果但稍微提高置信度
        return ClassificationResult(
            input_type=rule_result.input_type,
            confidence=min(0.8, rule_result.confidence + 0.1),
            extracted_data=rule_result.extracted_data,
            reasoning=f"{rule_result.reasoning} (AI增强处理)"
        )

class PatternExtractor:
    """模式提取器 - 从输入中提取关键信息"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def extract_patterns(self, input_text: str, classification_result: ClassificationResult) -> Dict[str, Any]:
        """提取输入文本中的关键模式"""
        logger.info("执行模式提取...")
        
        try:
            # 创建模式提取agent
            extractor_agent = ClassificationAgents.pattern_extraction_agent(self.llm)
            
            # 根据分类结果确定提取目标
            target_patterns = self._determine_target_patterns(classification_result.input_type)
            
            # 创建模式提取任务
            extraction_task = TaskRegistry.create_task(
                'pattern_extraction',
                agent=extractor_agent,
                input_text=input_text,
                target_patterns=target_patterns
            )
            
            # 执行提取
            crew = Crew(
                agents=[extractor_agent],
                tasks=[extraction_task],
                process=Process.sequential,
                verbose=False
            )
            
            result = crew.kickoff()
            
            # 解析提取结果
            return self._parse_extraction_result(result.raw)
            
        except Exception as e:
            logger.warning(f"模式提取失败: {e}")
            return {}
    
    def _determine_target_patterns(self, input_type: InputType) -> List[str]:
        """根据输入类型确定提取目标"""
        base_patterns = ['jira_issues', 'timestamps', 'ip_addresses']
        
        if input_type == InputType.ALERT:
            return base_patterns + ['error_codes', 'service_names', 'severity_indicators']
        elif input_type == InputType.JIRA_ISSUE:
            return base_patterns + ['component_names', 'version_numbers']
        elif input_type == InputType.LOG_QUERY:
            return base_patterns + ['application_names', 'log_levels']
        elif input_type == InputType.HYBRID:
            return base_patterns + ['error_codes', 'service_names', 'application_names']
        else:
            return base_patterns
    
    def _parse_extraction_result(self, extraction_output: str) -> Dict[str, Any]:
        """解析模式提取结果"""
        try:
            if '{' in extraction_output and '}' in extraction_output:
                start_idx = extraction_output.find('{')
                end_idx = extraction_output.rfind('}') + 1
                json_str = extraction_output[start_idx:end_idx]
                
                return json.loads(json_str)
        except Exception as e:
            logger.warning(f"提取结果解析失败: {e}")
        
        return {} 