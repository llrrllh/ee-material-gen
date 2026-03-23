import openpyxl
import json

path = "/Users/liuluheng/Library/CloudStorage/OneDrive-个人/Workfiles/05.项目运营/2026年度工作计划表.xlsx"
wb = openpyxl.load_workbook(path, data_only=True)
print(json.dumps(wb.sheetnames))
