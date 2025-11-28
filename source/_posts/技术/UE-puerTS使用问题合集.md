---
title: UE-puerTS使用问题合集
categories: 技术
tags: 
date: 2025-11-20 10:59:50
updated: 2025-11-20 10:59:50
cover:
---
## 无法正确初始化 Puerts

在正确安装（迁移）、没有缺少文件、插件列表中能正常看到 Puerts 的情况下，log 中有 mounting puerts 的提示，但运行 puerts 相关命令会报 Puerts command not initialized。

[Bug: Engine not generating Blueprints from TS · Issue #2142 · Tencent/puerts](https://github.com/Tencent/puerts/issues/2142)

![](IMG-20251128153843833.png)

## 运行时报错：无法定位程序输入点于动态链接库

dll 文件有问题，重新下对应版本的 puerTS 并且替换报错的 dll。

## 打包时报错 Bug: error: no template named 'result_of'

这是asio的c++20兼容性问题。  
可以在JsEnv.Build.cs指明使用c++17编译。

```cs
    public JsEnv(ReadOnlyTargetRules Target) : base(Target)
    {
#if UE_5_3_OR_LATER
        PCHUsage = PCHUsageMode.NoPCHs;
        CppStandard = CppStandardVersion.Cpp17;
#endif
```

[[UE] Bug: error: no template named 'result_of' · Issue #1649 · Tencent/puerts](https://github.com/Tencent/puerts/issues/1649)
