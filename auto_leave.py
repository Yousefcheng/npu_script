"""
cron: 0 5,14 * * *
new Env('自动疫情填报');
"""

# from email import header
from calendar import c
import sys
from time import sleep
import requests
import json
import re
import os
import base64
import time
# import pymysql


class Aoxiang:
    def __init__(self) -> None:
        # yqtb_url = "http://yqtb.nwpu.edu.cn"
        aoxiang_url = 'https://uis.nwpu.edu.cn/cas/login'
        self.session = requests.Session()
        # self.session.close
        response1 = self.session.get(aoxiang_url)
        self.cookie = self.session.cookies
        # self.yqtb_cookie = self.session.cookies["JSESSIONID"]
        self.uis_cookie = response1.cookies["SESSION"]

    def login_aoxiang(self, studentId, password):
        # 登录翱翔门户post的数据
        # uis_login_url = "https://uis.nwpu.edu.cn/cas/login?service=http%3A%2F%2Fyqtb.nwpu.edu.cn%2F%2Fsso%2Flogin.jsp%3FtargetUrl%3Dbase64aHR0cDovL3lxdGIubndwdS5lZHUuY24vL3d4L3hnL3l6LW1vYmlsZS9pbmRleC5qc3A%3D"
        aoxiang_url = 'https://uis.nwpu.edu.cn/cas/login'
        self.studentId = studentId
        loginData = {
            "username": studentId,
            "password": password,
            "currentMenu": 1,
            "execution": "e1s1",
            "_eventId": "submit",
            "geolocation": "",
            "submit": "稍等片刻……"
        }
        loginHeader = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36',
            'accept-language': 'zh-CN,zh;q=0.9',
            "Cookie": "SESSION=" + self.uis_cookie
        }
        # 请求登录
        self.session.get(aoxiang_url)
        response2 = self.session.post(
            aoxiang_url, data=loginData, headers=loginHeader)
        # print(response2.text)
        is_success = re.findall(r'登录成功', response2.text)
        # print(is_success)
        if is_success:
            return 1
        else:
            return 0

    def get_userinfo(self):
        # info_xid_url='https://personal-security-center.nwpu.edu.cn'
        info_url = 'https://personal-security-center.nwpu.edu.cn/api/v1/personal/user/info'

        ticket = self.session.get(
            'https://uis.nwpu.edu.cn/cas/login?service=https://ecampus.nwpu.edu.cn/').url.split('=')[-1]
        ticket = ticket.replace("%2B", '+').replace("%3D", '=').split('.')[1]
        self.xIdToken = json.loads(base64.b64decode(
            ticket.encode('utf8')).decode('utf8'))['idToken']
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'x-id-token': self.xIdToken
        }
        res = self.session.get(info_url, headers=headers).json()
        self.name = res['data']['user']['name']
        self.uid = res['data']['user']['uid']
        # print(self.name,self.uid)
        return self.name, self.uid

        # print(xIdToken)
    def distory(self):  # 销假
        base_url = 'https://yqtb.nwpu.edu.cn/wx/xg/xsqj/qjsq/'

        url = 'https://yqtb.nwpu.edu.cn/wx/xg/yz-mobile/index.jsp'

        qj_list_url = 'https://yqtb.nwpu.edu.cn/wx/xg/xsqj/qjsq/qjsq_list.jsp'
        middle_url='https://yqtb.nwpu.edu.cn/wx/xg/yz-mobile/grzx_xs.jsp'
        leave_url = 'https://yqtb.nwpu.edu.cn/wx/xg/xsqj/qjsq/qjsq_util.jsp'
            
        res = self.session.get(url)
        res = self.session.get(middle_url)
        res = self.session.get(qj_list_url)
        # print(res.text)
        is_distory = re.findall(r'待销假', res.text)
        print(is_distory)
        if is_distory:
            qssj = re.findall(r'(?<=请假开始时间：)\d.*-\d.*?(?=:)', res.text)[0]+'时'
            jssj = re.findall(r'(?<=请假结束时间：)\d.*-\d.*?(?=:)', res.text)[0]
            extract = re.findall(r'qjsq_info.jsp.*(?=")', res.text)[0]
            id = re.findall(r'(?<=id\=).*?(?=&)', extract)[0]
            xj_data = {
                'actionType': 'qjxj',
                'id': id,
                'qssj': qssj,
                'sjfxsj': jssj,
                'xjsm': '',
                'dyspr': '1',
                'xsxh': self.studentId,
                'xsxm': self.name,
            }
            fill_Header = {
                "Host": "yqtb.nwpu.edu.cn",
                "Connection": "keep-alive",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "X-Requested-With": "XMLHttpRequest",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Origin": 'http://yqtb.nwpu.edu.cn',
                "Referer": 'http://yqtb.nwpu.edu.cn/wx/xg/xsqj/qjsq/qjsq_list.jsp',
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                # "Cookie" : "JSESSIONID=" + yqtb_cookie
            }
            res = self.session.post(
                leave_url, headers=fill_Header, data=xj_data)
            try:
                if res.json()['state'] == 1:
                    print('销假成功')
                    return 1
            except Exception as e:
                print(e)
                print('销假失败')
                return 0
        else:
            print('没假可消')
            return 2

    def leave(self):
        time_str = time.strftime("%Y-%m-%d")
        qssj = time_str+' 08'
        jssj = time_str+' 23'
        # yqtb_url = "http://yqtb.nwpu.edu.cn"

        url = 'https://yqtb.nwpu.edu.cn/wx/xg/yz-mobile/index.jsp'
        leave_url = 'https://yqtb.nwpu.edu.cn/wx/xg/xsqj/qjsq/qjsq_util.jsp'
        

        fill_Data = {
            'actionType': 'addXsqxj',  # 类型
            'xgh': self.studentId,  # 学号
            'xm': self.name,  # 姓名
            'qssj': qssj,  # 起始时间
            'jzsj': jssj,  # 结束时间
            'sylb': 3,  # 事由类型
            'sysm': '去南院',            # 事由说明
            'sflkxx': 2,  # 行程范围
            'qwmdd': '南苑实验室',  # 前往目的地
            'xslbdm': 2,
            'dyspr': 1  # 第一审批人  1：导师   2：导员
        }

        fill_Header = {
            "Host": "yqtb.nwpu.edu.cn",
            "Connection": "keep-alive",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": 'yqtb.nwpu.edu.cn',
            "Referer": 'http://yqtb.nwpu.edu.cn/wx/xg/xsqj/qjsq/qjsq_list.jsp',
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            # "Cookie" : "JSESSIONID=" + yqtb_cookie

        }

        res = self.session.get(url)
        res = self.session.post(leave_url, headers=fill_Header, data=fill_Data)
        try:
            if res.json()['state'] == 1:
                print('请假成功')
                return 1
        except Exception:
            print(Exception)
            return 0


