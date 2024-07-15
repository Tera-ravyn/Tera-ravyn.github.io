---
title: antd-mobile的tab、swiper与滚动长度
categories: 技术
tags:
  - antd-mobile
  - tailwind
date: 2024-05-20 11:26:20
updated: 2024/05/20 18:06:55
cover:
date: 2024/05/20 11:26:20
---
## 前言

但不得不说，官方的 Tab 组件着实难用。样式难以替换，自带的 sticky 使用极为不便。FAQ 中这样说：

> Q: Tabs 是否支持 sticky 吸顶效果？
> 
A: 支持，但是 Tabs 并没有一个类似于 `sticky` 的属性。你可以自己在 Tabs 的外层容器中增加一下 `position: sticky` 的 CSS 样式，从而实现吸顶效果。

然而当 `tabs.tab` 包裹 children 的时候，直接用 sticky 只在外面包一层的话，依旧无法生效，因为 sticky 的父元素需要也是 sticky。但是为父级元素也添加 sticky 后，tab 和 tabs 则会一起被黏住。官方样例里的 sticky 要么是一整片的定位，实际上没有 tab 区的重渲染，要么是用了 Swiper（tab 区域也没有重渲染）。

所以目前就实测有用的实现导航 tab 的 sticky 方法，只有使用 Swiper，用 ref 传给 tab。

## Tab 与 Swiper 的结合

关于 Swiper 和 Tab 组件结合使用的方法，官方的文档有提供 demo：

不过个人感觉是没有长条自动滚动的需求的话，还不如自己手写一个 flex 然后统一进行状态管理方便。

## Swiper 的滚动条……

按照官方的用法写好 Swiper，开始往里面填充内容的时候，相信你很快就会发现一个问题：怎么后面还没写的空白内容也有这么长的滚动条？

是的，因为Swiper 本身就是一饼粘连，页面初始化的时候就给你全加载完了， Swiper 整个组件被内容撑开后，所有页面都共享同一个组件高度。如果每个页面都是无限下拉或者开启了虚拟滚动，也许这个问题还算无伤大雅，但是等待加载/页面偏短各种情况总可能使得这个小问题显得比较尴尬，所以解决一下。

解决方案，就是直接让 swiper 本身的高度被固定，而让被放在 Swiper 里面的内容滚动。