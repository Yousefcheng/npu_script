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
        yqtb_url = "http://yqtb.nwpu.edu.cn"
        
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
        fillinHeader = {
            "Host" : "yqtb.nwpu.edu.cn",
            "Connection" : "keep-alive",
            "Accept" : "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With" : "XMLHttpRequest",
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin" : yqtb_url,
            "Referer" : yqtb_detail_url,
            "Accept-Encoding" : "gzip, deflate",
            "Accept-Language" : "zh-CN,zh;q=0.9,en;q=0.8",
            # "Cookie" : "JSESSIONID=" + yqtb_cookie
        }
        res = self.session.get(url)
        res = self.session.get(yqtb_detail_url,headers=fillinHeader)
        content = res.content.decode('utf-8')
        # print(content)
        try:
            extract = re.findall("ry_util.jsp.*(?=')",content)[0] # 提取请求参数
        except:
            return 0
        # print(extract)
        yqtb_fillin_url += extract

        # # 提交填报信息
        try:
            res = self.session.post(yqtb_fillin_url, data = fillinData,headers=fillinHeader)
        except:
            return 0
        # print(res.content.decode('utf-8'))
        try:
            if res.json()['state']=='1':
                print(res.json())
                print(self.uid+'打卡成功')
                return 1
                
            else:
                print(self.uid+'打卡失败')
                return 0
                
        except:
            print(self.uid+'打卡失败')
            return 0
            
        
# studentId='2021264575'
# password='Cyf13935401857.'
# test1=Aoxiang()
# test1.login_aoxiang(studentId,password)
# test1.get_userinfo()
# test1.yqtb()



if __name__ == '__main__' :
    db = pymysql.connect(host="127.0.0.1", user="root", password="212666", db="aoxiang")


    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()

    # 使用 execute()  方法执行 SQL 查询
    cursor.execute("select * from aoxiang_users where switch=1")

    # 使用 fetchone() 方法获取单条数据.
    num=1
    while 1:
        n=0
        res=cursor.fetchone()
        if res is None:
            #表示已经取完结果集
            break
        studentId=str(res[1])
        password=str(res[2])
        try:
            print('第'+str(num)+'个账号')
            aoxiang=Aoxiang()
            aoxiang.login_aoxiang(studentId,password)        
            aoxiang.get_userinfo()
            # res=aoxiang.yqtb()
            
            while True:
                res=aoxiang.yqtb()
                if res==1:
                    break
                else:
                    print(studentId+'尝试重新打卡')
                    if n>=3:
                        break       
                    n=n+1
                sleep(3)
        except Exception as e:
            print(studentId+'打卡失败')
            print(e)
        num=num+1
        sleep(5)

    # 关闭数据库连接
    db.close()


