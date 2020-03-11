# 逆向某网站的登录接口生成元素加密
> 由于是非法网站所以本文对网址进行了遮挡,但是其中的登录接口加密还是挺有意思的,故写下日志进行逆向,本文仅供参考!

## 逆向环境
* [![chrome]][chrome_url]
* [![charles]][charles_url]
* ![GitHub Pipenv locked Python version](https://img.shields.io/github/pipenv/locked/python-version/metabolize/rq-dashboard-on-heroku)
* [![pycharm]][pycharm_url]

## 登录接口解析
还是用我们的老套路,发送登录请求,获取登录的url,来看看参数加密情况

![post参数](https://img-blog.csdnimg.cn/20200311234628655.jpg)

`password`很明显这个参数加密了,作者这里输入了123456但是返回的却是一堆乱码,话不多说直接搜索看看登录的url看看是否能定位到请求代码处

![在这里插入图片描述](https://img-blog.csdnimg.cn/20200311234957962.jpg)

很快就找到了登录接口处

![在这里插入图片描述](https://img-blog.csdnimg.cn/20200311235028591.jpg)

由于该代码完全明文所以我们也非常容易能看出来代码的作用:
> 判断`isCrypt`是否为真,真的话调用cryptStr函数传入password参数,假则直接返回password,再加上下面的提交的`crypt`参数,小编猜想是否能提交的时候将`crypt`改为0,`password`直接传入明文是否能登录成功,通过charles发包后也证实了此观点,不过本文的目的是为了逆向学习交流分析,故作此下文

而我们的逆向思路也显而易见的出来了,在此处下个断点看看cryptStr函数是如何运行的,重新发送登录请求,成功的断下来了,F11跟进看看代码内部逻辑
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200311235751178.jpg)

下面是这段代码:

```javascript
    var cryptStr = function (val) {
        var temp = $("<div style='display:none;'><input class='cryptStr' type='password' name='password' /><button class='btnCrypt'>submit</button></div>");
        var cryptStrInput = temp.find(".cryptStr").val(val);
        temp.appendTo(document.body);
        temp.find(".btnCrypt").click();
        var cryptStr = cryptStrInput.val();
        temp.remove();
        return cryptStr;
    };
```
首先通过传入的参数可以很明显的看出来是我们输入的明文密码,然后我们逐句分析
* 首先第一行代码就是生成一个元素放入`temp`变量中
* 第二行代码则是定义一个`cryptStrInput`变量,定位生成的元素中`class=cryptStr`样式传入我们的`val`参数也就是我们的明文密码
* 第三行将此元素添加到`body`的最后一行
* 第四行找到`class=btnCrypt`样式进行点击
* 第五行定义一个变量`cryptStr`令它等于变量`cryptStrInput`里的值
* 第六行删除`temp`元素
* 第七行返回`cryptStr`

分析完逻辑后很明显的看出来,有一段代码调用了点击函数然后用加密函数在里面进行加密,至于为什么程序员要大费周章的这样生成元素来进行加密而不是直接在`cryptStr`函数编写加密代码段呢?理由也十分简单,因为这样的话内存调用栈也就追踪不到关键加密函数,这是对逆向十分头疼的.但是我们前面分析了关键在于click了btnCrypt,然后调用函数.正所谓办法总比困难多,我们可以在宇宙第一的chrome浏览器中查看监听事件,看看click指向了那里的函数

![在这里插入图片描述](https://img-blog.csdnimg.cn/20200312005254947.jpg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3E2Mzc4NTYx,size_16,color_FFFFFF,t_70)

可以很明显的看到click只有一个函数参与调用了,不出意外这里面就是关键的加密代码,点进去看看

![在这里插入图片描述](https://img-blog.csdnimg.cn/20200312005553848.jpg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3E2Mzc4NTYx,size_16,color_FFFFFF,t_70)
到这里也就十分容易分析了,首先获取明文密码,然后获取cookie中的`randomYes`的值,如果密码中已经包含了`randomYes`值说明已经加密过了所以直接返回,下面则是判断三个cookie是否存在,存在就传入到`sessionCookie`变量中,后面的代码如下

```javascript
sessionCookie = sessionCookie || "undefined";
var randomId = encrypt(cryptStr,sdc(sessionCookie + randomYes));
$(".cryptStr").val(randomId + randomYes);
```
定义`randomId`变量,然后调用`encrypt`函数传入两个参数,一个是明文密码,另一个则是sdc函数将`sessionCookie + randomYes`进行加密返回值,很明显的看出加密函数是AES加密,模式为ECB模式,填充为Pkcs7方式填充(**不熟悉AES加密的同学此时可以百度一下获取新知识,这里不过多描述**)然后传入`text`参数,以及密钥`secKey`,加密完后到文本返回加密后的数值.至于sdc函数小编点进去看了一眼并没有看出个所以然来,所以待会写python登录的时候只能将直接调用JS文件中的sdc函数进行生成(**希望以后回来看自己文章能明白sdc函数的加密方式是什么,当然也可以大牛上github来一起研究看看是什么方式的加密**).

## 总结
理顺了具体的加密逻辑后写python登录也基本上没什么难度了,有兴趣看的同学可以上我的github一起学习交流,本网站逆向主要有两大点需要注意
1. 当Call Stack追踪不到我们想要的函数时候怎么办?需要从多方面角度分析,办法总比困难多,除非是不存在的代码我们才追溯不到本源!
2. 遇见了陌生的函数,这在逆向中是十分需要警惕的一件事,当你对加密函数看不懂的时候就代表你逆向出现了障碍,逻辑效率等方面都会出现偏差,sdc函数可能只是改了个名的常用加密方式,但是小编并没有看出来,这是十分不应该的,就算是网站程序员自己写的加密函数也应该一步步去分析其逻辑,但是本网站的加密方法已经禁止了你进行动态调试,追踪这条路自然也无从下手!希望能有大佬站出来为小弟排忧解难
* **顺带一提**,本文分析后的py文件已经放入github中,有需要一起学习分析的同学可以上github查看

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


