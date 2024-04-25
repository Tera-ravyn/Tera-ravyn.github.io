---
title: UE5 - pawn移动相关
categories: 技术
tags:
  - UE5
date: 2024-04-08 09:38:21
updated: 2024-04-08T18:00:00
---

## 前言

使用版本为 UE5.2。
本文主要对目前完成的 base pawn 的移动实现做个记录，主要基于 `floatingPawnMovement` 与 `enhancedInputSystem` 实现。因为业务需要，目前都是第一人称视角的内容，纯蓝图。主要针对获取玩家控制器后移动的实现，controller 和 gameMode 的前置部分省略。
UE5 迁移到论坛上的文档查起来极其麻烦，大量内容仍然是 4.0+的内容，api 的介绍也不比引擎内详细（说白了就是光看 description 根本看不懂怎么用），只能摸着石头过河了，使用不一定是最优解，欢迎任何指导。

## 一、准备工作

在 5.2 之后轴和操作映射已经被废弃，推荐使用增强输入系统(Enhanced Input System)，该系统现在除了本地子系统(local subsystem)外还有个实验性质的场景子系统，暂且不探讨。现在 UE 自带的几个模板都使用了这套增强输入系统，所以使用系统所需要的配置都是默认开启的，不需要额外配置。如果是空白新项目，可以检查一下插件中的 `Enhanced Input` 是否已经开启，以及项目配置中的引擎-输入-默认类是否都切换到了 `Enhanced Input` 相关类。

![](IMG-20240415092908311.png)
![](IMG-20240415092908363.png)
另外需要注意的是，pawn 组件同样需要本身拥有移动组件(Movement Component)才能够被增强输入系统应用，Character 自带有 CharacterMovementComponent，defaultPawn 自带有 FloatingPawnMovement。

## 二、 输入操作(Input Action)

新建蓝图，在`输入`中可以找到`输入操作`的蓝图类。

![](IMG-20240415092908400.png)
简单情况下，其实没有什么需要变动的，主要是配置`操作` - `值类型`。按键是否按下等是非值使用 `Boolean` ，滚轮等一维线性值使用 `Axis1D` ，移动根据轴向数量使用 `Axis2D` 或 `Axis3D` 。

