#!/usr/bin/env python3
"""
CSO Output Format Validator

验证 CSO 情报报告输出是否符合标准格式：
- 数据编码格式 [D-P-RT/AR-S/A/B/C-XXXX]
- 必需章节（Header, P-Prompt, Output, Source Index, Alignment Audit）
- 禁止格式（Markdown 代码块、Markdown 表格）
- 结构完整性

用法:
    python validate_output.py <output-file>

退出码:
    0 - 验证通过
    1 - 验证失败
"""
import re
import sys
from pathlib import Path
from typing import List, Tuple


class CSO_Validator:
    """CSO 输出格式验证器"""

    def __init__(self, content: str):
        self.content = content
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate(self) -> bool:
        """
        执行所有验证规则

        Returns:
            True if all validations pass, False otherwise
        """
        self._validate_header()
        self._validate_pprompt()
        self._validate_data_encoding()
        self._validate_recon_level()
        self._validate_source_index()
        self._validate_alignment_audit()
        self._validate_forbidden_formats()

        return len(self.errors) == 0

    def _validate_header(self):
        """验证 Header 章节"""
        required_patterns = [
            (r'致：P\s*\(Analyst\)', "Missing header: '致：P (Analyst)'"),
            (r'发件人：CSO', "Missing header: '发件人：CSO'"),
            (r'主题：', "Missing header: '主题：'"),
            (r'提案编号：\d{8}-CSO-RAW-\d+', "Invalid proposal ID format. Expected: YYYYMMDD-CSO-RAW-XXX"),
            (r'状态：.*侦察.*RAW', "Missing or invalid status. Expected: [侦察中(RAW)]"),
        ]

        for pattern, error_msg in required_patterns:
            if not re.search(pattern, self.content):
                self.errors.append(f"[HEADER] {error_msg}")

    def _validate_pprompt(self):
        """验证 P-Prompt 五模块结构"""
        required_sections = [
            ('时间锚点：', '[P-PROMPT] Missing section: 时间锚点'),
            ('Role:', '[P-PROMPT] Missing section: Role'),
            ('Mission:', '[P-PROMPT] Missing section: Mission'),
            ('Target_Data:', '[P-PROMPT] Missing section: Target_Data'),
            ('recon_level:', '[P-PROMPT] Missing section: recon_level'),
        ]

        for section, error_msg in required_sections:
            if section not in self.content:
                self.errors.append(error_msg)

        # 验证 Target_Data 格式
        target_data_pattern = r'--\d+、.*?\|\s*时间窗:\s*\[.*?\]\s*\|\s*置信度门槛:\s*[SABC]级'
        if 'Target_Data:' in self.content and not re.search(target_data_pattern, self.content):
            self.errors.append("[P-PROMPT] Invalid Target_Data format. Expected: --N、[描述] | 时间窗: [XX-XX] | 置信度门槛: [S/A/B/C]级")

    def _validate_data_encoding(self):
        """验证数据编码格式 [D-P-RT/AR-S/A/B/C-XXXX]"""
        # 查找所有数据编码
        data_encoding_pattern = r'\[D-P-(RT|AR)-(S|A|B|C|D)-(\d{4})\]'
        matches = re.findall(data_encoding_pattern, self.content)

        if not matches:
            self.errors.append("[DATA-ENCODING] No valid data encoding found. Expected format: [D-P-RT/AR-S/A/B/C-XXXX]")
            return

        # 验证序号唯一性
        sequence_numbers = [match[2] for match in matches]
        duplicates = [num for num in sequence_numbers if sequence_numbers.count(num) > 1]
        if duplicates:
            self.errors.append(f"[DATA-ENCODING] Duplicate sequence numbers found: {set(duplicates)}")

        # 检查是否使用了 D 级（逻辑毒素，应触发熔断）
        d_grade_matches = [m for m in matches if m[1] == 'D']
        if d_grade_matches:
            self.warnings.append("[DATA-ENCODING] Warning: D-grade data detected (逻辑毒素). This should trigger logical circuit breaker.")

    def _validate_recon_level(self):
        """验证 recon_level 格式"""
        recon_pattern = r'recon_level:\s*(L1|L2|L3)'
        match = re.search(recon_pattern, self.content)

        if not match:
            self.errors.append("[RECON-LEVEL] Invalid or missing recon_level. Must be L1, L2, or L3")
        elif match:
            level = match.group(1)
            # 可选：添加 recon_level 与数据源一致性检查
            if level == 'L1' and ('社交媒体' in self.content or 'Twitter' in self.content):
                self.warnings.append(f"[RECON-LEVEL] Warning: L1 (official only) but content mentions social media sources")

    def _validate_source_index(self):
        """验证信源指纹索引库"""
        if '信源指纹索引库' not in self.content and 'Source Fingerprint Index' not in self.content:
            self.errors.append("[SOURCE-INDEX] Missing section: 信源指纹索引库 (Source Fingerprint Index)")
            return

        # 查找锚点格式: -锚点A | ... | ... | MD5:xxx
        anchor_pattern = r'-锚点[A-Z]\s*\|.*?\|.*?\|.*?MD5:'
        matches = re.findall(anchor_pattern, self.content)

        if not matches:
            self.errors.append("[SOURCE-INDEX] No valid source anchors found. Expected format: -锚点A | [来源] | URL | MD5:xxx")

        # 验证所有锚点都被引用
        anchor_refs = re.findall(r'-锚点([A-Z])', self.content)
        anchor_usages = re.findall(r'Ref:.*?锚点([A-Z])', self.content)

        unreferenced = set(anchor_refs) - set(anchor_usages)
        if unreferenced:
            self.warnings.append(f"[SOURCE-INDEX] Warning: Unreferenced anchors: 锚点{', 锚点'.join(unreferenced)}")

    def _validate_alignment_audit(self):
        """验证强制对齐复盘章节"""
        if '强制对齐复盘' not in self.content and 'Alignment Audit' not in self.content:
            self.errors.append("[ALIGNMENT-AUDIT] Missing section: 强制对齐复盘 (Alignment Audit)")
            return

        # 验证必需内容
        required_items = [
            ('状态：', '[ALIGNMENT-AUDIT] Missing: 状态'),
        ]

        for item, error_msg in required_items:
            if item not in self.content:
                self.errors.append(error_msg)

    def _validate_forbidden_formats(self):
        """验证禁止使用的格式"""
        # 禁止 Markdown 代码块
        if '```' in self.content:
            self.errors.append("[FORMAT] Markdown code blocks (```) are FORBIDDEN in CSO output")

        # 禁止 Markdown 表格（检测表格分隔符）
        table_pattern = r'\|.*\|.*\n.*\|[-\s]+\|'
        if re.search(table_pattern, self.content):
            self.errors.append("[FORMAT] Markdown tables (|---|) are FORBIDDEN in CSO output")

        # 检查是否使用了不允许的 HTML 标签
        html_tags = re.findall(r'<(\w+)>', self.content)
        forbidden_tags = ['table', 'div', 'span', 'code', 'pre']
        found_forbidden = [tag for tag in html_tags if tag.lower() in forbidden_tags]
        if found_forbidden:
            self.errors.append(f"[FORMAT] Forbidden HTML tags found: {set(found_forbidden)}")

    def get_report(self) -> str:
        """生成验证报告"""
        lines = []

        if len(self.errors) == 0:
            lines.append("✅ Output format is VALID")
            lines.append("")
            lines.append("All validation checks passed:")
            lines.append("  ✓ Header structure")
            lines.append("  ✓ P-Prompt five modules")
            lines.append("  ✓ Data encoding format")
            lines.append("  ✓ Recon level specification")
            lines.append("  ✓ Source fingerprint index")
            lines.append("  ✓ Alignment audit section")
            lines.append("  ✓ Format constraints (no Markdown code blocks/tables)")
        else:
            lines.append("❌ Output format validation FAILED")
            lines.append("")
            lines.append(f"Found {len(self.errors)} error(s):")
            for i, error in enumerate(self.errors, 1):
                lines.append(f"  {i}. {error}")

        if self.warnings:
            lines.append("")
            lines.append(f"⚠️  {len(self.warnings)} warning(s):")
            for i, warning in enumerate(self.warnings, 1):
                lines.append(f"  {i}. {warning}")

        if len(self.errors) > 0:
            lines.append("")
            lines.append("📖 For guidance on fixing these errors, read:")
            lines.append("   cat .claude/skills/cso-get/v2/references/validation-errors.md")

        return "\n".join(lines)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: validate_output.py <output-file>", file=sys.stderr)
        print("", file=sys.stderr)
        print("Example:", file=sys.stderr)
        print("  python validate_output.py /tmp/cso_output.txt", file=sys.stderr)
        sys.exit(1)

    filepath = Path(sys.argv[1])

    if not filepath.exists():
        print(f"❌ Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    if not filepath.is_file():
        print(f"❌ Error: Not a file: {filepath}", file=sys.stderr)
        sys.exit(1)

    # 读取文件
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    # 验证
    validator = CSO_Validator(content)
    is_valid = validator.validate()

    # 打印报告
    print(validator.get_report())

    # 退出
    sys.exit(0 if is_valid else 1)


if __name__ == '__main__':
    main()
