#!/usr/bin/env python3
import openpyxl
import json
import os
import subprocess
from datetime import date, datetime
import hashlib

# --- Configuration ---
CHECKLIST_PATH = "/Users/liuluheng/Library/CloudStorage/OneDrive-个人/Workfiles/05.项目运营/AI领创计划/AI领创2期_运营Checklist.xlsx"
STATE_FILE_PATH = "/Users/liuluheng/.openclaw/workspace/scripts/ai_checklist_state.json"
REMINDERS_LIST_NAME = "AI领创2期"

def get_task_id(task_name):
    return hashlib.md5(task_name.encode('utf-8')).hexdigest()

def read_excel_tasks():
    tasks = {}
    try:
        wb = openpyxl.load_workbook(CHECKLIST_PATH, data_only=True)
        ws = wb["开学前 (总览)"]
        for row in ws.iter_rows(min_row=2, values_only=True):
            if len(row) < 8:
                continue
            phase, category, task, owner, start_date_val, due_date_val, status, notes = row[:8]
            if not task or status == "已完成":
                continue
            
            due_date_str = None
            if isinstance(due_date_val, datetime):
                due_date_str = due_date_val.strftime('%Y-%m-%d')
            elif isinstance(due_date_val, date):
                due_date_str = due_date_val.strftime('%Y-%m-%d')
            elif isinstance(due_date_val, str):
                # Try to parse string dates, handle simple cases
                try:
                    due_date_str = datetime.strptime(due_date_val, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
                except: # Fallback for non-standard date strings
                    pass

            task_id = get_task_id(task)
            tasks[task_id] = {"title": task, "due": due_date_str, "status": status}
        return tasks
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return {}

def load_state():
    if os.path.exists(STATE_FILE_PATH):
        with open(STATE_FILE_PATH, 'r') as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE_PATH, 'w') as f:
        json.dump(state, f, indent=2)

def get_existing_reminders():
    reminders = {}
    try:
        # First, ensure the list exists
        subprocess.run(["remindctl", "list", REMINDERS_LIST_NAME, "--create"], check=True)
        
        # Then, get its contents
        result = subprocess.run(["remindctl", "list", REMINDERS_LIST_NAME, "--json"], capture_output=True, text=True, check=True)
        reminders_list = json.loads(result.stdout)
        for r in reminders_list:
            reminders[r['title']] = r
        return reminders
    except Exception as e:
        print(f"Error getting existing reminders: {e}")
        return {}

def run_sync():
    print(f"--- Starting sync at {datetime.now()} ---")
    current_tasks = read_excel_tasks()
    last_state = load_state()
    existing_reminders = get_existing_reminders()
    
    # --- Sync logic ---
    # 1. New and updated tasks
    for task_id, task_data in current_tasks.items():
        title = task_data["title"]
        due = task_data["due"]
        
        if task_id not in last_state:
            # New task
            print(f"  [NEW] Adding: {title}")
            cmd = ["remindctl", "add", "--list", REMINDERS_LIST_NAME, "--title", title]
            if due:
                cmd.extend(["--due", due])
            subprocess.run(cmd)
        elif task_data != last_state.get(task_id):
            # Updated task
            print(f"  [UPDATE] Updating: {title}")
            if title in existing_reminders:
                reminder_id = existing_reminders[title]['id']
                cmd = ["remindctl", "edit", reminder_id]
                if due:
                    cmd.extend(["--due", due])
                else:
                    cmd.append("--clear-due")
                subprocess.run(cmd)

    # 2. Deleted tasks
    for task_id, task_data in last_state.items():
        if task_id not in current_tasks:
            title = task_data["title"]
            print(f"  [DELETE] Deleting: {title}")
            if title in existing_reminders:
                reminder_id = existing_reminders[title]['id']
                subprocess.run(["remindctl", "delete", reminder_id, "--force"])

    # --- Save new state ---
    save_state(current_tasks)
    print("--- Sync complete ---")

if __name__ == "__main__":
    run_sync()
