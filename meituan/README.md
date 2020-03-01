# 逆向分析美团API参数
> 近年来由于python的兴起,爬虫等业务也随即火热起来,那么外卖电商等平台首当其冲是要被爬取的对象.于是一场爬虫与反爬虫的攻坚战就此展开.本文逆向美团外卖平台获取商品信息的加密参数来应对美团采取的反爬虫措施.

## 逆向环境
* [![chrome]][chrome_url]
* [![charles]][charles_url]
* ![GitHub Pipenv locked Python version](https://img.shields.io/github/pipenv/locked/python-version/metabolize/rq-dashboard-on-heroku)
* [![pycharm]][pycharm_url]

## 分析请求接口
老规矩,我们获取一次商品信息,然后看一看请求接口都包含了哪些东西
<img src="https://s2.ax1x.com/2020/03/02/32WJF1.png">

可以看见这个请求地址后面包含了很多参数,带着一样的参数重新发送请求会发现请求失败,所以这里后面的加密参数应该就是验证参数了.由于这样可读性过差我们在chrome上往下拉

<img src="https://s2.ax1x.com/2020/03/02/32WRl8.png">
这样可读性就高多了,我们可以通过参数的命名来分析每个参数具体的作用,上面的参数就不一一分析了,毕竟我们是带着研究的心态来分析美团的接口,而不是用于爬虫等其他用途.
重复刷新页面可以发现,唯一变的值只有`_token`这个参数,说明它用于验证请求等操作.于是我们打开chrome的调试窗口 ctrl+shift+f搜索API开头的`getPoiList`这个路由,很快就能定位到我们想要的地方
<img src="https://s2.ax1x.com/2020/03/02/32fY7j.png">
可以发现美团的程序员比想象中的亲切,代码可读性并不低,可以看见`_token`参数来自于变量d,而变量d又来自于`d = window.Rohr_Opt.reload(p);`,于是我们在这一行下个断点跟进看看是怎样进行加密的,重新刷新网页可以发现成功断下,F11跟进看一看
<img src="https://s2.ax1x.com/2020/03/02/32fR41.png">

`jv = "https://sm.meituan.com/meishi/api/poi/getPoiList?cityName=三明&cateId=17&areaId=0&sort=&dinnerCountAttrId=&page=1&userId=&uuid=fbc5a9a6120f4893bb27.1583068822.1.0.0&platform=1&partner=126&originUrl=https://sm.meituan.com/meishi/c17/pn1/&riskLevel=1&optimusCode=10"`

可以发现传入的jv就是不带_token参数的path,继续跟进看看
<img src="https://s2.ax1x.com/2020/03/02/32hdVH.png">

首先开头代码创建了jw和jx两个变量,然后判断了传入jv变量的类型,`_$_543c[91]`是美团自己弄的一个数组,其中对应的值是string,所以这个if判断了jv是否为文本类型,如果是的话进行parse操作,由于时间有限这里的parse函数我们就不加以分析了,总结就是将传入的文本变为对象传入到jx里面,然后`iP.sign = iJ(jx);`然后传入jx进行iJ函数的加工,因为很关键所以我们还是要跟进去看一看.
<img src="https://s2.ax1x.com/2020/03/02/324Eod.png">

分析后就是将传入的je变量对象中的key值进行sort函数排序,然后将重新排序好的对象传入jd中生成相对应的文本值,图中也可以看到jd的内存.然而还要将生成的jd值通过iI函数加工,F11跟进看看
<img src="https://s2.ax1x.com/2020/03/02/324uSP.png">

首先`JSON.stringify`函数可以将传入的JSON对象变为字符串,然后忽视前面cD函数看到deflate,经常进行爬虫或者熟悉网页压缩的同学可能懂,deflate是一种压缩算法,
观察接口的头部也能发现deflate就在其中
<img src="https://s2.ax1x.com/2020/03/02/3242Sx.png">

那么我们可以默认待会调用python的时候可以直接调用python的压缩算法库,如果出错了可以继续分析cD函数.将jc进行压缩后,会发现把他传入到iD函数中
先直接跳过iD函数,我们发现jc的值在内存中为
<img src="https://s2.ax1x.com/2020/03/02/32450e.png">

由此我们可以断定,iD函数就是我们想要的加密函数,然而F11跟进去会发现这个函数十分复杂,笔者逆向了一会发现无果,便查阅了网络上的相关资料,网络上的思路通过token结尾的=号猜测是base64加密,decode后返回的是十六进制的ASCii码,考虑原数据可能进行二进制压缩+编码，使用python zlib库对byte数据进行解压.
<img src="https://s2.ax1x.com/2020/03/02/325qUJ.png">

get到加密方式后我们先忽视这里的数据,继续进行逆向
<img src="https://s2.ax1x.com/2020/03/02/32I9bD.png">

我们发现ip的参数和我们前面解压的数据一模一样,由此可以断定ip就是我们加密前的参数,搜索rId,看看我们是否能得到想要的参数传入.

<img src="https://s2.ax1x.com/2020/03/02/32IuqS.png">

至此逆向基本就结束了,我们只要分析每个参数的数值以及对应的函数后写入Python中实现获取美团商品信息,通过不断请求发现只有四个参数是在变动的
`ts``cts`这两个值很明显的可以看出是获取时间戳,写入python的时候直接调用time库就行,`bI`则是返回两个参数,第一个是打开网页的来源网址referer,第二个则是当前网页的地址,也就是说我们变动当前网页的网址参数就OK了,第四个则是`sign`,这个参数其实我们前面就分析过了,就是将未带有token参数的Url进行加密.

## 总结
1. 对网页压缩的三种算法:①gzip②deflate③br有了更深的了解
2. 对编码转化等理解不够透彻,有关的知识点有**base64**编码解码,**二进制流**的压缩与解压
3. 未能践行**大胆猜测,小心求证**的逆向思想,如果仔细观看token的末尾可以先尝试base64解码,逆向过程过于死板不够灵活,需要更多的练习以及获取更多相关的知识

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
