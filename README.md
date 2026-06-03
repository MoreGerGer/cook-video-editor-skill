# Cook Video Editor

一个用于做饭短视频剪辑的 Codex Skill。

## Skill 使用方式

把这个目录放到 Codex 的 Skills 目录下：

```bash
~/.codex/skills/cook-video-editor
```

目录结构应类似：

```text
cook-video-editor/
  SKILL.md
  README.md
  agents/
    openai.yaml
  scripts/
    scaffold_cook_project.py
  references/
    naming.md
```

使用时，在 Codex 会话中提供素材目录、菜名和步骤：

```text
用 cook-video-editor 剪 /path/to/做饭素材目录

菜名：芦笋杏鲍菇炒虾仁

步骤：
准备 芦笋 虾仁 杏鲍菇 蒜 花椒粒
腌制虾仁
加入生抽、白胡椒、料酒
处理芦笋
切杏鲍菇和蒜
芦笋焯水
煎虾仁
炒蒜和花椒
炒杏鲍菇
倒入芦笋和虾仁
调味翻炒
装盘出锅
```

推荐把素材按步骤命名，这样字幕和动作更容易匹配：

```text
01_成品展示.MOV
02_准备食材.MOV
03_虾仁加生抽.MOV
04_虾仁加白胡椒.MOV
05_虾仁加料酒.MOV
06_虾仁调味完成静置.MOV
07_芦笋切尾部.MOV
08_芦笋削硬皮.MOV
09_芦笋斜切段.MOV
10_杏鲍菇切块.MOV
11_蒜切块.MOV
12_芦笋焯水.MOV
13_芦笋捞出.MOV
14_虾仁下锅.MOV
15_虾仁煎至金黄.MOV
16_炒蒜和花椒.MOV
17_炒杏鲍菇.MOV
18_倒入芦笋.MOV
19_倒入虾仁.MOV
20_调味翻炒.MOV
21_出锅装盘.MOV
```

如果某一步没有明确的动作画面，可以使用完成状态命名：

```text
06_虾仁调味完成静置.MOV
```

Skill 会生成类似下面的输出：

```text
菜名/
  菜名.mp4
  菜名.srt
  菜名jp.srt
  菜名-封面.jpg
  project/
    clip_plan.tsv
    build_video.sh
    render_subtitles.py
    base_no_subtitles.mp4
    segments/
    subtitle_overlays/
```

如果需要微调某个片段，修改：

```text
菜名/project/clip_plan.tsv
```

然后重新运行：

```bash
bash "菜名/project/build_video.sh"
```

## 成片的内容结构

默认成片是竖屏做饭短视频，结构如下：

1. 成品或食材画面，叠加菜名标题
2. 展示主要食材和辅料
3. 处理主食材，例如腌制、焯水前准备
4. 切配蔬菜、菌菇、蒜、辣椒等配料
5. 焯水、沥水或其他预处理
6. 煎、炒或处理主料
7. 炒香蒜、花椒、辣椒等料头
8. 加入配菜并翻炒
9. 主料回锅并翻炒均匀
10. 加入盐、糖、鸡精、生抽等调味
11. 最后翻炒完成
12. 装盘或出锅
13. 成品展示
14. 可选的订阅、关注或结尾提示

默认视频风格：

```text
竖屏 1080x1920
60fps
每个动作通常 1-3 秒
一个动作对应一条字幕
白字黑边字幕烧进视频
中文为主，同时生成英文和日文字幕
```
