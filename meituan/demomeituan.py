import requests
import base64
from time import time
import zlib
import urllib.parse
class meituan(object):
    def __init__(self):
        self.headers = {
            "Host": "sm.meituan.com",
            "Connection": "keep-alive",
            "Accept": "application/json",
            "Sec-Fetch-Dest": "empty",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Referer": "https://sm.meituan.com/meishi/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cookie": "_lxsdk_cuid=170bac1274ac8-057fc17c12b568-4313f6a-144000-170bac1274ac8; ci=208; rvct=208; client-id=4afb7696-3ec2-41e6-b9b4-b8e09cf19169; uuid=b44ca28782c24481aaec.1583752549.1.0.0; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; __mta=244276922.1583681206705.1583681206705.1583752553241.2; _lxsdk=170bac1274ac8-057fc17c12b568-4313f6a-144000-170bac1274ac8; _lxsdk_s=170bf022051-b6-7-15a%7C%7C7",

        }
    def get_query(self):
        #地点名称
        cityName = '三明'
        #美食类型
        cateId = 0
        #地区类型
        areaId = 0
        #分类方法
        sort = ''
        dinnerCountAttrId = ''
        #查询页数
        page = 1
        userId = ''
        uuid = 'b44ca28782c24481aaec.1583752549.1.0.0'
        platform = 1
        partner = 126
        riskLevel = 1
        optimusCode = 10
        originUrl = 'https://sm.meituan.com/meishi/'
        query = 'cityName=%s&cateId=%d&areaId=%d&sort=%s&dinnerCountAttrId=%s&page=%d&userId=%s&uuid=%s&platform=%d&partner=%d&originUrl=%s&riskLevel=%d&optimusCode=%d'%(cityName,cateId,areaId,sort,dinnerCountAttrId,page,userId,uuid,platform,partner,originUrl,riskLevel,optimusCode)
        query_after = query.split('&')
        "areaId=0&cateId=0&cityName=三明&dinnerCountAttrId=&optimusCode=10&originUrl=https://sm.meituan.com/meishi/&page=1&partner=126&platform=1&riskLevel=1&sort=&userId=&uuid=0ab85fe798e54a26ab30.1583681184.1.0.0"
        query_all = []
        true_query = ''
        for i in query_after:
            i = i.split('=')
            if i == query_after[-1]:
                query_all.append(i[0] + '=' + i[1] )
            else:
                query_all.append(i[0]+'='+i[1]+'&')
        for j in sorted(query_all):
            true_query += j
        true_query = "\""+true_query+"\""
        sign = self.algorithm(true_query)
        sign = sign[2:-1]
        token =self.get_token(sign)
        # 将token进行url编码,否则API后台不识别数据返回数据null
        token1 = urllib.parse.quote(token)
        return query+'&_token='+token1
    def get_token(self,sign):
        refer = "https://sm.meituan.com/"
        local_href = "https://sm.meituan.com/meishi/"
        token ={
            'rId' : 100900,
            'ver' : "1.0.6",
            'ts' : int(round(time() * 1000)-150 * 1000),
            'cts' : int(round(time() * 1000)),
            'brVD' : [406, 754],
            'brR' : [[1536, 864],[1536, 824],24,24],
            'bI' : [local_href,refer],
            'mT': [],
            'kT': [],
            'aT': [],
            'tT': [],
            'aM': "",
            'sign':"eJwljjFuwzAMRe+SQaMsxbGjFtBQeCpQZMsBmJixiVqSQVEFeoQsmXOUHKjoOSK0038g/v/8G2CE99EbdQbBfyD5PkBA//O4/t5vaqQYkYdUoryJcPWotAqFkoc0ordGJaaJ4pEXP4us+bVpctABSQpEfU6hqZxnatQKUw1UYamV3m57tS4gl8Shnpny5wd+4VI5JxavSsa/f6VQXQYn111w/+Kw28G2h1NrtO1c2ztr3U5bbbTZPAGMkUe8"
        }

        # print(str(token))
        result = self.algorithm(token)
        return result
    def algorithm(self,inf):
        # 直接zlib压缩提示要转字节类型
        info = str(inf).encode()
        # 进行def压缩
        temp = zlib.compress(info)
        # 压缩后进行base64加密
        baseenco = base64.b64encode(temp)
        # 加密后转str文本
        result = str(baseenco,encoding='utf-8')
        return result

    def get_lis(self):
        resp = requests.get(url = 'https://sm.meituan.com/meishi/api/poi/getPoiList?'+self.get_query(),headers = self.headers,verify=False)


    def run(self):
        self.get_lis()

if __name__ == '__main__':
    parse = meituan()
    parse.run()

