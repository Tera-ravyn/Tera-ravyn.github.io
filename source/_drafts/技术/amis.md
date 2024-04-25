---
title: amis相关
categories: 技术
tags:
  - 前端
  - amis
date: 2024-03-22 17:49:49
updated: 2024-03-22 17:49:49
---

onEvent 中的 ajax：使用 event.data.result 来取

combo 默认不继承父级数据域，所以编辑器里上下文取不到其他 combo 里的数据，直接配置也会有 setvalue 导致的数据延迟，这个时候打开继承父级作用域变量即可。

picker 打开后的弹窗大小直接通过配置 size 改变

picker 初始化后不显示回显 →1.后端接口要能通过 id 查询，picker 会自己发请求查；2.后端返回的对象里包含 labelField 和 valueField 对应的字段，就能直接回显（推荐）

配置文件上传器
useChunk
修改下载文件名：修改 api 的 headers

自定义 js 中，获取数据域使用 event，context 此时是获取组件实例

集合与异步
const array=Promise.all(list.map(async(item)=>{...}))

要在 adaptor 里写一句 return response，event.data.responseResult 里才有东西，status 才有用，不为 0 的时候自动 error toast msg
