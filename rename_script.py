import os

base = "/Users/liuluheng/Library/Mobile Documents/com~apple~CloudDocs/Organized_SheetMusic/重奏"

renames = {
    "Selections from Phantom of the Opera_04490476_Conductor Score.pdf": "Selections from Phantom of the Opera(歌剧魅影选段)_Conductor Score.pdf",
    "Nocturne_Op. 5_Cello 1.pdf": "Nocturne(夜曲)_Op. 5_Cello 1.pdf",
    "Nocturne_Op. 5_Cello 2.pdf": "Nocturne(夜曲)_Op. 5_Cello 2.pdf",
    "Nocturne_Op. 5_Cello 3.pdf": "Nocturne(夜曲)_Op. 5_Cello 3.pdf",
    "Nocturne_Op. 5_Cello 4.pdf": "Nocturne(夜曲)_Op. 5_Cello 4.pdf",
    "Nocturne_Op. 5_Cello complete.pdf": "Nocturne(夜曲)_Op. 5_Complete.pdf",
    "Viva La Vida_Cello 1.pdf": "Viva La Vida(生命万岁)_Cello 1.pdf",
    "Viva La Vida_Cello 2.pdf": "Viva La Vida(生命万岁)_Cello 2.pdf",
    "Viva La Vida_Cello 3.pdf": "Viva La Vida(生命万岁)_Cello 3.pdf",
    "Viva La Vida_Cello 4.pdf": "Viva La Vida(生命万岁)_Cello 4.pdf",
    "Viva La Vida_Full Score.pdf": "Viva La Vida(生命万岁)_Full Score.pdf",
    "Viva La Vida_Score_alt_6402.pdf": "Viva La Vida(生命万岁)_Score_alt_6402.pdf",
    "Suite_Op. 16_Cello 2.pdf": "Suite(组曲)_Op. 16_Cello 2.pdf",
    "LOVE OF MY LIFE_Cello 3.pdf": "Love of My Life(一生所爱)_Cello 3.pdf",
    "Love of My Life_Cello 1.pdf": "Love of My Life(一生所爱)_Cello 1.pdf",
    "Love of My Life_Cello 1_alt_6791.pdf": "Love of My Life(一生所爱)_Cello 1_alt_6791.pdf",
    "Love of My Life_Cello 2.pdf": "Love of My Life(一生所爱)_Cello 2.pdf",
    "Love of My Life_Cello 4.pdf": "Love of My Life(一生所爱)_Cello 4.pdf",
    "Largo_B.109_Full Score.pdf": "Largo(广板)_B.109_Full Score.pdf",
    "Faure_Andantefrom2ndCelloSonata_Cello 1.pdf": "Andante from 2nd Cello Sonata(第二奏鸣曲行板)_Cello 1.pdf",
    "Faure_Andantefrom2ndCelloSonata_Cello 2.pdf": "Andante from 2nd Cello Sonata(第二奏鸣曲行板)_Cello 2.pdf",
    "Faure_Andantefrom2ndCelloSonata_Cello 3.pdf": "Andante from 2nd Cello Sonata(第二奏鸣曲行板)_Cello 3.pdf",
    "Faure_Andantefrom2ndCelloSonata_Cello 4.pdf": "Andante from 2nd Cello Sonata(第二奏鸣曲行板)_Cello 4.pdf",
    "Faure_Andantefrom2ndCelloSonata_Cello_Solo.pdf": "Andante from 2nd Cello Sonata(第二奏鸣曲行板)_Cello Solo.pdf",
    "Faure_Andantefrom2ndCelloSonata_Full_Full Score.pdf": "Andante from 2nd Cello Sonata(第二奏鸣曲行板)_Full Score.pdf",
    "Faure_Elegy_Full_Cello 1.pdf": "Elegy(悲歌)_Cello 1.pdf",
    "Faure_Elegy_Full_Cello 2.pdf": "Elegy(悲歌)_Cello 2.pdf",
    "Faure_Elegy_Full_Cello 3.pdf": "Elegy(悲歌)_Cello 3.pdf",
    "Faure_Elegy_Full_Cello 4.pdf": "Elegy(悲歌)_Cello 4.pdf",
    "Faure_Elegy_Full_Cello 5.pdf": "Elegy(悲歌)_Cello 5.pdf",
    "Faure_Elegy_Full_Cello_Solo.pdf": "Elegy(悲歌)_Cello Solo.pdf",
    "Faure_Elegy_Full_Full Score.pdf": "Elegy(悲歌)_Full Score.pdf",
    "A Town with an Ocean View_Cello 1.pdf": "A Town with an Ocean View(海边的街道)_Cello 1.pdf",
    "A Town with an Ocean View_Cello 2.pdf": "A Town with an Ocean View(海边的街道)_Cello 2.pdf",
    "A Town with an Ocean View_Cello 3.pdf": "A Town with an Ocean View(海边的街道)_Cello 3.pdf",
    "A Town with an Ocean View_Cello 4.pdf": "A Town with an Ocean View(海边的街道)_Cello 4.pdf",
    "FATA MORGANA_Cello 1.pdf": "Fata Morgana(海市蜃楼)_Cello 1.pdf",
    "FATA MORGANA_Cello 2.pdf": "Fata Morgana(海市蜃楼)_Cello 2.pdf",
    "FATA MORGANA_Cello 3.pdf": "Fata Morgana(海市蜃楼)_Cello 3.pdf",
    "FATA MORGANA_Cello 4.pdf": "Fata Morgana(海市蜃楼)_Cello 4.pdf",
    "FATA MORGANA_Cello 5.pdf": "Fata Morgana(海市蜃楼)_Cello 5.pdf",
    "Pavan & Fantasia_Cello 3.pdf": "Pavan & Fantasia(帕凡与幻想曲)_Cello 3.pdf",
    "Pavan & Fantasia_Full Score.pdf": "Pavan & Fantasia(帕凡与幻想曲)_Full Score.pdf",
    "Pavan & Fantasia_Score_alt_6531.pdf": "Pavan & Fantasia(帕凡与幻想曲)_Score_alt_6531.pdf",
    "IMSLP617256-PMLP991665-THEME_AND_VARIATIONS-Violoncello1.pdf": "Theme and Variations(主题与变奏曲)_Op. 28_Cello 1.pdf",
    "IMSLP617257-PMLP991665-THEME_AND_VARIATIONS-Violoncello2.pdf": "Theme and Variations(主题与变奏曲)_Op. 28_Cello 2.pdf",
    "IMSLP617258-PMLP991665-THEME_AND_VARIATIONS-Violoncello3.pdf": "Theme and Variations(主题与变奏曲)_Op. 28_Cello 3.pdf",
    "IMSLP617259-PMLP991665-THEME_AND_VARIATIONS-Violoncello4.pdf": "Theme and Variations(主题与变奏曲)_Op. 28_Cello 4.pdf",
    "Theme and Variations_Op. 28_Full Score.pdf": "Theme and Variations(主题与变奏曲)_Op. 28_Full Score.pdf",
    "City of Stars_Cello 1.pdf": "City of Stars(繁星之城)_Cello 1.pdf",
    "City of Stars_Cello 2.pdf": "City of Stars(繁星之城)_Cello 2.pdf",
    "City of Stars_Cello 3.pdf": "City of Stars(繁星之城)_Cello 3.pdf",
    "City of Stars_Cello 4.pdf": "City of Stars(繁星之城)_Cello 4.pdf",
    "City of Stars_Full Score.pdf": "City of Stars(繁星之城)_Full Score.pdf",
    "让我们荡起双桨_Cello 2.pdf": "Let Us Oars to Row(让我们荡起双桨)_Cello 2.pdf",
    "让我们荡起双桨_Cello 3.pdf": "Let Us Oars to Row(让我们荡起双桨)_Cello 3.pdf",
    "让我们荡起双桨_Full Score.pdf": "Let Us Oars to Row(让我们荡起双桨)_Full Score.pdf",
    "东方之珠_Cello 1.pdf": "Pearl of the Orient(东方之珠)_Cello 1.pdf",
    "东方之珠_Cello 2.pdf": "Pearl of the Orient(东方之珠)_Cello 2.pdf",
    "东方之珠_Cello 3.pdf": "Pearl of the Orient(东方之珠)_Cello 3.pdf",
    "东方之珠_Cello 4.pdf": "Pearl of the Orient(东方之珠)_Cello 4.pdf",
    "Suite for Cello Quartet_Op. 11_Full Score.pdf": "Suite for Cello Quartet(大提琴四重奏组曲)_Op. 11_Full Score.pdf",
    "Intermezzo Sinfonico_Full Score.pdf": "Intermezzo Sinfonico(交响间奏曲)_Full Score.pdf",
    "IMSLP501346-PMLP03607-E439896_etc-Tchaikovsky_NutcrackerSuite_CelloOrchestraArrangement_Seymour_ForIMSLP_-_Cello_1.pdf": "Nutcracker Suite(胡桃夹子组曲)_Cello 1.pdf",
    "Loch Lomond_Full Score.pdf": "Loch Lomond(洛蒙德湖)_Full Score.pdf",
    "Concerto for Three Solo Celli_114_Full Score.pdf": "Concerto for Three Solo Celli(三把大提琴协奏曲)_114_Full Score.pdf",
    "Dies Irae from REQUIEM_Full Score.pdf": "Dies Irae from Requiem(安魂曲震怒之日)_Full Score.pdf"
}

renamed_count = 0
for root, dirs, files in os.walk(base):
    for f in files:
        if f in renames:
            old_path = os.path.join(root, f)
            new_path = os.path.join(root, renames[f])
            os.rename(old_path, new_path)
            print(f"Renamed: {f} -> {renames[f]}")
            renamed_count += 1
print(f"Total renamed: {renamed_count}")
