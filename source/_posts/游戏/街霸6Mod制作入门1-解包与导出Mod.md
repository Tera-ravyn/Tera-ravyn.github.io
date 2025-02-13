---
title: 街霸6Mod制作入门1-解包与导出Mod
categories: 游戏
tags:
  - 街霸
  - Mod制作
date: 2025-02-10 14:55:10
updated: 2025-02-10 14:55:10
cover: https://image.baidu.com/search/down?url=https://imglf4.lf127.net/img/9d9fff3e7d72f203/SHRJMUQ3VE0yMkpNeTBROHplMmYwVVZHbkNKUWdnSHVUYkpOaHgwNXZ1cz0.png?imageView&thumbnail=1680x0&quality=96&stripmeta=0
---
## 前言

这系列文章并不是很正式的教程，而更接近于一个备忘。主要内容都参考自 Remy2Fang 的 Mod 制作导论。下文很多插件给出的下载链接是 github 仓库地址，如果打不开请自行使用 steam++ 等手段加速；要在仓库页面下载发行包，找到页面右侧的 `releases`，点击进行下载。

## 一、准备工具

### 1. RETool/MHRUnpack

要获取游戏内的文件，我们首先需要对游戏进行解包。所谓包，就是游戏的 `.pak` 文件，和游戏的可执行程序在同一文件夹下，可以通过在 steam 中右键要解包的游戏，点击**属性-安装位置-浏览本机上的文件**来直接打开这些游戏文件所在的文件夹。而RETool 和 MHRUnpack 都是用于从 `.pak` 包中解包出文件的程序。它们的区别在于，RETool 是全量解包，而 MHRUnpack 可以选择想要导出的文件，进行非全量解包。

个人更倾向于直接使用 MHRUnpack，虽说看名字就知道最初是为 MHR 制作的解包软件，不过它也适用于所有 RE Engine 开发的游戏。另外 MHRUnpack 由国人开发，内置中文使用指南。

无论使用哪种方法解包，都需要对应的 `.list` 文件（`.list` 文件的名字需要和解包程序内的名字匹配，并且目录下有且只能有一个）。

RETool 的使用方式：将 `.list` 文件放置在同一目录下，然后将 `.pak` 文件拖拽到 `extract-pak.bat` 批处理程序上，等待解压即可。使用 RETool 的时候必须按 pak 的 patch 更新顺序依次解压。

MHRUnpack 的使用方式：将 `.list` 文件更名为 `MHRisePC.list` ，放置在 `.exe` 可执行文件同一目录下，然后运行 MHRUnpack。等待 `.list ` 文件自动导入完成，之后就可以选择要导出的文件并且导出。关于需要导出哪些文件，可以跳到文末的速查表进行查看。

