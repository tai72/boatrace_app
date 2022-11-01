import itertools
import traceback
import requests
import pandas as pd
from decimal import Decimal
from django.db import models
from bs4 import BeautifulSoup

from . import gcs_ex
from . import utils


DICT_PLACE = {
    '桐生': '01', 
    '戸田': '02', 
    '江戸川': '03', 
    '平和島': '04', 
    '多摩川': '05', 
    '浜名湖': '06', 
    '蒲郡': '07', 
    '常滑': '08', 
    '津': '09', 
    '三国': '10', 
    'びわこ': '11', 
    '住之江': '12', 
    '尼崎': '13', 
    '鳴門': '14', 
    '丸亀': '15', 
    '児島': '16', 
    '宮島': '17', 
    '徳山': '18', 
    '下関': '19', 
    '若松': '20', 
    '芦屋': '21', 
    '福岡': '22', 
    '唐津': '23', 
    '大村': '24'
}

DICT_BET_TYPE = {
    '3連単': 'trifecta', 
    '3連複': 'triple', 
    '2連単': 'exacta', 
    '2連複': 'quinella', 
    '拡連複': 'wide', 
    '単勝': 'win'
}

DICT_BET_NUM = {
    'win': 1, 
    'quinella': 4, 
    'exacta': 5, 
    'triple': 6, 
    'trifecta': 7
}


class GetResult:
    def __init__(self):
        self.bucket = gcs_ex.GCSBucket('boat_race_ai', 'boat_race_ai')
    
    def get_daily_betting_result(self, param):
        # キー
        year = param['year']
        month = param['month']
        day = param['day']

        # race_date を作成
        month = str(month)
        if len(month) != 2:
            month = '0' + month
        day = str(day)
        if len(day) != 2:
            day = '0' + day
        race_date = str(year) + str(month) + str(day)

        try:
            df = self.bucket.read_csv('daily_betting_results/{}/bettings.csv'.format(race_date))
            buy = int(df['amount'].sum()*100)
            return_sum = int(df['return'].sum())
            benefit = return_sum - buy
            benefit_rate = Decimal(str((Decimal(return_sum) / Decimal(buy)))) // Decimal('0.001') * Decimal('0.1')

            info = {
                "buy": buy, 
                "return_sum": return_sum, 
                "benefit": benefit, 
                "benefit_rate": benefit_rate, 
            }

            return info
        except Exception as e:
            info = {"error": e}
            return info

