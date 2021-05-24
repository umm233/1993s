#!/usr/bin/env python
# coding=utf-8

import os
import time
import urllib

import gevent
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def list_page(url, foldername):
    print('crawling : %s' % url)
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(
        executable_path='./chromedriver_win32/chromedriver.exe', chrome_options=chrome_options)
    driver.set_window_size(1366, 768)
    driver.get(url)
    resp = driver.page_source
    html = etree.HTML(resp)
    driver.close()
    driver.quit()

    vkeys = html.xpath('//*[@class="stui-vodlist__thumb lazyload"]/@href')
    vjpgs = html.xpath(
        '//*[@class="stui-vodlist__thumb lazyload"]/@data-original')
    vtitles = html.xpath('//*[@class="stui-vodlist__thumb lazyload"]/@title')

    jobs = []
    for i in range(len(vkeys)):
        item = {}
        vkeytemp = vkeys[i].split('/')[-1]
        vkeytemp = vkeytemp.strip('.html')
        item['vname'] = vtitles[i] + '_' + vkeytemp
        item['vjpg'] = vjpgs[i]
        try:
            jobs.append(gevent.spawn(
                download_jpg, item['vjpg'], item['vname'], 'jpg', foldername))
        except Exception as err:
            print(err)
    gevent.joinall(jobs, timeout=2)


def detail_page(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(
        executable_path='./chromedriver_win32/chromedriver.exe', chrome_options=chrome_options)
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
    print("正在获取 %s 的下载链接, 目前一共有 %s 集" %(title, len(vlists)))
    vjs = []
    # 切换到视频框frame
    for i in range(len(vlists)):
        driver.get('https://www.zxzj.me' + vlists[i])
        print("==> 获取第%s集的下载链接" %(i+1))
        driver.switch_to.frame(
            driver.find_elements_by_tag_name("iframe")[2])
        resp = driver.page_source
        html = etree.HTML(resp)
        vjs.append(html.xpath(
            '//*[@class="dplayer-video dplayer-video-current"]/@src')[0])
        print(vjs[i])
        time.sleep(2)

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


def run(_arg=None):
    # paths = ['movie', 'show', 'movie_poster', 'show_poster']
    # for path in paths:
    #     if not os.path.exists(path):
    #         os.mkdir(path)
    if _arg == 'mp4':
        with open('download.txt', 'r') as file:
            keys = list(set(file.readlines()))
        jobs = []
        for key in keys:
            url = 'https://www.zxzj.me/detail/%s' % key.strip()
            print(url)
            jobs.append(gevent.spawn(detail_page, url))
        gevent.joinall(jobs, timeout=2)
    print('finish !')


if __name__ == '__main__':
    run("mp4")
    print("<== 获取成功，结果存放在download-link中")
    os.system("pause")
