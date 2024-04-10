---
title: amis相关
categories: 技术
tags:
  - 前端
  - amis
createDate: 2024-03-22 17:49:49
updateDate: 2024-03-22 17:49:49
---
onEvent中的ajax：使用event.data.result来取

combo默认不继承父级数据域，所以编辑器里上下文取不到其他combo里的数据，直接配置也会有setvalue导致的数据延迟，这个时候打开继承父级作用域变量即可。

picker打开后的弹窗大小直接通过配置size改变

picker初始化后不显示回显→1.后端接口要能通过id查询，picker会自己发请求查；2.后端返回的对象里包含labelField和valueField对应的字段，就能直接回显（推荐）

配置文件上传器
useChunk
修改下载文件名：修改api的headers

自定义js中，获取数据域使用event，context此时是获取组件实例


集合与异步
const array=Promise.all(list.map(async(item)=>{...}))


要在adaptor里写一句return response，event.data.responseResult里才有东西，status才有用，不为0的时候自动error toast msg