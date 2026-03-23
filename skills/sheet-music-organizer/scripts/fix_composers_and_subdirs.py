import os
import shutil

base = '/Users/liuluheng/Library/Mobile Documents/com~apple~CloudDocs/Organized_SheetMusic/重奏'
if not os.path.exists(base):
    print(f"Directory not found: {base}")
    exit(1)

composers = [c for c in os.listdir(base) if not c.startswith('.')]

# 1. 恢复外文全名 (简短中文)
renames = {
    "Beethoven (贝多芬)": "Ludwig van Beethoven (贝多芬)",
    "Tchaikovsky (柴可夫斯基)": "Pyotr Ilyich Tchaikovsky (柴可夫斯基)",
    "Popper (波珀)": "David Popper (波珀)",
    "Mozart (莫扎特)": "Wolfgang Amadeus Mozart (莫扎特)",
    "Haydn (海顿)": "Joseph Haydn (海顿)",
    "Bach (巴赫)": "Johann Sebastian Bach (巴赫)",
    "Vivaldi (维瓦尔第)": "Antonio Vivaldi (维瓦尔第)",
    "Chopin (肖邦)": "Frederic Chopin (肖邦)",
    "Dvořák (德沃夏克)": "Antonín Dvořák (德沃夏克)",
    "Brahms (勃拉姆斯)": "Johannes Brahms (勃拉姆斯)",
    "Mendelssohn (门德尔松)": "Felix Mendelssohn (门德尔松)",
    "Grieg (格里格)": "Edvard Grieg (格里格)",
    "Elgar (埃尔加)": "Edward Elgar (埃尔加)",
    "Ravel (拉威尔)": "Maurice Ravel (拉威尔)",
    "Bizet (比才)": "Georges Bizet (比才)",
    "Offenbach (奥芬巴赫)": "Jacques Offenbach (奥芬巴赫)",
    "Rossini (罗西尼)": "Gioacchino Rossini (罗西尼)",
    "Klengel (克伦格尔)": "Julius Klengel (克伦格尔)",
    "Fitzenhagen (菲岑哈根)": "Wilhelm Fitzenhagen (菲岑哈根)",
    "Boccherini (博凯里尼)": "Luigi Boccherini (博凯里尼)",
    "Fauré (福雷)": "Gabriel Fauré (福雷)",
    "Bartók (巴托克)": "Béla Bartók (巴托克)",
    "Mascagni (马斯卡尼)": "Pietro Mascagni (马斯卡尼)",
    "Strauss II (小约翰·施特劳斯)": "Johann Strauss II (施特劳斯)",
    "Mercury (墨丘利)": "Freddie Mercury (墨丘利)",
    "Hurwitz (赫维茨)": "Justin Hurwitz (赫维茨)",
    "Jenkins (詹金斯)": "John Jenkins (詹金斯)",
    "Bruce (布鲁斯)": "David Bruce (布鲁斯)",
    "Warlock (沃洛克)": "Peter Warlock (沃洛克)",
    "Wilfert (威尔弗特)": "Bruno Wilfert (威尔弗特)",
    "Krein (克列因)": "Alexandre Krein (克列因)",
    "Krylatov (克雷拉托夫)": "Evgeny Krylatov (克雷拉托夫)",
    "Werner (维尔纳)": "Josef Werner (维尔纳)",
    "Geminiani (杰米尼亚尼)": "Francesco Geminiani (杰米尼亚尼)",
    "Kàan (卡恩)": "Henri de Kàan (卡恩)",
    "Ellenburger (埃伦伯格)": "Kurt Ellenburger (埃伦伯格)",
    "Beatty (比蒂)": "Stephen W. Beatty (比蒂)",
    "Elizondo (埃利松多)": "José L. Elizondo (埃利松多)",
    "Komzák II (科姆扎克二世)": "Karl Komzák II (科姆扎克二世)",
    "Graham (格雷厄姆)": "Brendan Graham (格雷厄姆)",
    "Dare (戴尔)": "Marie Dare (戴尔)",
    "Llamazares (利亚马萨雷斯)": "Pablo Fernando Llamazares (利亚马萨雷斯)",
    "Hisaishi (久石让)": "Joe Hisaishi (久石让)",
    "Kozlov (科兹洛夫改编)": "Maxim Kozlov (科兹洛夫)",
}

for old in composers:
    if old in renames:
        old_path = os.path.join(base, old)
        new_path = os.path.join(base, renames[old])
        try:
            os.rename(old_path, new_path)
            print(f"Renamed composer: {old} -> {renames[old]}")
        except Exception as e:
            pass

# 重新获取作曲家列表
composers = [c for c in os.listdir(base) if not c.startswith('.')]

# 2. 为每个曲目创建子文件夹
moved_count = 0
for comp in composers:
    comp_path = os.path.join(base, comp)
    if not os.path.isdir(comp_path):
        continue
    
    for fname in os.listdir(comp_path):
        if not fname.endswith('.pdf'):
            continue
            
        # 解析曲名
        parts = fname[:-4].split('_')
        piece_name = parts[0].strip()
        
        piece_dir = os.path.join(comp_path, piece_name)
        if not os.path.exists(piece_dir):
            os.makedirs(piece_dir)
            
        old_file = os.path.join(comp_path, fname)
        new_file = os.path.join(piece_dir, fname)
        
        shutil.move(old_file, new_file)
        moved_count += 1

print(f"Done. Moved {moved_count} PDF files into individual piece folders.")
