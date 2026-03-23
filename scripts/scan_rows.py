import openpyxl
import json

path = "/Users/liuluheng/Library/CloudStorage/OneDrive-个人/Workfiles/05.项目运营/2026年度工作计划表.xlsx"
wb = openpyxl.load_workbook(path, data_only=True)
sheet = wb["工作表1"]

for r in range(11, 20):
    row_data = [cell.value for cell in sheet[r]]
    print(f"Row {r}: {row_data}")
