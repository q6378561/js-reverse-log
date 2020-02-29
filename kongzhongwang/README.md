# 空中网登录逆向
> 空中网登录逆向相对来说难度不高,但是也有碰到许多坑,故写下此日志记录爬坑

## 逆向环境
* [![chrome]][chrome_url]
* [![charles]][charles_url]
* ![GitHub Pipenv locked Python version](https://img.shields.io/github/pipenv/locked/python-version/metabolize/rq-dashboard-on-heroku)
* [![pycharm]][pycharm_url]

## 接口解析
空中网的登录接口采用目前少见的get请求来设置cookie登录,但其中参数是有加密的,我们此次的目标就是逆向出其中的加密方式,首先我们来看一下登录get请求中需要的参数

<img src="https://s2.ax1x.com/2020/02/26/3UxDfK.png" width=600 align=center>

可以见到基本的参数是显而易见的,`username`也没有加密,只有`password`和`_`两个参数是我们需要探讨的东西

这时候的思路一般往两个方面衍生,1.通过监听事件调试跟进我们需要的加密函数 2.搜索关键词找到我们需要的加密函数   鉴于关键词越不偏僻越不好搜的原则我们这里采用监听事件 可以很容易定位到我们想要的关键函数

<img src="https://s2.ax1x.com/2020/02/26/3aCCP1.png" width=600 align=center>

我们在此函数下个断点更进看看有什么收获.

<img src="https://s2.ax1x.com/2020/02/26/3aCdGq.png" width=600 align=center>

F11不断跟进之后会发现我们来到了VM文件,**VM是浏览器为匿名函数创建的内存空间，是无法清除的。
匿名函数需要运行，首先需要有一块内存空间来存储它，这块内存空间显示在浏览器调试信息中就是以VM开头的文件（但是其实并非真正的文件）**。右下角可以看见文件真正的来源是另一个JS文件中的eval语句,这也是十分常见的一种JS加密方式,使用chrome浏览器的大括号展开可以得到可读的关键函数代码.

<img src="https://s2.ax1x.com/2020/02/26/3aP9eg.png" width=600 align=center>

可以发现login这个函数传入了很多参数 username,password等等 初步判断加密过程就在这里面,继续F11跟进找到关键代码

<img src="https://s2.ax1x.com/2020/02/26/3aPqnU.png" width=600 align=center>

经常逆向或者英语同学好的同学知道encrypt就是加密的意思,并且上下行代码也是之前所衔接的参数,所以这函数应该就是我们所需要的加密函数.此时我们可以选择python模拟加密过程进行加密,或者通过直接调用JS函数的方式来实现加密,为了节约时间我们使用第二种方式来进行加密.所以我们只要了解所需要传入的参数就OK,第一个显而易见是我们的密码,第二个则是j_data数据里面的dc变量,通过短暂的分析可以得到dc变量来自于上一个请求中的rep,所以我们传入python时获取上一个请求就能获得我们想要的DC变量.

到这里`password`的逆向已经结束了,剩下的`_`如果不逆向JS文件的话通过不断的发送请求可以看出是13位时间戮,逆向的话则可以看见`temptime`这个参数,简而言之就是不难拿到这个参数的值.

至此空中网的逆向就告一段落了.

## 后记(心得体会)
1. 小编一开始是用charles代理js文件来解密eval加密函数进行动态调试的,后面才发现原来强大的chrome浏览器有VM模式功能,算是一个小小的坑.
2. 通过python的requests库中的session会话来保持会话完全模拟从主页面到login等协议请求的cookie获取
3. 刚写完代码时,提交请求返回的是操作太过频繁,本以为是频繁恶意操作被banIP了,结果换了个IP代理发现还是这样,结合JS文件中对temptime的时间间隔判断(原JS文件只有间隔过长返回NULL的判断,间隔过段的判断应该是在后端,只是联想到了是否有这种可能).于是采用了python文件的time模块的sleep函数等待几秒发现status状态返回成功了.
4. 虽然可能看日志觉得逆向很快,但还是要一步一步慢慢调试,才获取到的这些信息

## 支持作者
喜欢我的话点一下下方的按钮哦!

![GitHub followers](https://img.shields.io/github/followers/q6378561?style=social)
![GitHub stars](https://img.shields.io/github/stars/q6378561/js-reverse-log?style=social)
![GitHub forks](https://img.shields.io/github/forks/q6378561/js-reverse-log?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/q6378561/js-reverse-log?style=social)

[chrome]: https://img.shields.io/badge/chrome-80.0.3987.122-ff69b4
[chrome_url]: https://www.google.com/chrome/
[charles]: https://img.shields.io/badge/charles-v3.11.2-brightgreen
[charles_url]: https://www.charlesproxy.com/
[pycharm]: https://img.shields.io/badge/pycharm-professional-red
[pycharm_url]: https://www.jetbrains.com/pycharm/

