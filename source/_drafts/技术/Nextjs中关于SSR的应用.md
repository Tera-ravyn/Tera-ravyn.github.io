---
title: Nextjs中关于SSR的应用
categories: 技术
tags:
  - Nextjs
  - SSR
  - 前端
createDate: 2024-03-22 17:48:32
updateDate: 2024-03-22 17:48:32
---
## SSR概述
服务端渲染，顾名思义是在服务端渲染的。无法和任何需要在运行时获取的浏览器变量共同使用，包括 `window` 和 `localStorage` 。


## React支持与Next适配

### \<Suspense\>
基本使用：
```ts
<Suspense fallback={<JSX>}>
<Component />
</Suspense>
```
其中 `Component` 是一个异步执行的组件或直接使用了promise数据

```ts
 <Suspense fallback={<Spinner />}>

              {url === "" ? <b>-</b> : <b>{getData(url)}</b>}

            </Suspense> 
```
