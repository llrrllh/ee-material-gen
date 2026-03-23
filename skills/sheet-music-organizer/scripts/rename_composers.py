import os

base = '/Users/liuluheng/Library/Mobile Documents/com~apple~CloudDocs/Organized_SheetMusic/重奏'
composers = [c for c in os.listdir(base) if not c.startswith('.')]

renames = {
    "Lalila (拉莉拉)": "Lalila (拉莉拉)", 
    "Rabinowitz (拉比诺维茨)": "Rabinowitz (拉比诺维茨)"
}

count = 0
for old in composers:
    if old in renames and renames[old] != old:
        old_path = os.path.join(base, old)
        new_path = os.path.join(base, renames[old])
        try:
            os.rename(old_path, new_path)
            print(f"Renamed: {old} -> {renames[old]}")
            count += 1
        except Exception as e:
            print(f"Error renaming {old}: {e}")

print(f"Total directories renamed: {count}")
