#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
优化后的敏感信息检测模块 (sensitive_info_detector.py)
该模块负责分析文本内容，识别其中的敏感信息。
增加了更精确的正则表达式和上下文验证以减少误报。
"""

import re
from collections import defaultdict

class SensitiveInfoDetector:
    """
    敏感信息检测类，负责分析文本内容，识别其中的敏感信息
    """
    
    def __init__(self):
        """
        初始化敏感信息检测器
        """
        # 初始化各类敏感信息的正则表达式模式
        self.patterns = {
            'phone': {
                'name': '手机号码',
                'pattern': r'(?:\+?86)?(?<!\d)1[3-9]\d{9}(?!\d)',  # 中国大陆手机号码，支持可选的+86前缀
                'description': '11位数字，以1开头，第二位是3-9，可能带有+86前缀',
                'validator': self._validate_phone
            },
            'landline': {
                'name': '座机号码',
                'pattern': r'(?<!\d)(?:0\d{2,3}[-\s])?(?:[2-9]\d{6,7})(?!\d)',  # 座机号码，可能带区号
                'description': '区号(可选)+7-8位数字',
                'validator': self._validate_landline
            },
            'id_card': {
                'name': '身份证号',
                'pattern': r'(?<!\d)[1-9]\d{5}(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx](?!\d)',  # 18位身份证
                'description': '18位数字，最后一位可能是X',
                'validator': self._validate_id_card
            },
            'address': {
                'name': '家庭住址',
                'pattern': r'(?:北京|上海|天津|重庆|广州|深圳|杭州|南京|武汉|成都|西安|沈阳|大连|青岛|济南|郑州|长沙|福州|厦门|哈尔滨|长春|太原|石家庄|呼和浩特|南宁|银川|乌鲁木齐|拉萨|西宁|兰州|贵阳|昆明|南昌|合肥|海口|三亚|香港|澳门|台北)(?:市|省|特别行政区)?[\u4e00-\u9fa5]{1,3}(?:区|县|市)[\u4e00-\u9fa5]{2,10}(?:路|街|道|巷|胡同)[\u4e00-\u9fa5\d]{1,10}号?(?:[\u4e00-\u9fa5\d]{1,10}(?:号楼|单元|室|号))?',
                'description': '包含省市区县、路街道等信息的地址',
                'validator': self._validate_address
            },
            'email': {
                'name': '电子邮箱',
                'pattern': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                'description': '标准电子邮箱格式',
                'validator': self._validate_email
            },
            'password': {
                'name': '密码',
                'pattern': r'(?:密码|password|pwd)[：:]\s*([a-zA-Z0-9@#$%^&*]{6,20})',
                'description': '密码标识后跟随的6-20位字符',
                'validator': self._validate_password
            },
            'credit_card': {
                'name': '银行卡号',
                'pattern': r'(?<!\d)(?:\d{4}[\s-]?){3,4}\d{0,4}(?!\d)',
                'description': '16-19位数字，可能有空格分隔',
                'validator': self._validate_credit_card
            },
            'ip_address': {
                'name': 'IP地址',
                'pattern': r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
                'description': '标准IPv4地址格式',
                'validator': self._validate_ip_address
            }
        }
        
        # 默认启用所有类型的敏感信息检测
        self.enabled_types = set(self.patterns.keys())
        
        # 设置最小置信度阈值（0-100）
        self.confidence_threshold = 50  # 降低阈值使检测更宽松
    
    def _validate_phone(self, match, text):
        """验证手机号码"""
        phone = match.group()
        
        # 提取纯数字部分
        digits_only = ''.join(c for c in phone if c.isdigit())
        
        # 如果有国际前缀，去掉前面的86
        if len(digits_only) > 11 and digits_only.startswith('86'):
            digits_only = digits_only[2:]
        
        # 检查是否是有效的手机号码格式
        if not re.match(r'^1[3-9]\d{9}$', digits_only):
            return 0
        
        # 检查上下文是否包含手机号相关词汇
        context = self._get_context_text(text, match.start(), match.end(), 20)
        if re.search(r'(手机|电话|联系|拨打|号码)', context):
            return 100
        
        # 检查是否是常见无效号码
        if digits_only in ['12345678910', '13800138000', '13912345678']:
            return 0
        
        # 基本验证通过
        return 80
    
    def _validate_landline(self, match, text):
        """验证座机号码"""
        landline = match.group()
        
        # 检查是否是有效的座机号码格式
        if not re.match(r'^(?:0\d{2,3}[-\s])?[2-9]\d{6,7}$', landline):
            return 0
        
        # 检查上下文是否包含座机相关词汇
        context = self._get_context_text(text, match.start(), match.end(), 20)
        if re.search(r'(电话|座机|分机|传真|客服)', context):
            return 100
        
        # 基本验证通过
        return 70
    
    def _validate_id_card(self, match, text):
        """验证身份证号"""
        id_card = match.group()
        
        # 检查是否是有效的身份证号格式
        if not re.match(r'^[1-9]\d{5}(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx]$', id_card):
            return 0
        
        # 检查上下文是否包含身份证相关词汇
        context = self._get_context_text(text, match.start(), match.end(), 20)
        if re.search(r'(身份证|证件|号码|身份|证号)', context):
            return 100
        
        # 检查出生日期是否有效
        year = int(id_card[6:10])
        month = int(id_card[10:12])
        day = int(id_card[12:14])
        
        # 简单的日期验证
        if year < 1900 or year > 2100 or month < 1 or month > 12 or day < 1 or day > 31:
            return 0
        
        # 基本验证通过
        return 90
    
    def _validate_address(self, match, text):
        """验证地址"""
        address = match.group()
        
        # 检查上下文是否包含地址相关词汇
        context = self._get_context_text(text, match.start(), match.end(), 20)
        if re.search(r'(地址|住址|家庭|位于|住在)', context):
            return 100
        
        # 检查地址长度
        if len(address) < 10:
            return 0
        
        # 基本验证通过
        return 80
    
    def _validate_email(self, match, text):
        """验证电子邮箱"""
        email = match.group()
        
        # 检查是否是有效的邮箱格式
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return 0
        
        # 检查上下文是否包含邮箱相关词汇
        context = self._get_context_text(text, match.start(), match.end(), 20)
        if re.search(r'(邮箱|邮件|电子邮件|Email|联系)', context):
            return 100
        
        # 检查是否是常见的测试邮箱
        if re.match(r'^(test|example|sample)@', email.lower()):
            return 30
        
        # 基本验证通过
        return 80
    
    def _validate_password(self, match, text):
        """验证密码"""
        # 密码在分组中
        password = match.group(1) if match.groups() else match.group()
        
        # 检查上下文是否明确包含密码相关词汇
        context = self._get_context_text(text, match.start(), match.end(), 20)
        if re.search(r'(密码|口令|password|pwd)', context):
            return 100
        
        # 基本验证通过
        return 90
    
    def _validate_credit_card(self, match, text):
        """验证银行卡号"""
        card = match.group().replace(' ', '').replace('-', '')
        
        # 检查是否是有效的银行卡号格式（16-19位数字）
        if not re.match(r'^\d{16,19}$', card):
            return 0
        
        # 检查上下文是否包含银行卡相关词汇
        context = self._get_context_text(text, match.start(), match.end(), 20)
        if re.search(r'(银行卡|信用卡|储蓄卡|卡号|账号)', context):
            return 100
        
        # 使用Luhn算法验证卡号
        digits = [int(d) for d in card]
        # 从右向左，对奇数位（从0开始）数字乘以2
        for i in range(len(digits)-2, -1, -2):
            digits[i] *= 2
            # 如果乘以2后大于9，则减去9
            # (等同于各位数字之和：例如16的各位数字之和为1+6=7，也等于16-9=7)
            if digits[i] > 9:
                digits[i] -= 9
        
        if sum(digits) % 10 != 0:
            return 0
        
        # 基本验证通过
        return 80
    
    def _validate_ip_address(self, match, text):
        """验证IP地址"""
        ip = match.group()
        
        # 检查是否是有效的IP地址格式
        parts = ip.split('.')
        if len(parts) != 4:
            return 0
        
        for part in parts:
            if not part.isdigit() or int(part) > 255:
                return 0
        
        # 检查上下文是否包含IP相关词汇
        context = self._get_context_text(text, match.start(), match.end(), 20)
        if re.search(r'(IP|地址|服务器|网络|主机)', context):
            return 100
        
        # 检查是否是特殊IP
        if ip in ['127.0.0.1', '0.0.0.0', '255.255.255.255']:
            return 50
        
        # 基本验证通过
        return 70
    
    def _get_context_text(self, text, start, end, context_size=20):
        """
        获取匹配项的上下文文本
        
        参数:
            text (str): 原始文本
            start (int): 匹配项开始位置
            end (int): 匹配项结束位置
            context_size (int): 上下文大小（前后各多少字符）
            
        返回:
            str: 上下文文本
        """
        # 计算上下文的起始和结束位置
        context_start = max(0, start - context_size)
        context_end = min(len(text), end + context_size)
        
        # 提取上下文
        return text[context_start:context_end]
    
    def get_available_info_types(self):
        """
        获取所有可用的敏感信息类型
        
        返回:
            list: 敏感信息类型列表，每项包含类型ID、名称和描述
        """
        return [
            {
                'id': type_id,
                'name': info['name'],
                'description': info['description']
            }
            for type_id, info in self.patterns.items()
        ]
    
    def set_enabled_types(self, type_ids):
        """
        设置要检测的敏感信息类型
        
        参数:
            type_ids (list): 要启用的敏感信息类型ID列表
        """
        # 验证类型ID是否有效
        for type_id in type_ids:
            if type_id not in self.patterns:
                raise ValueError(f"无效的敏感信息类型ID: {type_id}")
        
        self.enabled_types = set(type_ids)
    
    def set_confidence_threshold(self, threshold):
        """
        设置置信度阈值
        
        参数:
            threshold (int): 置信度阈值（0-100）
        """
        if threshold < 0 or threshold > 100:
            raise ValueError("置信度阈值必须在0-100之间")
        
        self.confidence_threshold = threshold
    
    def detect_sensitive_info(self, text, info_types=None):
        """
        检测文本中的敏感信息
        
        参数:
            text (str): 要检测的文本内容
            info_types (list, optional): 要检测的敏感信息类型列表，如果为None则使用已启用的类型
            
        返回:
            dict: 检测结果，格式为 {类型ID: [匹配项列表]}
        """
        if text is None or text.strip() == "":
            return {}
        
        # 如果未指定类型，则使用已启用的类型
        if info_types is None:
            info_types = self.enabled_types
        else:
            # 验证类型ID是否有效
            for type_id in info_types:
                if type_id not in self.patterns:
                    raise ValueError(f"无效的敏感信息类型ID: {type_id}")
        
        results = defaultdict(list)
        
        # 对每种类型进行检测
        for type_id in info_types:
            if type_id not in self.patterns:
                continue
                
            pattern = self.patterns[type_id]['pattern']
            validator = self.patterns[type_id].get('validator')
            
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                # 验证匹配项
                confidence = 100
                if validator:
                    confidence = validator(match, text)
                
                # 如果置信度低于阈值，则跳过
                if confidence < self.confidence_threshold:
                    continue
                
                # 对于密码类型，提取分组中的实际密码
                if type_id == 'password' and match.groups():
                    password = match.group(1)
                    results[type_id].append({
                        'value': password,
                        'start': match.start(1),
                        'end': match.end(1),
                        'context': self._get_context(text, match.start(1), match.end(1)),
                        'confidence': confidence
                    })
                else:
                    results[type_id].append({
                        'value': match.group(),
                        'start': match.start(),
                        'end': match.end(),
                        'context': self._get_context(text, match.start(), match.end()),
                        'confidence': confidence
                    })
        
        return dict(results)
    
    def _get_context(self, text, start, end, context_size=20):
        """
        获取匹配项的上下文
        
        参数:
            text (str): 原始文本
            start (int): 匹配项开始位置
            end (int): 匹配项结束位置
            context_size (int): 上下文大小（前后各多少字符）
            
        返回:
            str: 带有上下文的文本片段
        """
        # 计算上下文的起始和结束位置
        context_start = max(0, start - context_size)
        context_end = min(len(text), end + context_size)
        
        # 提取上下文
        prefix = text[context_start:start]
        match = text[start:end]
        suffix = text[end:context_end]
        
        return f"{prefix}【{match}】{suffix}"
    
    def format_results(self, results):
        """
        格式化检测结果为易读的文本
        
        参数:
            results (dict): 检测结果
            
        返回:
            str: 格式化后的文本
        """
        if not results:
            return "未检测到敏感信息。"
        
        output = []
        output.append("检测到以下敏感信息：\n")
        
        for type_id, matches in results.items():
            if not matches:
                continue
                
            type_name = self.patterns[type_id]['name']
            output.append(f"## {type_name}（{len(matches)}项）")
            
            for i, match in enumerate(matches, 1):
                confidence = match.get('confidence', 100)
                confidence_str = f"置信度: {confidence}%" if confidence < 100 else ""
                
                output.append(f"{i}. 值: {match['value']} {confidence_str}")
                output.append(f"   上下文: {match['context']}")
                output.append("")
        
        return "\n".join(output)


# 测试代码
if __name__ == "__main__":
    detector = SensitiveInfoDetector()
    
    # 测试文本
    test_text = """
    联系方式：张三，手机号码13812345678，座机010-12345678
    家庭住址：北京市海淀区中关村南大街5号，邮编100081
    身份证号：110101199001011234
    电子邮箱：zhangsan@example.com
    银行卡：6222 0000 1111 2222
    登录信息：用户名admin，密码：Admin@123456
    服务器IP：192.168.1.100
    国际手机号：+8618321019580
    """
    
    # 检测所有类型的敏感信息
    results = detector.detect_sensitive_info(test_text)
    
    # 打印格式化结果
    print(detector.format_results(results))
    
    # 测试仅检测特定类型
    print("\n仅检测手机号和身份证：")
    results = detector.detect_sensitive_info(test_text, ['phone', 'id_card'])
    print(detector.format_results(results))
