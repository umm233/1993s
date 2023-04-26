#!/usr/bin/env python
# coding=utf-8

import os
import sys
import time
import urllib

import gevent
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

site_url = ''

def detail_page(url):
    chrome_driver_path = './chromedriver_win32/chromedriver.exe'
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(
        executable_path=chrome_driver_path, chrome_options=chrome_options)
    driver.set_window_size(1366, 768)
    driver.get(url)
    resp = driver.page_source
    html = etree.HTML(resp)

    # 获取视频名称
    title = ''.join(html.xpath('//h1[@class="title"]//text()')[0]).strip()
    print("正在获取 %s 的下载链接" %title)
    # 获取视频链接
    vlists = html.xpath(
        '((//ul[@class="stui-content__playlist clearfix"])[1])/li/a/@href')
    # print(vlists)
    print("剧名: %s, 目前一共有 %d 集" %(title, len(vlists)))
    vjs = []
    # 切换到视频框frame
    for i in range(len(vlists)):
        driver.get(site_url + vlists[i])
        print("==> 获取第%s集的下载链接" %(i+1))
        driver.switch_to.frame(
            driver.find_elements_by_tag_name("iframe")[2])
        resp = driver.page_source
        html = etree.HTML(resp)
        vjs.append(html.xpath(
            '//*[@class="dplayer-video dplayer-video-current"]/@src')[0])
        print(vjs[i])
        time.sleep(0.3)

    with open('./download-link.txt', 'w') as f:
        link_str = str(vjs).replace("[", "").replace("]", "").replace(",", "\n\n")
        f.write(link_str)
    driver.close()


def download_jpg(url, name, filetype, foldername):
    filepath = '%s/%s.%s' % (foldername, name, filetype)
    if os.path.exists(filepath):
        print('this file had been downloaded :: %s' % (filepath))
        return
    response = urllib.request.urlretrieve(url, '%s' % (filepath))
    print('download success :: %s' % (filepath))
    response.close()

def download_video(id:str):
    jobs = []
    url = '{site_url}/detail/{id}.html'.format(site_url=site_url, id=id)
    print(url)

    jobs.append(gevent.spawn(detail_page, url))
    gevent.joinall(jobs, timeout=2)
    print('finish !')

def parse_url(url:str):
    parsed_url = urllib.parse.urlparse(url)
    domain = parsed_url.netloc
    # 3969-1-1.html
    last_param = url.split('/')[-1]
    id = last_param.split('-')[0]
    return domain, id

if __name__ == '__main__':
    _arg = str(sys.argv[1])
    domain, id = parse_url(_arg)
    site_url = 'https://{domain}'.format(domain=domain)
    download_video(id=id)
    print("<== 获取成功, 下载连接存放在download-link.txt中")
    os.system("pause")
