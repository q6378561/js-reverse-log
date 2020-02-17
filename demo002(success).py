import requests
import re
import hashlib
import base64
import execjs

def MD5_HEX(str):
    m = hashlib.md5()
    b = str.encode(encoding='utf-8')
    m.update(b)
    str_md5 = m.hexdigest()
    return str_md5

def get_js():
    # f = open("D:/WorkSpace/MyWorkSpace/jsdemo/js/des_rsa.js",'r',encoding='UTF-8')
    f = open("demo01.js", 'r', encoding='UTF-8')
    line = f.readline()
    htmlstr = ''
    while line:
        htmlstr = htmlstr + line
        line = f.readline()
    return htmlstr

class UESTC(object):
    image_url = "http://jwgl.bsuc.edu.cn/bsxyjw/cas/genValidateCode?dateTime=Sat"
    url = "http://jwgl.bsuc.edu.cn/bsxyjw/custom/js/SetKingoEncypt.jsp"
    login_url = "http://jwgl.bsuc.edu.cn/bsxyjw/cas/logon.action"
    loginafter_url = "http://jwgl.bsuc.edu.cn/bsxyjw/MainFrm.html"
    def __init__(self,username,password):
        self.__session = requests.session()
        self.username = username
        self.password = password

    def login(self):
        HEADERS = {
            'Host': "jwgl.bsuc.edu.cn",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36 LBBROWSER",
            'Accept': "image/webp,image/*,*/*;q=0.8",
            'Referer': "http://jwgl.bsuc.edu.cn/bsxyjw/cas/login.action",
            'Accept-Encoding': "gzip, deflate, sdch",
            'Accept-Language': "zh-CN,zh;q=0.8"
        }
        HEADERS1 = {
            'Host': "jw.tgc.edu.cn",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36 LBBROWSER",
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            'Accept-Encoding': "gzip, deflate, sdch",
            'Accept-Language': "zh-CN,zh;q=0.8"
        }
        Headers = {
            'Accept': "text/plain, */*; q=0.01",
            'Accept-Encoding': "gzip, deflate",
            'Accept-Language': "zh-CN,zh;q=0.8",
            'Connection': "keep-alive",
            'Content-Length': "1124",
            'Content-Type': "application/x-www-form-urlencoded",
            'Host': "jwgl.bsuc.edu.cn",
            'Origin': "http://jwgl.bsuc.edu.cn",
            'Referer': "http://jwgl.bsuc.edu.cn/bsxyjw/cas/login.action",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36 LBBROWSER",
            'X-Requested-With': "XMLHttpRequest"
        }
        username = self.username
        password = self.password
        txt_mm_expression = "12"
        txt_mm_userzh = "0"
        txt_mm_length = str(len(password))
        image = self.__session.get(self.image_url, headers=HEADERS)
        _sessionid = image.cookies.get("JSESSIONID")
        with open('img2.png', 'wb') as f:
            f.write(image.content)
        randnumber = input("请输入验证码:\n")
        p_username = "_u" + randnumber
        p_password = "_p" + randnumber
        password1 = MD5_HEX(MD5_HEX(password) + MD5_HEX(randnumber))
        username1 = username + ";;" + _sessionid
        username1 = str(base64.b64encode(username1.encode("utf-8")), "utf-8")
        rep = self.__session.get(self.url, headers=HEADERS)
        text = rep.text
        _deskey = re.search(r"var _deskey = '(.*?)';", text)
        _nowtime = re.search(r"var _nowtime = '(.*?)';", text)
        parms = p_username + "=" + username1 + "&" + p_password + "=" + password1 + "&randnumber=" + randnumber + "&isPasswordPolicy=1" + "&txt_mm_expression=" + txt_mm_expression + "&txt_mm_length=" + txt_mm_length + "&txt_mm_userzh=" + txt_mm_userzh
        token = MD5_HEX(MD5_HEX(parms) + MD5_HEX(_nowtime.group(1)))
        jsstr = get_js()
        ctx = execjs.compile(jsstr)
        _parms = str(base64.b64encode(ctx.call('strEnc', parms, _deskey.group(1)).encode("utf-8")), "utf-8")
        data = 'params='+_parms+'&token='+token+"&timestamp="+_nowtime.group(1)
        res = self.__session.post(self.login_url,headers=Headers,data=data)
        print(res.text)
    def run(self):
        self.login()
        # self.evaluate()
if __name__ == '__main__':
    username = input('请输入用户名:\n')
    password = input('请输入密码:\n')
    spider = UESTC(username,password)
    spider.run()


