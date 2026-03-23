import openpyxl
import json

try:
    path = "/Users/liuluheng/Library/CloudStorage/OneDrive-个人/Workfiles/05.项目运营/股权投资班/开班相关/股权投资班开班准备checklist.xlsx"
    wb = openpyxl.load_workbook(path, data_only=True)
    sheet = wb.active

    results = []
    for r in range(1, 15):
        row_data = [str(c.value) if c.value else "" for c in sheet[r]]
        results.append(" | ".join(row_data))
    
    print(json.dumps(results, ensure_ascii=False, indent=2))
except Exception as e:
    print(str(e))
