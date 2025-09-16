---
title: UE编译报错MSB3073
categories: 技术
tags:
  - UE5
  - 虚幻引擎
date: 2025-09-16
updated: 2025-09-16
cover:
---
## 问题简述

打开 VS 手动 build 项目的时候报MSB3073。

## 产生原因及解决方案

#### 1. Living Code 和 VS 编译器同时运行

关闭 UE，或者单独关闭 Living Code 即可。

#### 2. 有不符合编码规范的子文件/路径

一般是路径或者资产名称使用了中文字符，修改掉即可。需要注意的是，如果项目启用了 git，git 提交记录里的中文也会被读取到从而导致报错，可以先将 .git 文件夹备份后删除，先通过编译再添加回项目。

#### 3. 缺少 dll 文件

缺啥加啥，这大概也是纯代码插件才会出现的问题（比如 `PuerTS`）。

#### 4. MSVC 版本不对

这种情况一般 return code=6。原因是UnrealBuildTool 自动会选用目前安装的工具链里最新的 MSVC，但是老版本引擎可能存在部分对应组件/插件需要选用对应版本的 MSVC 的情况。

在执行 build 时，可以在输出中看到这一行提示使用工具链版本的信息。

```output
2>Using Visual Studio 2022 14.44.35216 toolchain (C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.44.35207) and Windows 10.0.26100.0 SDK (C:\Program Files (x86)\Windows Kits\10).
```

以笔者使用的 5.3 引擎版本举例，使用 14.44 版本时会有若干头文件报错如下：

```output
2>C:\Program Files\Epic Games\UE_5.3\Engine\Source\Runtime\Core\Public\Experimental\ConcurrentLinearAllocator.h(31): error C4668: 没有将“__has_feature”定义为预处理器宏，用“0”替换“#if/#elif”
```

而在 14.36~14.38 的版本中，该头文件第 20 行定义了这个宏，因此是纯粹的版本不兼容。

但是 VS 编辑器中是无法直接选择编译时使用的 MSVC 版本的，以下有几种处理方式：

##### 1. 卸载最新的 MSVC 工具，只安装对应版本的 MSVC 工具（仅推荐只固定使用一个版本且不需要在其他地方使用 VS 的用户）

在 Visual Studio Installer 里，切至 `单个组件` 窗口，去掉不需要的 MSVC 版本，仅保留需要的 MSVC 版本，然后执行修改。

##### 2. 指定 MSVC 版本（推荐）

根据官网文档中 Build Configuration 一节所述，可以使用 `CompilerVersion` 标签对 MSVC 版本进行指定。

> $ CompilerVersion : The specific compiler version to use. This may be a specific version number (for example, "14.13.26128"), the string "Latest" to select the newest available version, or the string "Preview" to select the newest available preview version. By default, and if it is available, we use the toolchain version indicated by WindowsPlatform.DefaultToolChainVersion (otherwise, we use the latest version).

而 Unreal Build Tool (UBT) 可以从以下路径读取到 build configuration 文件：

+ `Config/UnrealBuildTool/BuildConfiguration.xml`

- `Engine/Saved/UnrealBuildTool/BuildConfiguration.xml`

- `<USER>/AppData/Roaming/Unreal Engine/UnrealBuildTool/BuildConfiguration.xml`

- `My Documents/Unreal Engine/UnrealBuildTool/BuildConfiguration.xml`

- `<PROJECT_DIRECTORY>/Saved/UnrealBuildTool/BuildConfiguration.xml`

其中最后一项是仅针对于项目的配置，推荐放到此处，避免对其他版本的引擎和项目造成影响。一个 `BuildConfiguration.xml` 大致内容如下（具体的配置项参考文档改动）：

```xml
<?xml version="1.0" encoding="utf-8"?>
<Configuration xmlns="https://www.unrealengine.com/BuildConfiguration">
    <WindowsPlatform>
        <CompilerVersion>14.36.32532</CompilerVersion>
    </WindowsPlatform>
</Configuration>
```

MSVC 的具体版本号可以在 `C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC` 路径下查看，每个版本的文件夹就是版本号。

另外，在[UE5编译报错：Error MSB3073 - 知乎](https://zhuanlan.zhihu.com/p/562697309)一文中，作者建议安装的是 14.29~14.31 版本，但目前 14.30.0~14.33.99999 已经被 UE 禁用，建议安装 14.36 ，否则在生成解决方案的时候会遇到以下报错：

> UnrealBuildTool has banned the MSVC 14.30.0-14.33.99999 toolchains due to compiler issues. Please install a different toolchain such as 14.36.32532 by opening the generated solution and installing recommended components or from the Visual Studio installer.

以及，与该博文评论区作者的回复不同，通过修改 `BuildConfiguration.xml` 进行 MSVC 版本指定是需要重新生成解决方案的。