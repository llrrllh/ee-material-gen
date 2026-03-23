# 乐谱库编目规范 (Sheet Music Cataloging Standards)

为保证重奏乐谱库的长期可检索性与可维护性，所有目录与文件须严格遵循「三级标准化」命名：

## 第一级：作曲家目录 (Composer Directory)
**规范**：西方作曲家保留“外文姓氏/常用名 (中文通译名)”即可，无需冗长全名；中国作曲家仅保留“中文名”。
**目的**：保持目录简洁，便于浏览和搜索。
*   西方作曲家示例：`Beethoven (贝多芬)`、`Tchaikovsky (柴可夫斯基)`、`Popper (波珀)`
*   中国/亚洲作曲家示例：`久石让`、`鲍元恺`、`刘炽`

## 第二级：曲目名称 (Work Title)
**规范**：`外文/英文曲名(中文曲名)`
**目的**：确保曲目信息全球通用（方便去 IMSLP 查谱），且在国内排练发谱时一目了然。
*   错误：`YOU RAISE ME UP_...`、`踏雪寻音_...`
*   正确：`You Raise Me Up(你鼓舞了我)_...`、`Ta Xue Xun Yin(踏雪寻音)_...`

## 第三级：作品号与声部 (Opus & Part)
**规范**：`..._[作品号]_[标准声部].pdf`
*   **作品号**（若有）：使用标准缩写加空格，如 `Op. 33`、`BWV 1068`、`K. 458`。无则省略。
*   **标准声部**：
    *   总谱：`Full Score`
    *   总分谱合集：`Complete`
    *   分谱合集：`All Parts` / `Parts`
    *   各声部分谱：`Cello 1` ~ `Cello 6`
    *   独奏声部：`Cello Solo`

## 最终文件路径结构示例
```text
重奏/
└── Tchaikovsky (柴可夫斯基)/
    ├── Variations on a Rococo Theme(洛可可主题变奏曲)_Op. 33_Full Score.pdf
    ├── Variations on a Rococo Theme(洛可可主题变奏曲)_Op. 33_Cello 1.pdf
    └── Variations on a Rococo Theme(洛可可主题变奏曲)_Op. 33_Cello 2.pdf
```