---
title: antd-mobile使用记录
categories: 技术
tags:
  - antd-mobile
  - 前端
---

### sticky不生效的tabs
当tabs.tab包裹children的时候，sticky实际无法生效。直接用sticky只在外面包一层的话，是不生效的，因为sticky的父元素需要也是sticky。但是全部sticky后，tab和tabs会一起被黏住。官方样例里的sticky要么是一整片的定位，实际上没有tab区的重渲染，要么是用了swiper（tab区域也没有重渲染）。
所以想要实现导航tab的sticky只能使用Swiper，用ref传给tab。