![](IMG-20240415092908429.png)
关于更详细的 IA 部分内容，以下摘录知乎用户 @牵线木偶 的[整理](https://zhuanlan.zhihu.com/p/615553951)，感谢他的工作。

#### InputAction 字段功能介绍

<details><summary>
展开查看全部
</summary>

1. **Consume Input**：是否阻止事件向低优先级的 Action 传递。勾选 Consume Input 时只有高优先级的 IA2 会触发，IA1 被阻止不会触发。只有取消勾选 Consume Input，同时勾选 Reserve All Mappings 字段时，在 IA2 触发后 IA1 才会触发。
2. **Trigger when Paused**：通过 SetGamePaused 暂停游戏之后是否可以触发，勾选暂停时也可以触发。
3. **Reserve All Mappings**：是否恢复被覆写的低优先级 InputAction。不勾选时，两个绑定了相同输入的 InputAction，低优先级的 InputAction 会被高优先级的覆写，导致按下触键时不会触发。勾选取消覆写。
4. **Value Type**：事件的数据类型，分别为布尔型、一维(鼠标滚轮等)、二维(摇杆数据等)与三维(飞行模拟手柄等)。
5. **Triggers**：InputAction 的触发器类型。</details>

#### 不同的 Trigger 的触发逻辑与事件类型

在 InputAction 中设置 Triggers 与在 InputMappingContext 中设置具有相同的作用。
在 InputAction 中与 InputMappingContext 中均设置 Triggers 时，只有 InputMappingContext 中的 Triggers 会起作用。
多个 Trigger 之间是或的关系。

<details><summary>
展开查看全部
</summary>

1. **None**：此时使用的是 Down 类型
   按下按键触发 Started
   保持按下会不断触发 Triggered 事件
   松开按键触发 Completed
2. **Pressed**：
   按下按键依次触发 Started、Triggered 与 Completed，松开按键不触发任何事件。
3. **Down**：可用于机枪的连续射击，Started 开始射击，Completed 停止射击，Triggered 检查弹夹。
   按下按键触发 Started 事件
   保持按下会不断触发 Triggered 事件
   松开按键触发 Completed 事件
4. **Hold**：
   - IsOneShot 没有勾选时：可用于按下保持一段时间，松开才会触发的动作。如吃鸡里手雷投掷。
     按下按键触发 Started，保持按下不断触发 Ongoing，松开时如果保持的时间达到或超过 HoldTimeThreshold 设置的时间则触发 Completed，否则触发 Canceled。
   - IsOneShot 勾选：用于按下保持一段时间后自动触发的动作，如 CS 里拆包。
     按下按键触发 Started，保持按下不断触发 Ongoing，在达到 HoldTimeThreshold 设置的时间前松开触发 Canceled。保持按下达到 HoldTimeThreshold 设置的时间后会依次触发 Triggered 与 Completed。
5. **HoldAndRelease**：与 Hold 类型不勾选 IsOneShot 类似。
   按下按键触发 Started
   保持按下不断触发 Ongoing
   松开按键时如果保持的时间达到 HoldTimeThreshold 设置的时间会依次触发 Triggered 与 Completed，否则触发 Canceled。
6. **Pulse**：用于保持按下时每隔一段时间触发一次的动作。如按下吃药键，每隔一段时间执行一次吃药的动作
   按下时触发 Started 事件
   如果勾选 TriggerOnStart 则立即触发一次 Triggered 事件，不勾选则间隔一段时间后触发 Triggered。
   保持按下触发 Ongoing 事件。
   距上一次 Trigger 的时间间隔达到 Interval 设置的时间触发一次 Triggered 事件，随后判断 Trigger 触发的数量是否达到 TriggerLimit 的限制(TriggerLimit&lt;=0 表示不限制次数)，未达到则继续上一步，否则触发 Completed。
7. **Release**：作用与 Down 类似
   按下时触发 Started 事件
   保持按下触发 Ongoing 事件
   松开时依次触发 Triggered 与 Completed
8. **Tap**：
   按下按键触发 Started 事件
   保持按下触发 Ongoing 事件
   如果保持的时间超过 TapReleaseTimeThreshold 设置的时间触发 Canceled 事件。
   松开按键时保持的时间小于 TapReleaseTimeThreshold 设置的时间依次触发 Triggered 与 Completed 事件。
9. **Chorded Action**：用于多个 Action 的串联形成组合键。
   触发的事件类型与 Chorded Action 下拉选择的 Action 相同。
10. **Combo**：用于类似上上下下左右左右 BABA 在短时间内完成的组合键。
按下第一个键触发 Started
过程当中不断触发 Ongoing
如果某个键按下的时间没有达到 TimeToPressKey 或者按错键触发 Canceled
当所有的键完成后依次触发 Triggered 与 Completed
</details>

## 三、 输入映射上下文(Input Mapping Context)

新建蓝图，在`输入`中可以找到`输入映射上下文`的蓝图类。
在`映射`中，可以选择已经创建的输入操作。选择完毕后就可以开始将需要的控制绑定添加到操作映射。触发器的字段同输入操作中的内容，修改器的内容用于调整映射。

![](IMG-20240415092908465.png)

### 移动操作

本文的移动操作包含 XYZ 三轴，分别对应 AD、SW、QE。将所有需要的键都添加控制绑定，并且使用修改器调整它们的绑定轴方向。
在默认情况下，所有键的值都映射到 X 轴。使用 `拌合输入轴值` ，在 `排序` 中可以自定义交换轴或轴的顺序。YXZ 排序将 XY 轴值交换，即可将值映射到 Y 轴，同理排序改为 ZYX 即可映射到 Z 轴。
除此以外，轴的 `否定` 值即往轴的反向移动，需要为 ASQ 键增加该修饰器。

![](IMG-20240415092908494.png)

### 环视操作

环视本身是通过获取鼠标 XY2D 轴并将其添加到控制器的 Yaw 和 Pitch 轴来实现视角转动的。由于我们希望在按下右键时才触发视角转动，所以需要另外增加一个输入操作来监听鼠标右键是否触发，并且将它作为环视操作的触发器。这里用到的是 Chorded Action，只有当所有前置输入操作都满足条件时才会触发。
鼠标 XY2D 轴本身 Y 是反向的，所以还要记得应用 `否定` 并仅勾选 Y 轴。

> “弦操作”这个翻译我个人觉得比较莫名其妙，虽然 chord 可以指通过多点的直线，但这里的 chorded 应该和 chorded keyboard 的语境更相似，也就是从和弦的概念引申过来的，同时多个事件串联才能触发。不过 chorded 这个词确实也没有更好的翻译，弦或和弦，nevermind（摊手）

![](IMG-20240415092908527.png)
完成以上控制绑定后，映射部分就完成了，接下来需要在 pawn 的蓝图内调用。

### 所有修改器(modifier)的功能列表

<details><summary>展开查看更多</summary>

- **到世界空间(To World Space)**：输入空间到世界空间转换。自动将输入操作值中的轴转换为世界空间，允许将结果直接插入到采用世界空间值的函数中。
- **否定(Negate)**：反转每个轴的输入。
- **响应曲线 - 指数(Response Curve – Exponential)**：将简单的指数响应曲线应用于每个轴的输入值。
- **响应曲线 - 用户定义(Response Curve – User Defined)**：将自定义响应曲线应用于每个轴的输入值。
- **平滑(Smooth)**：平滑多个帧的输入。
- **拌合输入轴值(Swizzle Input Axis Values)**:：可用于将 1D 输入映射到 2D 操作的 Y 轴上。
- **按差量时间缩放(Scale by Delta Time)**：将输入值乘以此帧的增量时间。
- **标量(Scalar)**：按每个轴的设定因子缩放输入。
- **盲区(Dead Zone)**：LowerThreshold -> UpperThreshold 范围内的输入值将从 0 -> 1 重新映射。超出此范围的值将被钳制。
- **视野缩放(FOV Scaling)**：将 FOV 相关缩放应用于每个轴的输入值。

</details>

## 四、pawn 调用增强输入系统

首先在 `begin play` 从控制器获取增强输入系统，并且在映射上下文中选择之前编辑好的蓝图类。

![](IMG-20240415092908554.png)
此后可以直接获取到映射完成的输入，如上文添加的 `IA_Move` 。
获取轴值后有两种输入移动的方式：

1. `AddMoveInput`
   使用 `AddMoveInput` 的情况下，移动速度应用 Pawn 组件里设置的速度、加速度、减速度，无法灵活修改速度。如果你的`AddMoveInput`不生效，请点击下面第二条内容中的展开。
2. `MoveUpdatedComponent`
使用 `MoveUpdatedComponent` 的情况下，可以自由设置移动速度。该函数本身按给定差量移动。需要注意的是因为此时直接按照输入的向量移动，因此没有缓动，需要缓动的话需要自己再配置弹簧臂和摄像机，然后在挂载摄像机的 springArm 上勾选摄像机延迟。
这个方法最有用的地方是用滚轮前进后退模拟视角缩放以及拖拽移动。
<details>
<summary>
不要自己模拟Pawn的缓动运动，我是傻逼所以我干了，并且干得稀烂。

</summary>

其实是因为一开始到处乱试的时候，把加速度调成了 1，导致启动过慢，我以为没在动，就觉得 `Add Move Input` 不适用，真是傻傻又逼逼啊。

</details>

![](IMG-20240415092908580.png)
![](IMG-20240415092908606.png)
Look 的输入值添加到控制器的 Yaw 和 Pitch 轴中即可，如果没有生效请检查 Pawn 组件本身有没有开启。

![](IMG-20240415092908631.png)
![](IMG-20240415092908655.png)

### 结语

`EnhancedInputSystem` 主要优势还是为监听封装了更多的状态，便于完善状态机的执行。
如果想要从代码层面更加了解增强输入系统，推荐：[UE5 -- EnhancedInput(增强输入系统) - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/470949422)

---

## references

[Unreal Engine: Enhanced Input Actions (Keyboard + Controller) - GameDev EXP](https://gamedevexp.com/unreal-engine-enhanced-input/#:~:text=To%20get%20this%20working%2C%20you%20will%20always%20need,the%20Mapping%20Context%20you%20created%20in%20Step%203.)
[UE5 InputAction 使用手册 - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/615553951)
[UE5.2 实操 1-增强输入 - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/640271313)
