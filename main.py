import json
import os
import pprint
import sys
import time
import string
import traceback
import thread
import urllib2
from lxml import etree

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

reload(sys)
sys.setdefaultencoding('utf8')


class MyPrinter(pprint.PrettyPrinter):

    def format(self, object, context, maxlevels, level):
        if isinstance(object, unicode):
            return (object.encode('utf8'), True, False)
        return pprint.PrettyPrinter.format(self, object, context, maxlevels, level)


class ptt_notify:

    #config_data = {}
    hestory_interest_list = {}  # 找到的文章列表
    hestory_checked_list = {}  # 找到的文章列表

    def __init__(self, board, keywords):
        self.board = board
        self.keywords = keywords
        self.httpHandler = urllib2.HTTPHandler(debuglevel=0)
        self.httpsHandler = urllib2.HTTPSHandler(debuglevel=0)
        self.opener = urllib2.build_opener(self.httpHandler, self.httpsHandler)
        self.opener.addheaders.append(('Cookie', 'over18=1'))  # 進入18禁的板
        urllib2.install_opener(self.opener)
        pass

    def mail(self, keywords, subject, body, url):
        return None
        try:
            msg = MIMEMultipart("alternative")
            msg['Subject'] = subject
            msg['From'] = "party@qmo-a.com"
            msg['To'] = ""
            #msg['Bcc'] = self.config_data["mail"]

            part1 = MIMEText(u"網址：" + url + u"\n\n關鍵字：" + keywords + u"\n\n\n" + body, "plain", "utf-8")
            msg.attach(part1)

            s = smtplib.SMTP('localhost')
            s.sendmail(msg['From'], msg["To"].split(",") + msg["Bcc"].split(","), msg.as_string().encode('ascii'))
            s.quit()
        except Exception:
            print('generic exception: ' + traceback.format_exc())

    def stripTags(self, s):
        intag = [False]

        def chk(c):
            if intag[0]:
                intag[0] = (c != '>')
                return False
            elif c == '<':
                intag[0] = True
                return False
            return True
        return ''.join(c for c in s if chk(c))

    def stripSpeicalSign(self, s):
        return s.replace("\n", "").replace("\r", "").replace("\t", "").replace(" ", "").replace(":", "").replace(".", "").replace("\"", "").replace("(", "").replace(")", "").replace(",", "").replace("，", "").replace("。", "").replace("「", "").replace("」", "").replace("、", "").replace("：", "").replace("…", "")

    def get_html(self, url):
        request = urllib2.Request(url)
        request.add_header('User-Agent', 'fake-client')
        try:
            response = urllib2.urlopen(request, timeout=4)
            return response.read().decode('utf-8')
        except urllib2.HTTPError, e:
            print('HTTPError = ' + str(e.code))
            return ''
        except urllib2.URLError, e:
            print('URLError = ' + str(e.reason))
            return ''
        except Exception:
            print('generic exception: ' + traceback.format_exc())
            return ''
        # print response.info()
        # print response.read()
        # print response.geturl()

    def get_article(self, url):
        html = self.get_html(url)
        if len(html) == 0:
            return ''
        page = etree.HTML(html)
        hrefs = page.xpath(u"/descendant::div[@id='main-content']")
        body = ''
        for href in hrefs:
            body = body + self.stripTags(etree.tostring(href, encoding='utf8'))

        return (body)

    def get_board_list(self, board):

        url = "https://www.ptt.cc/bbs/" + board + "/index.html"
        html = self.get_html(url)
        if len(html) == 0:
            return ''
        page = etree.HTML(html)
        hrefs = page.xpath(u"//*[contains(@class, 'r-ent')]/*/a")

        for href in hrefs:
            if href.text.find(u"公告") > 0:
                continue
            if self.hestory_interest_list.has_key(href.attrib["href"]) == True:
                continue
            if self.hestory_checked_list.has_key(href.attrib["href"]) == True:
                continue
            # print stripSpeicalSign(stripTags(etree.tostring(href,encoding='utf8')))
            article_url = "\nhttps://www.ptt.cc" + href.attrib["href"]
            article_body = self.get_article(article_url)
            self.hestory_checked_list[href.attrib["href"]] = href.text
            keys = self.check_keywords(self.stripSpeicalSign(article_body), self.keywords)
    # 找到了
            if len(keys) > 0:
                self.hestory_interest_list[href.attrib["href"]] = href.text
                print u"\t" + href.text + " " + article_url + "\n"
                self.mail(keys, href.text, article_body, article_url)
            time.sleep(0.2)
        return ''

    def check_keywords(self, article, keywords):
        keys = ''
        for keyword in keywords:
            if unicode(article, 'utf-8').find(keyword) > 0:
                print u"\t符合keyword:" + keyword
                keys = keys + "," + keyword

        return keys

    def process(self):
        while True:
            try:
                print u"\n==進入" + self.board + u"版=="
                self.get_board_list(self.board)
        #        MyPrinter().pprint(self.hestory_interest_list)

                if len(self.hestory_checked_list) > 500:
                    self.hestory_checked_list.clear()  # 移除全部

                print "interest num = " + str(len(self.hestory_interest_list))
                print "checked num = " + str(len(self.hestory_checked_list))
                print u"\n等待中..."
            except Exception:
                print('generic exception: ' + traceback.format_exc())
            time.sleep(10)


def ThreadfunA(string, sleeptime, *args):
    a = ptt_notify("Wanted", ["徵","安"])
    a.process()
    print '{0}_{1}\n'.format(string, sleeptime)
    time.sleep(sleeptime)


def ThreadfunB(string, sleeptime, *args):
    a = ptt_notify("Wanted", ["求","火"])
    a.process()
    print '{0}_{1}\n'.format(string, sleeptime)
    time.sleep(sleeptime)

if __name__ == "__main__":
    thread.start_new_thread(ThreadfunA, ("ThreadFunA", 3))
    thread.start_new_thread(ThreadfunB, ("ThreadFunB", 4))
    while(True):
        print 'MainThread {0}'.format(thread.get_ident())
        time.sleep(1)


#    def process(self):
#        while True:
#            try:
#                # load config
#                json_data = open('config.json')
#                self.config_data = json.load(json_data)  # global 變數
#                MyPrinter().pprint(self.config_data["keywords"])
#                json_data.close()
#
#                for board in self.config_data["ptt_boards"]:
#                    print u"\n==進入" + board + u"版=="
#                    self.get_board_list(board)
#        #        MyPrinter().pprint(self.hestory_interest_list)
#
#                if len(self.hestory_checked_list) > 500:
#                    self.hestory_checked_list.clear()  # 移除全部
#
#                print "interest num = " + str(len(self.hestory_interest_list))
#                print "checked num = " + str(len(self.hestory_checked_list))
#                print u"\n等待中..."
#            except Exception:
#                print('generic exception: ' + traceback.format_exc())
#            time.sleep(10)


# setup cookie and debug


#url = 'https://www.ptt.cc/bbs/Gossiping/M.1422944508.A.D98.html'
# print get_article(url)
# get_board_list("Food")


# reference
# http://blog.csdn.net/pleasecallmewhy/article/details/8925978
# http://blog.ez2learn.com/2008/10/05/python-is-the-best-choice-to-grab-web/

# lxml
# http://www.cnblogs.com/descusr/archive/2012/06/20/2557075.html
