import openpyxl
import json

path = "/Users/liuluheng/Library/CloudStorage/OneDrive-个人/Workfiles/05.项目运营/2026年度工作计划表.xlsx"
wb = openpyxl.load_workbook(path, data_only=True)
sheet = wb["工作表1"]

rows = []
for row in sheet.iter_rows(min_row=1, max_row=10, values_only=True):
    rows.append(row)

print(json.dumps(rows, ensure_ascii=False))
