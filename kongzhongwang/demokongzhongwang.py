import re
import requests
import execjs
import time
from urllib import parse

class jskzw(object):
    def __init__(self,user,pwd):
        self.user = user
        self.pwd =pwd
        self.s = requests.session()
        self.base_login_url = 'https://sso.kongzhong.com/ajaxLogin?'
        self.base_url = 'https://passport.kongzhong.com'
        self.base_headers = {
            "Host": "passport.kongzhong.com",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36",
            "Sec-Fetch-Dest": "document",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Referer": "https://passport.kongzhong.com/v/user/userindex?validate=true",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            
        }
        self.login_headers = {
            "Host": "sso.kongzhong.com",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36",
            "Sec-Fetch-Dest": "script",
            "Accept": "*/*",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "no-cors",
            "Referer": "https://passport.kongzhong.com/login",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
        self.createCode_headers = {
            "Host": "sso.kongzhong.com",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36",
            "Sec-Fetch-Dest": "image",
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "no-cors",
            "Referer": "https://passport.kongzhong.com/login",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }


    def login(self):
        base = self.s.get(url=self.base_url+'/login',headers= self.base_headers,verify=False)
        createCode = self.s.get(url='https://sso.kongzhong.com/createQRCode',headers = self.createCode_headers,verify=False)
        dc_juery = 'j=j&jsonp=j&service=https://passport.kongzhong.com/&_=%d'%int(round(time.time() * 1000))
        login_exec = self.s.get(url=self.base_login_url+dc_juery,headers = self.login_headers,verify = False).text
        dc = re.search('"dc":"(.*?)"',login_exec).group(1)
        qr_user = parse.urlencode({'username':self.user})
        jsstr = self.get_js()
        ctx = execjs.compile(jsstr)
        encrypt = ctx.call('encrypt',self.pwd,dc)
        time.sleep(3)
        login_juery = 'j=j&&type=1&service=https://passport.kongzhong.com/&%s&password=%s&vcode=&toSave=0&_=%d'%(qr_user,encrypt,int(round(time.time() * 1000)))
        login_status = self.s.get(url=self.base_login_url+login_juery,headers = self.login_headers,verify = False)
        print(login_status.text)

    def run(self):
        self.login()

    def get_js(self):
        # f = open("D:/WorkSpace/MyWorkSpace/jsdemo/js/des_rsa.js",'r',encoding='UTF-8')
        f = open("encrydc.js", 'r', encoding='UTF-8')
        line = f.readline()
        htmlstr = ''
        while line:
            htmlstr = htmlstr + line
            line = f.readline()
        return htmlstr

if __name__ == '__main__':
    user =input('请输入您的账号:\n')
    pwd = input('请输入您的密码:\n')
    luanwushencai = jskzw(user,pwd)
    luanwushencai.run()



