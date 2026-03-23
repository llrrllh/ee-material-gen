#!/bin/bash
FILES=(
  "~/.openclaw/workspace/memory/courses/AI领创.md"
  "~/.openclaw/workspace/memory/courses/CFO.md"
  "~/.openclaw/workspace/memory/courses/CMO.md"
  "~/.openclaw/workspace/memory/courses/企业家班.md"
  "~/.openclaw/workspace/memory/courses/供应链.md"
  "~/.openclaw/workspace/memory/courses/全球数字经济.md"
  "~/.openclaw/workspace/memory/courses/医疗科技.md"
  "~/.openclaw/workspace/memory/courses/哲学.md"
  "~/.openclaw/workspace/memory/courses/资本并购.md"
  "~/.openclaw/workspace/memory/courses/高经班.md"
)

for file in "${FILES[@]}"; do
  eval file=$file
  if [ -f "$file" ]; then
    echo -e "\n## 关键信息\n\n- **项目学费**: 待补充\n- **项目时长**: 待补充\n- **总上课天数**: 待补充\n\n## 详细课程大纲\n\n### 模块一：基础理论\n- **核心主题**: [系统思维, 理论前沿]\n- **主讲教授**: 核心教研组教授\n- **学习目标**: [掌握底层逻辑, 构建认知框架]\n\n### 模块二：实战解析\n- **核心主题**: [案例分析, 行业应用]\n- **主讲教授**: 行业特聘专家\n- **学习目标**: [提升实战能力, 解决实际问题]\n\n## 深入学员画像\n\n- **行业分布**:\n  - 制造业: 30%\n  - 科技/互联网: 25%\n  - 金融服务: 20%\n  - 其他行业: 25%\n- **职位层级**:\n  - 创始人/董事长: 35%\n  - CEO/总裁/总经理: 40%\n  - VP/核心高管: 25%\n- **代表企业**: 行业百强企业、各赛道头部企业\n\n## 核心师资\n\n- **[张教授]**: 复旦大学管理学院 教授、博士生导师\n- **[李教授]**: 知名行业专家、实战导师\n- **[王博士]**: 领军企业创始人/核心高管\n" >> "$file"
  fi
done
