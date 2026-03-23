import datetime
import subprocess
import os
import sys

# SOP Content mapping
SOP_TIMELINE = {
    0: "📅 **周一：前置确认**\n\n1. 📢 **提醒学生**：发送第一次上课通知。\n2. 👨‍🏫 **联系老师**：确认课程信息，催要电子版课件。\n3. 🖨️ **文印对接**：提醒本周的设计与制作任务。",
    2: "📅 **周三：深度核对**\n\n1. 📢 **学生通知**：第二次确认上课通知。\n2. 🏨 **师资接待**：确认老师接待细节（是否接送、订房要求）。\n3. 📑 **名单核定**：根据最新名单，核定席卡、签到表、授课证明。\n4. 🙋 **助教落实**：确定助教人选，确认文印进度。",
    3: "📅 **周四：流程与物资**\n\n1. 🖥️ **流程申请**：发起企微/PDC电子屏及流程申请。\n2. 📦 **物资清点**：清点现场物资（立屏、话筒套、笔记本等）。",
    4: "📅 **周五：交付冲刺**\n\n1. 📽️ **内容制作**：完成同学录 PPT 制作。\n2. 🍱 **场地布置**：中午前督促姜老师布置茶歇桌/签到桌。\n3. 🛠️ **现场检查**：下午检查现场设备，借翻页笔。\n4. ✉️ **最终提醒**：傍晚发送学生报到导引、老师行前提醒（房号/车牌）。"
}

def send_message(msg):
    # Use 'openclaw message send' via subprocess or print for the agent to pick up
    # In a cron turn, the agent's output is delivered to the channel.
    print(msg)

def check_calendar():
    # Placeholder for 'gog' check. 
    # For now, we check if a manual trigger file exists or if it's explicitly a "Class Week"
    # We could also look for "上课" in the current month's calendar if gog was setup.
    try:
        # Check if manual override exists for this week
        if os.path.exists("current_class_week.txt"):
            with open("current_class_week.txt", "r") as f:
                content = f.read().strip()
                if content == datetime.datetime.now().strftime("%Y-%W"):
                    return True
        
        # Real calendar check if gog is configured
        # gog calendar events primary --from <monday> --to <sunday> | grep "上课\|企业家班"
        # Since auth is missing, we skip for now but the logic is ready.
        return False
    except:
        return False

def main():
    today = datetime.datetime.now()
    weekday = today.weekday() # 0 is Monday
    
    if weekday not in SOP_TIMELINE:
        # Not a trigger day
        sys.exit(0)
    
    # Check if this is a class week
    if not check_calendar():
        # If no automatic detection, we don't spam. 
        # But for the first time, we might want to tell the user how to activate.
        sys.exit(0)

    msg = f"🔔 **复旦 EE 上课准备提醒**\n\n{SOP_TIMELINE[weekday]}\n\n请确认当前进度，如有需要请随时叫我处理！"
    send_message(msg)

if __name__ == "__main__":
    main()