def pushplus(token, title, msg):
    url = 'http://www.pushplus.plus/send?token=' + \
        str(token)+'&title='+str(title)+'&content='+str(msg)+'&template=html'
    res = requests.get(url)



def pprint(msg):
    print(msg)
    return '<a>'+str(msg)+'</a>'+'<br>'
 

if __name__ == '__main__':

    leave_sid = os.environ.get('leave_sid')
    leave_sid = str(leave_sid).split('&')
    leave_pwd = os.environ.get('leave_pwd')
    leave_pwd = str(leave_pwd).split('&')
    token = os.environ.get('token')
    token = str(token).split('&')

    msg = ''

    for i in range(len(leave_sid)):
        txt = '第'+str(i)+'个账号：'
        msg = msg+pprint(txt)
        studentId = str(leave_sid[i])
        password = str(leave_pwd[i])
        try:
            aoxiang = Aoxiang()
            aoxiang.login_aoxiang(studentId, password)
            aoxiang.get_userinfo()
            aoxiang.distory()
            for _ in range(3):
                res = aoxiang.leave()
                if res == 1:
                    txt = studentId+'请假成功'
                    msg = msg+pprint(txt)
                    break
                else:
                    txt = studentId+'尝试重新请假'
                    msg = msg+pprint(txt)
                sleep(3)
            else:
                txt = studentId+'请假失败,请联系作者'
                msg = msg+pprint(txt)
        except Exception as e:
            txt = studentId+'请假失败,请联系作者'
            msg = msg+pprint(txt)
            print(e) 
        sleep(5)
    for t in token:
        pushplus(t, '自动请假', msg)