class Prob:
    def __init__(self):
        self.bucket = gcs_ex.GCSBucket('boat_race_ai', 'boat_race_ai')
        self.replace_dct = {
            1: 'a',
            2: 'b',
            3: 'c',
            4: 'd',
            5: 'e',
            6: 'f',
        }
    
    def get_prob(self, param):
        # キー
        year = param['year']
        month = param['month']
        day = param['day']
        place_id = param['place_id']
        race_no = param['race_no']

        # race_date を作成
        month = str(month)
        if len(month) != 2:
            month = '0' + month
        day = str(day)
        if len(day) != 2:
            day = '0' + day
        race_date = str(year) + str(month) + str(day)

        # place_id を str　にする
        place_id = str(place_id)
        if len(place_id) != 2:
            place_id = '0' + place_id

        # データ取得
        path = 'prediction_result/{0}/{1}_{2}_prediction_result.csv'.format(race_date, place_id, race_no)
        prob_dct = {}
        try:
            df = self.bucket.read_csv(path)

            # 各ベットタイプの確率を取得
            for bet_type in df['bet_type'].unique():
                # 単勝
                if bet_type == 1:
                    for bracket_no in range(1, 7):
                        prob = df.loc[df['bracket_no'] == str(bracket_no), 'probability'].iloc[-1]
                        prob = float(int(prob*100000)/1000)    # %表記
                        # 変換
                        for key, val in zip(self.replace_dct.keys(), self.replace_dct.values()):
                            bracket_no = str(bracket_no).replace(str(key), val)
                        prob_dct[str(bracket_no)] = prob
                        
                # 2連複
                if bet_type == 4:
                    for bracket_no in df.loc[df['bet_type'] == bet_type, 'bracket_no']:
                        prob = df.loc[(df['bet_type'] == bet_type) & (df['bracket_no'] == bracket_no), 'probability'].iloc[-1]
                        prob = float(int(prob*100000)/1000)    # %表記
                        # 変換
                        for key, val in zip(self.replace_dct.keys(), self.replace_dct.values()):
                            bracket_no = str(bracket_no).replace(str(key), val).replace('-', '')
                        bracket_no += '_'
                        prob_dct[str(bracket_no)] = prob
                
                # 2連単
                if bet_type == 5:
                    for bracket_no in df.loc[df['bet_type'] == bet_type, 'bracket_no']:
                        prob = df.loc[(df['bet_type'] == bet_type) & (df['bracket_no'] == bracket_no), 'probability'].iloc[-1]
                        prob = float(int(prob*100000)/1000)    # %表記
                        # 変換
                        for key, val in zip(self.replace_dct.keys(), self.replace_dct.values()):
                            bracket_no = str(bracket_no).replace(str(key), val).replace('-', '')
                        prob_dct[str(bracket_no)] = prob
                        
                # 3連複
                if bet_type == 6:
                    for bracket_no in df.loc[df['bet_type'] == bet_type, 'bracket_no']:
                        prob = df.loc[(df['bet_type'] == bet_type) & (df['bracket_no'] == bracket_no), 'probability'].iloc[-1]
                        prob = float(int(prob*100000)/1000)    # %表記
                        # 変換
                        for key, val in zip(self.replace_dct.keys(), self.replace_dct.values()):
                            bracket_no = str(bracket_no).replace(str(key), val).replace('-', '')
                        bracket_no += '_'
                        prob_dct[str(bracket_no)] = prob

                # 3連単
                if bet_type == 7:
                    comb = list(itertools.permutations([1, 2, 3, 4, 5, 6], 3))
                    for elem in comb:
                        txt = '{0}-{1}-{2}'.format(elem[0], elem[1], elem[2])
                        prob = df.loc[df['bracket_no'] == txt, 'probability'].iloc[-1]
                        prob = float(int(prob*100000)/1000)    # %表記
                        txt = txt.replace('-', '')
                        for key, val in zip(self.replace_dct.keys(), self.replace_dct.values()):
                            txt = txt.replace(str(key), val)
                        prob_dct[txt] = prob
            prob_dct['error'] = ''
        except Exception as e:
            prob_dct['error'] = 'no data'
        
        # 選手名取得
        try:
            url = 'https://www.boatrace.jp/owpc/pc/race/racelist?rno={2}&jcd={1}&hd={0}'.format(race_date, place_id, race_no)
            html = requests.get(url).content
            soup = BeautifulSoup(html, 'html.parser')

            player_tbody = soup.find_all('tbody', {'class': 'is-fs12'})
            for i in range(len(player_tbody)):
                name = player_tbody[i].find_all('div', {'class': 'is-fs18'})[0].find('a').get_text()
                prob_dct['player_{}'.format(i+1)] = name
        except Exception as e:
            print(traceback.format_exc())
        return prob_dct
    
    def get_prob_tansyo(self, param):
        # キー
        race_date = param['race_date']
        place_id = param['place_id']
        race_no = param['race_no']

        # place_id を str　にする
        place_id = str(place_id)
        if len(place_id) != 2:
            place_id = '0' + place_id

        # データ取得
        path = 'prediction_result/{0}/{1}_{2}_prediction_result.csv'.format(race_date, place_id, race_no)
        prob_dct = {}
        try:
            df = self.bucket.read_csv(path)
            df = df.loc[df['bet_type'] == 1]

            for bracket_no in range(1, 7):
                prob = df.loc[df['bracket_no'] == str(bracket_no), 'probability'].iloc[-1]
                prob = float(int(prob*100000)/1000)    # %表記
                # 変換
                for key, val in zip(self.replace_dct.keys(), self.replace_dct.values()):
                    bracket_no = str(bracket_no).replace(str(key), val)
                prob_dct[str(bracket_no)] = prob
            prob_dct['error'] = ''
        except Exception as e:
            prob_dct['error'] = 'no data'
        
        # 選手名取得
        try:
            url = 'https://www.boatrace.jp/owpc/pc/race/racelist?rno={2}&jcd={1}&hd={0}'.format(race_date, place_id, race_no)
            html = requests.get(url).content
            soup = BeautifulSoup(html, 'html.parser')

            player_tbody = soup.find_all('tbody', {'class': 'is-fs12'})
            for i in range(len(player_tbody)):
                name = player_tbody[i].find_all('div', {'class': 'is-fs18'})[0].find('a').get_text()
                prob_dct['player_{}'.format(i+1)] = name
        except Exception as e:
            print(traceback.format_exc())
        return prob_dct

