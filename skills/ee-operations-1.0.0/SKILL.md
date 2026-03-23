---
name: ee-operations
description: Automate and manage Fudan Executive Education (EE) daily operations, including course preparation checklists, admission/interview notifications, and post-course follow-ups. Use when asked to generate checklists, send course reminders, schedule operations, or manage EE class logistics.
read_when:
  - User asks to "准备一下上课", "生成课前checklist", "排一下课", "写一个新的ee operations技能"
  - Need to manage EE daily operations, interview notifications, or class logistics
  - Need to generate standard operating procedures (SOPs) for class delivery
metadata: {"clawdbot":{"emoji":"🏢","requires":{"bins":["python3"]}}}
allowed-tools: Bash(ee-operations:*)
---

# EE Operations (复旦管院高管教育项目运营)

This skill defines the standard operating procedures (SOPs) and automation workflows for Fudan EE project management, spanning from pre-course preparation to post-course delivery.

## 1. Core Operating Modes

Based on the established `fudan_ee_operations.md` memory, operations are divided into two main tracks:

### A. "开学典礼" (Opening Ceremony / New Class Launch)
- **Goal:** Establish identity, break the ice, and launch the program successfully.
- **Key Stages:**
  1. **T-30 (启动规划):** Confirm dates, venues, key speakers, and budget.
  2. **T-20 (信息设计):** Finalize visual assets, backdrops, name tags, and welcome letters.
  3. **T-10 (制作采购):** Order materials, catering, gifts, and uniforms.
  4. **T-3 (最终筹备):** Venue setup, AV testing, staff briefing, and final rehearsals.
- **Focus Areas:** Teaching, Marketing, Students, Banquet.

### B. "日常授课" (Daily Class Operations - e.g., 企业家班, 高经班)
- **Goal:** Ensure flawless course delivery and premium student experience.
- **Key Timeline (Reverse Scheduled):**
  - **T-7 (课前一周):** 
    - 确认师资行程与接送安排。
    - 确认场地布置需求（课桌型/岛型）、设备要求。
    - 发送【正式上课通知】给学员。
  - **T-3 (课前三天):**
    - 落实餐饮（茶歇、午餐、晚宴排位）。
    - 打印物料（桌牌、签到表、讲义、反馈表）。
    - 确认助教与摄影摄像安排。
  - **T-1 (课前一天):**
    - 场地验收（温控、灯光、麦克风、PPT翻页笔测试）。
    - 物料入场摆放。
    - 提醒讲师与核心学员。
  - **D-Day (课程当天):**
    - 提前1小时到场，迎宾签到。
    - 控场（时间管理、茶歇翻台、突发应对）。
  - **T+1 (课后一天):**
    - 整理学员反馈表并发送报告。
    - 财务结算与供应商报销。
    - 资料归档（照片、课件、录音）。

## 2. Standardized Communications (话术模板)

When asked to generate notifications, STRICTLY adhere to Lila's formatting standards: "Professional, elegant, structured, no empty corporate jargon."

### Interview Reminder (线上面试通知)
Use when generating reminders for online admission interviews (e.g., 大健康项目):

```text
【复旦管院XX项目 - 面试温馨提示】

XX总您好，

您的线上面试将于 **[日期] [时间]** 准时开始。
面试链接及入会密码已发送至您的邮箱，请注意查收。

为确保面试顺利，请您：
1. **提前5分钟**点击链接进入等候室测试设备。
2. 保持网络畅通，处于安静的室内环境。
3. 建议着**商务便装**出席。

期待您的精彩表现！如有任何设备登录问题，请随时与我联系。
```

### Class Notification (正式上课通知)
Use when generating the T-7 course reminder:

```text
【复旦管院XX项目 - 上课通知】

尊敬的XX班同学：

本月课程将于 **[日期]** 在 **[地点]** 举行。

📚 **课程预告：**
- [日期/上午]: 《[课程名称]》 - [授课教授]
- [日期/下午]: 《[课程名称]》 - [授课教授]

📌 **重要提醒：**
- 签到时间：[时间]
- 着装要求：[如：商务休闲/正装]
- 课前材料：已发送至班级群，请提前审阅。

期待在复旦校园与您重聚！
```

## 3. Automation Workflows

When the user says "排一下课" (Schedule a class) or "准备一下上课" (Prepare for class) and provides a date:
1. Calculate the T-7, T-3, and T-1 dates relative to the provided class date.
2. Generate a structured Markdown checklist tailored to those specific dates.
3. Offer to draft the official "Class Notification" (上课通知) for the T-7 milestone.
4. If it's a new class launch ("开学"), switch to the T-30/T-20/T-10/T-3 Opening Ceremony checklist.