[下载 RETool](https://fluffyquack.com/tools/REtool.zip)

[下载 MHRUnpack](https://www.nexusmods.com/monsterhunterrise/mods/849)

[所有 Capcom 游戏的 list 文件](https://github.com/Ekey/REE.PAK.Tool/tree/main/Projects)

### 2. Noesis 以及相关插件

Noesis 是一款可以查看各种模型格式文件以及对模型进行格式转换、导入导出的工具。

配合插件，它可以把 RE Engine 的专有格式如 `.mesh.230110883` 以及 `.mdf2.31` 转换到 `.fbx` 格式，以便导入其他建模工具。不过，如果使用 blender 进行编辑操作，它不是非常必要，可以直接跳到 [3. Blender 及其插件](### 3. Blender 及其插件) 。

插件的安装方式：安装 Noesis 之后，打开 `[Noesis 安装路径]/plugins/python` 文件夹并将  `fmt_RE_MESH.py` 放入其中，然后重新启动该程序。安装插件后，使用 Noesis 打开网格或 `tex` 文件将自动加载它。

[Noesis 下载](https://richwhitehouse.com/index.php?content=inc_projects.php&showproject=91)

[Noesis 导入、导出 RE Engine 文件插件](https://github.com/alphazolam/fmt_RE_MESH-Noesis-Plugin)

### 3. Blender 及其插件

如果你更熟悉 3ds Max ，也可以用 3ds Max，配合 Noesis 使用导出的 fbx，并且在完成对 fbx 的编辑后再用 Noesis 转回 mesh 文件。如果 3ds Max 和 Blender 你都不知道是什么，那我推荐你直接用 Blender，因为它开源免费，而且插件也更好用。



[在 Blender 内导入导出 RE Engine 的 mesh 和 mdf2 文件的插件](https://github.com/NSACloud/RE-Mesh-Editor)

[在 Blender 的资产文件夹里直接浏览 RE Engine 文件的插件](https://github.com/NSACloud/RE-Asset-Library)

[在 3ds Max 内导入 RE Engine 的 mesh 文件的插件](https://www.mediafire.com/file/jczyvcbtadoira6/RE_Engine_Mesh_v1.39b.ms.zip/file) 

## 二、导出 Mod

一切素材都处理好后，为 Mod 新建一个文件夹，这个文件夹内应该包含：1. Mod 本体的文件；2. 介绍 Mod 内容的 `modinfo.ini` ；3. 预览图像 `screenshot.png`。

### 1. Mod 本体文件

用于替换的 mod 文件需要以原文件所在路径以及相同的名字去覆盖。

> 例如：修改卢克皮肤 2 身体部分的模型，需要按照以下路径创建文件夹并命名文件：
> natives/stm/product/model/esf/esf002/002/01/esf002_002_01.mesh.230110883

### 2. `modinfo.ini`

新建文本文档，以 `[属性]=[值]` 的格式记录关于 mod 的信息。编辑完成后把后缀名改成 `.ini` 即可。以下是一个配置文件样例：

``` modinfo.ini
name=Luke C2 with Shirt
version=1.0
description=shirt Luke
screenshot=screenshot.png
author=RavynTera
```

### 3. 预览图像

在当前文件夹里放入 `screenshot.png` 就好了。也可以不叫这个，和 `modinfo.ini` 里 `screenshot` 属性一致就行。

## 三、加载 Mod

Mod 文件夹完成后，可以按照需求打包成 `.rar` 文件。一般正式发布的 Mod 都是经过打包的，不过还需要调试的 Mod 可以直接以文件夹形式存放。两者都可以被 Mod 管理器正常读取。

安装 [Fluffy Mod Manager](https://www.nexusmods.com/streetfighter6/mods/14) ，在程序的根目录找到（或新建） `Games/SF6/Mods` ，放入整个 Mod 文件夹，运行程序即可读取成功。

## 文件对应游戏内容速查表

### 角色模型

路径： `natives/stm/product/model/efs `

**Charcters**
esf001 - Ryu
esf002 - Luke
esf003 - Kimberly
esf004 - Chun-Li
esf005 - Manon
esf006 - Zangief 
esf007 - JP
esf008 - Dhalsim
esf009 - Cammy
esf010 - Ken
esf011 - Dee Jay
esf012 - Lily
esf013 - A.K.I.
esf014 - Rashid
esf015 - Blanka
esf016 - Juri
esf017 - Marisa
esf018 - Guile
esf019 - E.D.
esf020 - E. Honda
esf021 - Jamie
esf022 - Gouki (Akuma)
esf026 - Vega (Bison)
esf027 - Terry
esf028 - Mai


### NPC 模型

路径： `natives/stm/product/model/npc`

**NPCs**
npc1000 - Bosch
npc1001 - Li-Fen  
npc1002 - Rudra  
npc1003 - Eternity the Host  
npc1999 - Yua and the other dancers

### 环球游历道具模型

路径： `natives/stm/product/model/wcs`

**World Tour Mode Create-a-Character Items**  
wcs000 = hair (can't export, but can be replaced)  
wcs001 = hats and masks  
wcs002 = Shirts  
wcs003 = Shirts with Sweaters  
wcs004 = Pants  
wcs006 = Shoes and socks  
wcs007 = Leggings?  
wcs008 = Accessories (glasses, jewelry, gloves, boxing gloves, cat ears, wings, etc)  
wcs009 = ??  
wcs601 = Masks  
wcs602 = There's a Super Hero jumpsuit lol  
  
wpl100 (male) & wpl200 (female) = Avatar Head, skin textures, chain files, etc.

### 纹理材质

除了模型同一目录下所携带的内容，还可以在 `natives/stm/streaming/product/model` 下找到分辨率更高的相同材质。

### 不同 patch 的 pak 包所含的内容

patch_001：增加了拉希德的模型。

patch_004：mdf2 材质更新。

patch_007：更新了皮肤三和颜色（CMD 文件）。

patch_009：玛丽莎皮肤三部分模型更新。

patch_010：增加了爱德的模型，更新了所有角色的 chain 文件。

patch_011：增加了豪鬼的模型，更新了隆的部分模型，更新了配色（对应 `custom_colors_file` 字段的 CCVD 文件），肌肉动画（对应 ` muscle_control_udata` 字段的 shape 文件）, 部分物理效果（havok 文件）。

patch_012：增加了维加的模型。

patch_013：增加了部分角色的 ccvd 文件。

patch_014：增加了特瑞的模型。更新了chain 文件。

patch_015：更新了肯、玛丽莎、维加部分材质、颜色等。

patch_017：增加了舞的模型。

## References

[Remy2Fang的 Mod 教学合集](https://www.tumblr.com/remy2fang/748342653516742656/street-fighter-6-modding-guide-and-tutorial)