class RaceResultSelect:
    def __init__(self):
        self.bucket_boat = gcs_ex.GCSBucket('boat_race_ai', 'boat_race_ai')
        self.bucket_keiba = gcs_ex.GCSBucket('keiba-ai', 'keiba-ai')
    
    def read_todays_race_count(self):
        """本日の各場のレース数をkeiba-aiバケットから取得する."""

        # csv読み込み
        race_count_list = []
        try:
            df = self.bucket_keiba.read_csv('meta_data/todays_race_count_each_place.csv', encoding='utf-8')
            for idx in df.index:
                race_count_list.append({
                    "place_name": str(df.loc[idx, "place_name"]), 
                    "place_id": DICT_PLACE[str(df.loc[idx, "place_name"])], 
                    "race_count": str(df.loc[idx, "race_count"]), 
                })
        except:
            print('failed to get "todays_race_count_each_place.csv" from GCS.')
            print(traceback.format_exc())
        
        return race_count_list

class RaceResult:
    def __init__(self):
        # bucket
        self.bucket_boat = gcs_ex.GCSBucket('boat_race_ai', 'boat_race_ai')
        self.bucket_keiba = gcs_ex.GCSBucket('keiba-ai', 'keiba-ai')

        # db_setting（サーバー用）
        self.db_settings = self.bucket_boat.read_json(
            'db_settings/boatrace_cloudsql.json'
        )
        self.db_engine = utils.load_cloud_sql(self.db_settings)

        # db_setting（ローカル用）
        # self.db_settings = self.bucket_boat.read_json(
        #     'db_settings/boatrace_local.json'
        # )
        # self.db_engine = utils.load_local_db(self.db_settings)
    
    def get_betting_results(self, race_date, place_id, race_no):
        """betting_resultsから各買い目の枠番、確率、期待値を取得"""

        path = 'betting_results/{0}/{1}_{2}_betting_result.csv'.format(race_date, place_id, race_no)

        dct = {}
        try:
            df = self.bucket_boat.read_csv(path)

            # 3連単
            trifecta_list = []
            for idx in df.loc[df['bet_type'] == 7].index:
                # 着順に対する枠番
                bracket_no = df.loc[idx, 'bracket_no']
                first = bracket_no.split('-')[0]
                second = bracket_no.split('-')[1]
                third = bracket_no.split('-')[2]
                
                # 確率
                prob = str(df.loc[idx, 'probability'] * 100 // 0.01 / 100) + '%'
                
                # 期待値
                ex_val = str(df.loc[idx, 'ex_value'] * 100 // 1 * 0.01)
                if len(str(ex_val).split('.')[1]) > 2:
                    ex_val = str(ex_val.split('.')[0]) + '.' +  str(ex_val.split('.')[1][0:2])
                
                trifecta_list.append({
                    'first': first, 
                    'second': second, 
                    'third': third, 
                    'prob': prob, 
                    'ex_val': ex_val
                })
            dct['trifecta'] = trifecta_list

            # 3連複
            triple_list = []
            for idx in df.loc[df['bet_type'] == 6].index:
                # 着順に対する枠番
                bracket_no = df.loc[idx, 'bracket_no']
                first = bracket_no.split('-')[0]
                second = bracket_no.split('-')[1]
                third = bracket_no.split('-')[2]
                
                # 確率
                prob = str(df.loc[idx, 'probability'] * 100 // 0.01 / 100) + '%'
                
                # 期待値
                ex_val = str(df.loc[idx, 'ex_value'] * 100 // 1 * 0.01)
                if len(str(ex_val).split('.')[1]) > 2:
                    ex_val = str(ex_val.split('.')[0]) + '.' +  str(ex_val.split('.')[1][0:2])
                
                triple_list.append({
                    'first': first, 
                    'second': second, 
                    'third': third, 
                    'prob': prob, 
                    'ex_val': ex_val
                })
            dct['triple'] = triple_list
            
            # 2連単
            exacta_list = []
            for idx in df.loc[df['bet_type'] == 5].index:
                # 着順に対する枠番
                bracket_no = df.loc[idx, 'bracket_no']
                first = bracket_no.split('-')[0]
                second = bracket_no.split('-')[1]
                
                # 確率
                prob = str(df.loc[idx, 'probability'] * 100 // 0.01 / 100) + '%'
                
                # 期待値
                ex_val = str(df.loc[idx, 'ex_value'] * 100 // 1 * 0.01)
                if len(str(ex_val).split('.')[1]) > 2:
                    ex_val = str(ex_val.split('.')[0]) + '.' +  str(ex_val.split('.')[1][0:2])
                
                exacta_list.append({
                    'first': first, 
                    'second': second, 
                    'prob': prob, 
                    'ex_val': ex_val
                })
            dct['exacta'] = exacta_list

            # 2連複
            quinella_list = []
            for idx in df.loc[df['bet_type'] == 4].index:
                # 着順に対する枠番
                bracket_no = df.loc[idx, 'bracket_no']
                first = bracket_no.split('-')[0]
                second = bracket_no.split('-')[1]
                
                # 確率
                prob = str(df.loc[idx, 'probability'] * 100 // 0.01 / 100) + '%'
                
                # 期待値
                ex_val = str(df.loc[idx, 'ex_value'] * 100 // 1 * 0.01)
                if len(str(ex_val).split('.')[1]) > 2:
                    ex_val = str(ex_val.split('.')[0]) + '.' +  str(ex_val.split('.')[1][0:2])
                
                quinella_list.append({
                    'first': first, 
                    'second': second, 
                    'prob': prob, 
                    'ex_val': ex_val
                })
            dct['quinella'] = quinella_list

            # 「当たり」か「はずれ」の判定
            if df['return'].sum() > 0:
                dct['is_hit'] = 'hit.png'
            else:
                dct['is_hit'] = 'not_hit.png'
            
            # 収支
            buy = int(df['amount'].sum() * 100)
            dividend = int(df['return'].sum())
            benefit = dividend - buy
            dct['buy'] = buy
            dct['dividend'] = dividend
            dct['benefit'] = benefit

            dct['is_finished'] = True
        except:
            dct['is_finished'] = False
        
        print('betting_results')
        print(dct)

        return dct
    
    def get_race_result(self, race_date, place_id, race_no):
        """レース結果の各買い目の着順をスクレイピング、および予測時の確率、オッズを取得"""

        url = 'https://www.boatrace.jp/owpc/pc/race/raceresult?rno={2}&jcd={1}&hd={0}'.format(race_date, place_id, race_no)

        # パース
        html = requests.get(url).content
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find_all('table', {'class': 'is-w495'})
        tbody = table[2].find_all('tbody')

        # 取得
        container_dct = {}
        for i in range(len(tbody)):
            dct = {}
            lst = []
            bet_type = tbody[i].find_all('tr')[0].find('td').get_text()

            # 配当金
            payout_list = []
            payout = tbody[i].find_all('span', {'class': 'is-payout1'})
            for k in range(len(payout)):
                if payout[k].get_text() != '\xa0':
                    payout_list.append(payout[k].get_text())
            dct["payout"] = payout_list
            
            wrapper_row = tbody[i].find_all('div', {'class': 'numberSet1_row'})
            for j in range(len(wrapper_row)):
                wrapper_number = wrapper_row[j].find_all('span', {'class': 'numberSet1_number'})
                txt = '-'.join([wrapper_number[k].get_text() for k in range(len(wrapper_number))])
                lst.append(txt)
            dct["comb"] = lst
            container_dct[DICT_BET_TYPE.get(bet_type)] = dct

        # GCS（boatrace）から、レース結果に対する予測結果を取得する。
        path = 'prediction_result/{0}/{1}_{2}_prediction_result.csv'.format(race_date, place_id, race_no)
        df = self.bucket_boat.read_csv(path)

        for bet_type in container_dct.keys():
            if bet_type not in DICT_BET_NUM.keys():
                continue
            
            bet_type_num = DICT_BET_NUM[bet_type]
            prob_list = []
            for i in range(len(container_dct[bet_type]['comb'])):
                prob = df.loc[(df["bet_type"] == bet_type_num) & (df["bracket_no"] == container_dct[bet_type]["comb"][i]), 'probability'].iloc[-1]
                prob = str(prob * 100 // 0.01 / 100) + '%'
                prob_list.append(prob)
            container_dct[bet_type]["prob"] = prob_list
        
        # DBの「pre_odds」テーブルから、予測時のオッズを取得する.
        bet_type_list = ['win', 'quinella', 'exacta', 'triple', 'trifecta']
        for key in bet_type_list:
            bracket_no = container_dct[key]['comb'][0]
            bet_type = DICT_BET_NUM[key]
            query = f"select * from pre_odds where race_date = {race_date} and place_id = '{place_id}' and race_no = {race_no} and bet_type = {bet_type} and bracket_no = '{bracket_no}';"
            # DB接続
            with self.db_engine.connect() as conn:
                try:
                    for _ in range(3):
                        res = conn.execute(query)
                        break
                except Exception as e:
                    print(e)
                    pass
            
            # 抽出
            pre_odds = 0
            ex_val = 'err'
            if res != None:
                try:
                    result = list(res)
                    if len(result) != 0:
                        pre_odds = result[0][5]
                    
                    # 反映
                    ex_val = float(container_dct[key]['prob'][0].replace('%', '')) * float(pre_odds) / 100
                    ex_val = round(Decimal(ex_val), 2)
                    container_dct[key]['ex_val'] = ex_val
                except:
                    # 反映
                    container_dct[key]['ex_val'] = ex_val
                    print('\n\n')
                    print(traceback.format_exc())
                    print('\n\n')
        
        print('レース結果をスクレイピングしたやつ')
        print(container_dct)
        
        return container_dct
