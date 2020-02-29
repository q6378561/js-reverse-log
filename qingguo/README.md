![pic](https://s2.ax1x.com/2020/02/17/3i0Pwq.jpg)
# 逆向青果软件有限公司外包的教务系统登录接口
> 很早以前为了抢课就研究过学校的登录接口,当时刚碰JS遇到了许多坑,故记下此篇造福人类,也让自己复习一遍,完整的代码可以点此仓库的py文件模拟登录,但希望点进来观看的你看了此篇教程能有一点点收获就是乱舞神菜最大的荣幸!

## 逆向环境
* [![chrome]][chrome_url]
* [![charles]][charles_url]
* ![GitHub Pipenv locked Python version](https://img.shields.io/github/pipenv/locked/python-version/metabolize/rq-dashboard-on-heroku)
* [![pycharm]][pycharm_url]

## POST请求解析
研究登录接口的第一件事就是对登录的post的请求进行解析,看看传入的参数是否加密以及是否有多余的参数.如果没有,那么恭喜你这篇教程不用看了,直接对明文参数进行post进行登录研究.

<img src="https://s2.ax1x.com/2020/02/17/3i0vAx.jpg" width=600 align=center alt="操作前不要忘记勾选上面的 Preserve log">

首先我们F12打开开发者工具,点NETWORK查看相关的请求,我们先随便输入账号密码和验证码点击登录.

<img src="https://s2.ax1x.com/2020/02/17/3i0OBR.jpg" width=600 align=center>

可以很明显的看出来 http://jwgl.bsuc.edu.cn/bsxyjw/cas/logon.action  这个接口就是我们要研究的登录接口,当然其中的data数据也是进行了加密.

<img src="https://s2.ax1x.com/2020/02/17/3iwHeI.jpg" width=600 align=center alt="加密的参数">

## data参数解密过程
逆向JS的方向有很多,例如ctrl+shift+f调用搜索窗口搜params,token这些加密参数,或者对按钮单击事件下断点逆向分析数据等等,笔者这里采用此接口逆向较全面的从按钮处下断点

<img src="https://s2.ax1x.com/2020/02/17/3iwqTP.jpg" width=600 align=center alt="监听事件">

右键按钮审查元素定位登录按钮在html中的位置,点击右边的Event Listeners将Ancestors all的选项取消,这样就能单独监听按钮的事件,点击click，发现定位到一处代码之中,跟过去看看。

<img src="https://s2.ax1x.com/2020/02/17/3iwbwt.jpg" width=600 align=center alt="鼠标单击事件">

此时已经定位到按钮事件的单击事件中,我们在左边的行数字那里单击一下就能下断点.再重新提交一次请求看看能不能被断下.

<img src="https://s2.ax1x.com/2020/02/17/3iwOFf.jpg" width=600 align=center alt="断点">

很明显此时已经被断下了,我们用F11单步步入进去看有关于如何处理本次按钮事件的有关函数.

<img src="https://s2.ax1x.com/2020/02/17/3iwXY8.jpg" width=600 align=center alt="相关函数">

值得庆幸的事,也是让笔者当初有动力逆向的地方就在于这个接口的JS都是明文没有加密,这也就有助于我们的逆向过程.可以很明显的看到程序员给我们的注释第一个函数是用于输入信息验证的,跟我们想要的params等参数无关,所以直接F10步过.此时来到了
var username = j$("#yhmc").val();

这里,可以很明显的看出来这里是JQUERY的代码,val函数用于取id为yhmc元素里面的值.结合html分析可以很明显的看出来username就是我们输入的账号,以及下面几个变量。

`password` 密码

`token` 还是密码("说明等下要将密码进行加密加工变为token")

`randnumber` 验证码

`passwordPolicy`为了节省时间就不对此变量的函数进行分析了,总结就是判断密码是否符合密码策略,不符合返回0,符合返回1,后续我们模拟登录的时候可以下死码令他直接等于1

`url` 当然是我们登录接口的API啦,用于POST用的~

`txt_mm_expression` `txt_mm_length` `txt_mm_userzh`这三个变量都是从网页上获取的,都是死码,分别是8,6,0(我们也可以直接获取网页的文本来填写这个三个参数,由于比较麻烦笔者就不这样做了)

接下来我们就发现开始对这些变量进行加密了
```
passsword = hex_md5(hex_md5(password)+hex_md5(randnumber.toLowerCase()));
```
这段代码显而易见,首先对密码进行md5加密,再对取小写的验证码进行MD5加密,两个相加的文本再进行MD5加密放入变量password中

<img src="https://s2.ax1x.com/2020/02/17/3iwxSg.jpg" width=600 align=center alt="函数分析">

继续进行分析

`p_username`就是文本_u加上验证码

`p_password`就是文本_p加上验证码

```angular2
username = base64encode(username+";;"+_sessionid);
```
这段代码就是用户名文本加上;;再加上_sessionid(这个变量从何得来呢,ctrl+shift+f搜一下发现他就在主页中,应该是每次访问随机生成的那种)三者相加进行base64加密.

```angular2
var params = p_username+"="+username+"&"+p_password+"="+password+"&randnumber="+randnumber+"&isPasswordPolicy="+passwordPolicy+
	             "&txt_mm_expression="+txt_mm_expression+"&txt_mm_length="+txt_mm_length+"&txt_mm_userzh="+txt_mm_userzh;
```
很明显,就是讲前面几个变量相加变为params
然而我们的逆向分析还没有结束,我们请求中的token很明显是经过加密的,但是逆向分析到此时token还是等于password,于是我们继续逆向

`params = getEncParams(params); `
很明显,getEncParams这个函数才是加密了token，params这些参数的地方,我们F11单步步入进去看看.

<img src="https://s2.ax1x.com/2020/02/17/3iwzlQ.jpg" width=600 align=center alt="函数分析">

很明显这里就是进行综合加密的地方了,data里面的三个数据这里都有,我们一一分析看看.

`var timestamp = _nowtime;` 这里的文本由 `_nowtime`变量传入,ctrl+f搜索此变量发现就在此jsp文件的顶部,对应的是我们请求的提交时间.

`var token = md5(md5(params)+md5(timestamp)); `这里的数据比较明显,就是将params进行md5加密加上时间戮进行md5加密的和再进行md5加密就是我们要的token了.

`var _params = b64_encode(des_encode(params)); `我们发现这段代码要先经过des_encode后返回的文本再进行base64加密

<img src="https://s2.ax1x.com/2020/02/17/3i0Syj.jpg" width=600 align=center alt="函数分析">

F11单步步入点进去看看,我们发现这个网站的程序员确实差点意思,写的都是一层套一层循环嵌套,再F11单步步入进入strEnc这个函数看看.

<img src="https://s2.ax1x.com/2020/02/17/3i0pOs.jpg" width=600 align=center alt="函数分析">
<img src="https://s2.ax1x.com/2020/02/17/3i0Cmn.jpg" width=600 align=center alt="函数分析">

程序员已经给我们备注了是des加密了,所以我们也就不必进行分析,此时我们有两种选择,一种是直接复制调用这段JS进行加密,另一种则是直接python调用des加密模块进行加密,由于不清楚程序员是否修改了des的加密方式故我们直接采用调用js的加密方式确保不会出错.
分析到这里我们只要再回头看看对des传入了哪些参数就能解密出来了.

`function des_encode(data) { return strEnc(data, _deskey, null, null); }`
很明显data传入的是我们的params,那这个_deskey是什么?,通过ctrl+f搜索发现同样在这个jsp文件顶部,由于_deskey的加密方式搜不到,分析也十分难分析,故笔者这里采用直接获取jsp文本的方式获取这两个变量:
```
url = "http://jwgl.bsuc.edu.cn/bsxyjw/custom/js/SetKingoEncypt.jsp"
rep = self.__session.get(self.url, headers=HEADERS)
_deskey = re.search(r"var _deskey = '(.*?)';", rep.text).group(1)
_nowtime = re.search(r"var _nowtime = '(.*?)';", rep.text).group(1)
```
到这里我们的解密工作也就告一段落了.

## 调用js
剩下的小难点就是调用js了,我们可以利用execjs这个库来调用js:
```
def get_js():
    # f = open("D:/WorkSpace/MyWorkSpace/jsdemo/js/des_rsa.js",'r',encoding='UTF-8')
    f = open("demo01.js", 'r', encoding='UTF-8')
    line = f.readline()
    htmlstr = ''
    while line:
        htmlstr = htmlstr + line
        line = f.readline()
    return htmlstr
jsstr = get_js()
ctx = execjs.compile(jsstr)
ctx.call('strEnc', parms, _deskey)
```

## 后续
剩下的就是获取相关的url,构造相关的请求头,以及python调用md5加密和base加密等操作,利用requests库的session来保持会话就能实现我们的模拟登录了.

<img src="https://s2.ax1x.com/2020/02/17/3iwwJU.jpg" width=600 align=center alt="发送请求">

## 总结
此次逆向说难不难说简单不简单,算是对新手来说是很方面的加密了,但是综合性很强,我们需要分析协议,下断点,分析js代码,甚至利用正则表达式,好在js代码是明文这让我们的逆向工作简单了很多,希望各位看到这边文章能有所收获,共同进步!

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
