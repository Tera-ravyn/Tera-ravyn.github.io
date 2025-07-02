---
title: Mate Engine模组制作
categories: 技术
tags:
  - 3D模型
  - Mate-Engine
date: 2025-06-30 09:30:52
updated: 2025-06-30 09:30:52
cover:
---
## 前言

[项目 wiki 网址](https://github.com/shinyflvre/Mate-Engine/wiki)

需求：

- Visual Studio（建议在安装 Unity 之前就手动安装，否则会默认安装到 C 盘）
- Unity 6000 版本（需要先下载 Unity Hub；cn 分部没有 6000 的下载入口，可以打开浏览器新页面在地址栏输入 `unityhub://6000.0.46f1` 进行下载安装，后面的版本号也可以按需更换）
- Mate Engine 项目源代码（clone 或者下载都行）

## MateSDK

获取源代码后，打开 Unity Hub，添加 Mate-Engine 项目。源代码使用的引擎版本在添加后就可以看到。

![](IMG-20250702103409246.png)

项目成功启动后，可以看到右侧有一个 MateEngine SDK 窗口，提供了四个功能：导出模组、导出模型模组、骨骼合并以及 VRM 模型校验器。

![](IMG-20250702103628453.png)
## 模型模组

ME 模型模组能够完成的内容：自定义 shader

ME 模型模组不能完成的内容：使用非 VRM 标准骨骼的模型

非 VRM 标准骨骼的模型，可以在其他程序中处理并导出为 VRM 模型，再添加到 Unity 当中修改材质。当然也可以直接在 Unity 中修改，ME 的工程已经内置了 UniVRM。

软件本身自带的模型资源都放在了 `Assets/MATE ENGINE - Avatar` 中，建议在导入自己的模型资产的时候也放在这里，保持文件结构一致性。导入方式可以是将文件直接复制到路径下，或者拖拽到 project 的窗口。

模型导入后，点击新建→ scene → prefab，双击 prefab 进入编辑界面，将模型拖入，之后可以对模型进行编辑。被打包进模型的材质无法直接编辑，建议新建 `.Textures` 并复制模型的材质到里面，之后将模型的材质替换为这些新材质，再进行材质和 shader 的修改。

![](IMG-20250702104314768.png)



## 服装模组

## 动画模组

## 声音模组

