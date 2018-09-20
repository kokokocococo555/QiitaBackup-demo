#!/usr/bin/env python
# coding: utf-8

# 1. SeleniumでQiitaにログイン
# 2. マイページから投稿一覧とURLを取得
# 3. 各投稿の編集ページへ移行
# 4. 編集ページからQiita記法のテキストを抽出
# 5. 保存

# 自動ログインのデモ
# 今回はスクレイピングをSeleniumで行う。
# 今回はChromeDriverを使う→ページの移行が可視化されてコーディング時に分かりやすい
# Qiitaはスクレイピング等について利用規約で特に言及していない。

from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

import os
import sys
import time
import datetime
import csv
from selenium import webdriver # pip install selenium
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

QIITA_EMAIL=sys.argv[1]
QIITA_PASSWORD=sys.argv[2]
QIITA_ACCOUNT=sys.argv[3]

deray_time = 2

def main():
    """
    メイン処理
    """
    # chromedriver本体のパスを指定
    chr_path = r"C:\chromedriver-2.42\chromedriver.exe"
    driver = webdriver.Chrome(executable_path=chr_path)

    # Qiitaにログインする
    login_qiita(driver)
    time.sleep(deray_time)
    print('login')
    
    # マイページから投稿一覧とURLを取得
    # マイページに移行
    mypage_url = 'https://qiita.com/' + QIITA_ACCOUNT
    driver.get(mypage_url)
    time.sleep(deray_time)
    print('move to ', mypage_url, ' ...')

    # 投稿済みの記事のリスト
    posts = driver.find_elements_by_css_selector('article.ItemLink')
    num_posts = len(posts)
    # 投稿済みの記事のURLリスト
    post_urls = []
    for post in posts:
        post_urls.append(post.find_element_by_css_selector('.ItemLink__title a').get_attribute('href'))

    post_data_list = []

    for i in range(num_posts):
        no = num_posts - i
        # 各投稿のURLを取得
        post_url = post_urls[i]
        post_data = get_post_content(driver, post_url)
        # 話数的な数字をゼロパディングで作成
        post_no = str(no).zfill(4)
        post_data['no'] = post_no
        post_data_list.append(post_data)
        print('[{}]{} data is appended  ...'.format(post_no, post_url))
        
    save_as_csv(post_data_list)
    print('backup finish!')
    

def login_qiita(driver):
    """
    Qiitaにログイン
    """
    # Qiitaログイン画面を開く
    driver.get('https://qiita.com/login')
    time.sleep(deray_time)
    
    # Qiitaにログイン
    login_email = driver.find_element_by_id('identity')
    login_email.send_keys(QIITA_EMAIL)

    login_password = driver.find_element_by_id('password')
    login_password.send_keys(QIITA_PASSWORD)

    login_button = driver.find_element_by_name('commit')
    login_button.click()


def get_post_content(driver, post_url):
    """
    投稿記事コンテンツを取得
    """
    # 各投稿の編集ページへ移行
    driver.get(post_url)
    time.sleep(deray_time)

    # 編集ページからQiita記法のテキストを抽出
    # 投稿ページ内の編集へのリンクを取得
    edit_url = driver.find_element_by_css_selector('.it-Header_edit a').get_attribute('href')

    # 編集ページへ移行
    driver.get(edit_url)
    time.sleep(deray_time)

    # 投稿記事コンテンツを取得
    post_data = {
        # Qiita記法のテキストをまるごとゲット
        'text': driver.find_element_by_css_selector('textarea.editorMarkdown_textarea').text,
        # タイトル
        'title': driver.find_element_by_css_selector('div.editorTitle input').get_attribute('value'),
        # tag
        'tags': driver.find_element_by_css_selector('div.editorTag input').get_attribute('value'),
        'url': post_url,
        }

    return post_data


def save_as_csv(post_data_list):
    """
    csvファイルにデータを保存
    """
    # バックアップファイルの保存先の指定
    directory_name = 'backup'
    # ディレクトリが存在しなければ作成する
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    # バックアップファイル名の作成
    today = datetime.datetime.now().strftime('%Y-%m-%d_%Hh%Mm')
    csv_name = os.path.join(directory_name, '[{}]Qiita-backup.csv'.format(today))

    # 列名（1行目）を作成
    col_name = ['no', 'title', 'url', 'tags', 'text']

    with open(csv_name, 'w', newline='', encoding='utf-8') as output_csv:
        csv_writer = csv.writer(output_csv)
        csv_writer.writerow(col_name) # 列名を記入

        # csvに1行ずつ書き込み
        for post in post_data_list:
            row_items = [post['no'], post['title'], post['url'], post['tags'], post['text']]
            csv_writer.writerow(row_items)
            
    print(csv_name, ' saved...')


if __name__ == '__main__':
    main()
