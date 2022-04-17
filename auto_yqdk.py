"""
cron: 0 6,8,10 * * *
new Env('疫情填报');
"""

from email import header
import sys
from time import sleep
import requests
import json
import re
import os
import base64
import pymysql



class Aoxiang:
    def __init__(self) -> None:
        # yqtb_url = "http://yqtb.nwpu.edu.cn"
        aoxiang_url='https://uis.nwpu.edu.cn/cas/login'
        self.session = requests.Session()
        # self.session.close
        response1 = self.session.get(aoxiang_url)
        self.cookie=self.session.cookies
        # self.yqtb_cookie = self.session.cookies["JSESSIONID"] # 疫情填报的会话id
        self.uis_cookie = response1.cookies["SESSION"] # 登录翱翔门户的会话id
    

    def login_aoxiang(self,studentId,password):
        # 登录翱翔门户post的数据
        # uis_login_url = "https://uis.nwpu.edu.cn/cas/login?service=http%3A%2F%2Fyqtb.nwpu.edu.cn%2F%2Fsso%2Flogin.jsp%3FtargetUrl%3Dbase64aHR0cDovL3lxdGIubndwdS5lZHUuY24vL3d4L3hnL3l6LW1vYmlsZS9pbmRleC5qc3A%3D"
        aoxiang_url='https://uis.nwpu.edu.cn/cas/login'
        self.studentId=studentId
        loginData = {
            "username" : studentId,
            "password" : password,
            "currentMenu" : 1,
            "execution" : "e1s1",
            "_eventId" : "submit",
            "geolocation" : "",
            "submit" : "稍等片刻……"
        }
        loginHeader = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36',
            'accept-language': 'zh-CN,zh;q=0.9',
            "Cookie" : "SESSION=" + self.uis_cookie
        }
        # 请求登录
        self.session.get(aoxiang_url)
        response2 = self.session.post(aoxiang_url, data = loginData, headers = loginHeader)
        # print(response2.text)
        is_success=re.findall(r'登录成功',response2.text)
        # print(is_success)
        if is_success:
            return 1
        else:
            return 0

    def get_userinfo(self):
        # info_xid_url='https://personal-security-center.nwpu.edu.cn'
        info_url='https://personal-security-center.nwpu.edu.cn/api/v1/personal/user/info'

        ticket = self.session.get('https://uis.nwpu.edu.cn/cas/login?service=https://ecampus.nwpu.edu.cn/').url.split('=')[-1]
        ticket = ticket.replace("%2B", '+').replace("%3D", '=').split('.')[1]
        self.xIdToken = json.loads(base64.b64decode(ticket.encode('utf8')).decode('utf8'))['idToken']
        headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'x-id-token': self.xIdToken
        }
        res=self.session.get(info_url,headers=headers).json()
        self.name=res['data']['user']['name']
        self.uid=res['data']['user']['uid']
        # print(self.name,self.uid)
        return self.name,self.uid
        
        # print(xIdToken)
    def yqtb(self):
        yqtb_url = "yqtb.nwpu.edu.cn"
        
        url='http://yqtb.nwpu.edu.cn/wx/xg/yz-mobile/index.jsp'
        
        yqtb_fillin_url = "http://yqtb.nwpu.edu.cn/wx/ry/" # 获取到签名和时间戳后拼接上去
        yqtb_detail_url = "http://yqtb.nwpu.edu.cn/wx/ry/jrsb_xs.jsp"
        
        
        fillinData = {
            "hsjc" : 1,
            "xasymt" : 1,
            "actionType" : "addRbxx",
            "userLoginId" : self.studentId,
            "szcsbm" : 1,
            "bdzt" : 1,
            "szcsmc" : "在学校",
            "sfyzz" : 0,
            "sfqz" : 0,
            "tbly" : "sso",
            "qtqksm" : "",
            "ycqksm" : "",
            "userType" : 2,
            "userName" : self.name


        }
        Header={
            # "Host" : "yqtb.nwpu.edu.cn",
            # "Connection" : "keep-alive",
            # "Accept" : "application/json, text/javascript, */*; q=0.01",
            # "X-Requested-With" : "XMLHttpRequest",
            # "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
            # "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            # "Origin" : yqtb_url,
            # "Referer" : yqtb_detail_url,
            # "Accept-Encoding" : "gzip, deflate",
            # "Accept-Language" : "zh-CN,zh;q=0.9,en;q=0.8",
            # # "Cookie" : "JSESSIONID=" + yqtb_cookie

            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Content-Type': 'application/x-www-form-urlencoded',
            # Cookie: JSESSIONID=945B6A17026C7BDF42971D7271CBE851; _dd_s=logs=1&id=7f8c15b2-8590-4df6-b8dc-0c4d8b298599&created=1650119624247&expire=1650120559686
            'Host': 'yqtb.nwpu.edu.cn',
            'Origin': 'https://yqtb.nwpu.edu.cn',
            'Referer': 'https://yqtb.nwpu.edu.cn/wx/ry/jrsb_xs.jsp',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': "Windows",
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36',
        }
        fillinHeader = {
            # "Host" : "yqtb.nwpu.edu.cn",
            # "Connection" : "keep-alive",
            # "Accept" : "application/json, text/javascript, */*; q=0.01",
            # "X-Requested-With" : "XMLHttpRequest",
            # "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
            # "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            # "Origin" : yqtb_url,
            # "Referer" : yqtb_detail_url,
            # "Accept-Encoding" : "gzip, deflate",
            # "Accept-Language" : "zh-CN,zh;q=0.9,en;q=0.8",
            # # "Cookie" : "JSESSIONID=" + yqtb_cookie

            # 'Accept':' application/json, text/javascript, */*; q=0.01',
            'Accept': "application/json, text/javascript, */*; q=0.01",
            # 'Accept-Encoding': 'gzip, deflate, br',
            # 'Accept-Language': 'zh-CN,zh;q=0.9',
            # 'Connection': 'keep-alive',
            'Content-Length': '196',
            'Content-Type': 'application/x-www-form-urlencoded',
            # Cookie: JSESSIONID=945B6A17026C7BDF42971D7271CBE851; _dd_s=logs=1&id=7f8c15b2-8590-4df6-b8dc-0c4d8b298599&created=1650119624247&expire=1650120559686
            'Host': 'yqtb.nwpu.edu.cn',
            'Origin': 'https://yqtb.nwpu.edu.cn',
            'Referer': 'https://yqtb.nwpu.edu.cn/wx/ry/jrsb_xs.jsp',
            # 'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
            # 'sec-ch-ua-mobile': '?0',
            # 'sec-ch-ua-platform': "Windows",
            # 'Sec-Fetch-Dest': 'empty',
            # 'Sec-Fetch-Mode': 'cors',
            # 'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }
        res = self.session.get(url)
        res = self.session.get(yqtb_detail_url,headers=Header)
        content = res.content.decode('utf-8')
        # print(content)
        try:
            extract = re.findall("ry_util.jsp.*(?=')",content)[0] # 提取请求参数
            print(extract)
        except:
            return 0
        # print(extract)
        yqtb_fillin_url += extract
        print(yqtb_fillin_url)

        # # 提交填报信息
        # try:
        res = self.session.post(yqtb_fillin_url, data = fillinData,headers=fillinHeader)
            # pri
        # except:
        #     return 0
        # print(res.content.decode('utf-8'))
        # try:
        print(res.text)
        # if res.json()['state']=='1':
        #     print(res.json())
        #     print(self.uid+'打卡成功')
        #     return 1
                
        #     else:
        #         print(self.uid+'打卡失败')
        #         return 0
                
        # except Exception as e:
        #     # print(self.uid+'打卡失败')
        #     print(e)
        #     return 0
            
        

# test1=Aoxiang()
# test1.login_aoxiang(studentId,password)
# test1.get_userinfo()
# test1.yqtb()

def pushplus(token,title,msg):
    url='http://www.pushplus.plus/send?token='+str(token)+'&title='+str(title)+'&content='+str(msg)+'&template=html'
    res=requests.get(url)

if __name__ == '__main__' :

    yqdk_sid=os.environ.get('yqdk_sid')
    yqdk_sid=str(yqdk_sid).split('@')
    yqdk_pwd=os.environ.get('yqdk_pwd')
    yqdk_pwd=str(yqdk_pwd).split('@')
    token=os.environ.get('token')
    token=str(token)
    msg=''
    # print(yqdk_sid)
    aoxiang=Aoxiang()
    print(aoxiang.login_aoxiang(yqdk_sid,yqdk_pwd))
    print(aoxiang.get_userinfo())
    res=aoxiang.yqtb()
    # for i in range(len(yqdk_sid)):
    #     print(i)
        

    #     studentId=str(yqdk_sid[i])
    #     password=str(yqdk_pwd[i])
    #     # try:
    #     aoxiang=Aoxiang()
    #     print(aoxiang.login_aoxiang(studentId,password))
    #     print(aoxiang.get_userinfo())
    #     # res=aoxiang.yqtb()
    #     n=0
    #     while True:
    #         res=aoxiang.yqtb()
    #         if res==1:
    #             print('打卡成功')
    #             txt='<a>'+studentId+'打卡成功'+'</a>'+'<br>'
    #             msg=msg+txt
    #             break
    #         else:
    #             print('重新打卡')
    #             txt=studentId+'尝试重新打卡'+'<br>'
    #             msg=msg+txt
    #             if n>=3:
    #                 break       
    #             n=n+1
    #         sleep(3)
    #     # except Exception as e:
    #     #     print(studentId+'打卡失败')
    #     #     txt=studentId+'打卡失败'+'<br>'
    #     #     msg=msg+txt
    #     #     print(e)
    #     sleep(5)
    # pushplus(token)


