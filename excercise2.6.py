import os
from selenium.webdriver import Chrome 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

# Selenium4対応済

def set_driver(hidden_chrome: bool=False):
    '''
    Chromeを自動操作するためのChromeDriverを起動してobjectを取得する
    '''
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
    options = Options()

    # ヘッドレスモード（画面非表示モード）をの設定
    if hidden_chrome:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument(f'--user-agent={USER_AGENT}') # ブラウザの種類を特定するための文字列
    options.add_argument('log-level=3') # 不要なログを非表示にする
    options.add_argument('--ignore-certificate-errors') # 不要なログを非表示にする
    options.add_argument('--ignore-ssl-errors') # 不要なログを非表示にする
    options.add_experimental_option('excludeSwitches', ['enable-logging']) # 不要なログを非表示にする
    options.add_argument('--incognito') # シークレットモードの設定を付与
    
    # ChromeのWebDriverオブジェクトを作成する。
    service=Service(ChromeDriverManager().install())
    return Chrome(service=service, options=options)


def main():
    '''
    main処理
    '''
    search_keyword = input("検索ワードを入力して下さい:")
    # driverを起動
    driver = set_driver()
    
    # Webサイトを開く
    driver.get("https://tenshoku.mynavi.jp/")
    time.sleep(5)
    
    '''
    ポップアップを閉じる
    ※余計なポップアップが操作の邪魔になる場合がある
      モーダルのようなポップアップ画面は、通常のclick操作では処理できない場合があるため
      excute_scriptで直接Javascriptを実行することで対処する
    '''
    driver.execute_script('document.querySelector(".karte-close").click()')
    time.sleep(5)
    # ポップアップを閉じる
    driver.execute_script('document.querySelector(".karte-close").click()')


    '''
    find_elementでHTML要素(WebElement)を取得する
    byで、要素を特定する属性を指定するBy.CLASS_NAMEの他、By.NAME、By.ID、By.CSS_SELECTORなどがある
    特定した要素に対して、send_keysで入力、clickでクリック、textでデータ取得が可能
    '''
    # 検索窓に入力
    driver.find_element(by=By.CLASS_NAME, value="topSearch__text").send_keys(search_keyword)
    # 検索ボタンクリック
    driver.find_element(by=By.CLASS_NAME, value="topSearch__button").click()


    '''
    find_elements(※複数形)を使用すると複数のデータがListで取得できる
    一覧から同一条件で複数のデータを取得する場合は、こちらを使用する
    '''
    
    #空のname_list,job_title_listを用意する
    name_list = []
    job_title_list = []
    '''
    recruit_elmsには１社分の情報が格納されているのでforでループさせて１つづつ取り出して、name_list,job_title_listに格納する
    '''
    while True:
        # divタグのcassetteRecruitクラスを取り出し、変数recruit_elmsに入れる
        recruit_elms = driver.find_elements(by=By.CLASS_NAME, value="cassetteRecruit")
        
        for recruit_elm in recruit_elms:
            try:
                # raise Exception("意図的なエラー")
                # 会社名を含むデータを変数nameに取り出す
                name = recruit_elm.find_element(by=By.CSS_SELECTOR,value=".cassetteRecruit__name").text
                # 求人タイトルを含むデータを変数job_titleに取り出す
                job_title = recruit_elm.find_element(by=By.CSS_SELECTOR,value=".cassetteRecruit__copy.boxAdjust").text
                # DataFrameに対してリスト形式でデータを追加する
                name_list.append(name)
                job_title_list.append(job_title)
                
            except Exception as e:
                print(e)
                
        df = pd.DataFrame({
            '会社名':name_list,
            '求人タイトル':job_title_list
            })
            
        try:
            next_link = driver.find_element(by=By.CLASS_NAME,value="iconFont--arrowLeft")
            driver.get(next_link.get_attribute("href"))
        except:
            print("最終ページです") 
            break
            
    #追加されたデータフレームを出力する   
    df.to_csv(f"{search_keyword}.csv", encoding ="utf-8-sig")

# 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    main()
