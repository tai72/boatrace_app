import traceback
import itertools
import requests
import os
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from sqlalchemy import text

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

DICT_PLACE_NO = {
    '01': '桐生', 
    '02': '戸田', 
    '03': '江戸川', 
    '04': '平和島', 
    '05': '多摩川', 
    '06': '浜名湖', 
    '07': '蒲郡', 
    '08': '常滑', 
    '09': '津', 
    '10': '三国', 
    '11': 'びわこ', 
    '12': '住之江', 
    '13': '尼崎', 
    '14': '鳴門', 
    '15': '丸亀', 
    '16': '児島', 
    '17': '宮島', 
    '18': '徳島', 
    '19': '下関', 
    '20': '若松', 
    '21': '芦屋', 
    '22': '福岡', 
    '23': '唐津', 
    '24': '大村', 
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

DICT_BET_NAME = {
    'win': '単勝', 
    'quinella': '2連複', 
    'exacta': '2連単', 
    'triple': '3連複', 
    'trifecta': '3連単', 
}


class DealBucketData:
    def __init__(self, project_id: str, bucket: str):
        self.bucket = gcs_ex.GCSBucket(project_id, bucket)
        self.replace_dct = {
            1: 'a',
            2: 'b',
            3: 'c',
            4: 'd',
            5: 'e',
            6: 'f',
        }
    
    def make_race_date(
        self, 
        post_data: dict
    ) -> str:
        """ year, month, day から 'YYYYMMDD' の形式にして返す """

        # 日付データ取得
        year = post_data['year']
        month = post_data['month']
        day = post_data['day']

        # race_date を作成
        if len(str(month)) != 2:
            month = '0' + str(month)
        if len(str(day)) != 2:
            day = '0' + str(day)
        race_date = str(year) + str(month) + str(day)

        return race_date
    
    def make_place_id(
        self, 
        post_data: dict
    ) -> str:
        """ place_id を2桁の文字列にして返す """

        place_id = post_data['place_id']
        if len(str(place_id)) != 2:
            place_id = '0' + place_id
        return str(place_id)
    
    def get_db_engine(
        self, 
        is_product: bool
    ):
        """ db接続するためのエンジンを返す """

        if is_product:
            # db_setting（サーバー用）
            db_settings = self.bucket.read_json(
                'db_settings/boatrace_cloudsql.json'
            )
            db_engine = utils.load_cloud_sql(db_settings)
        else:
            # db_setting（ローカル用）
            db_settings = self.bucket.read_json(
                'db_settings/boatrace_local.json'
            )
            db_engine = utils.load_local_db(db_settings)

        return db_engine

    def get_daily_betting_result(
        self, 
        post_data: dict
    ) -> dict:
        """ １日の収支情報を取得・計算する """

        # 「race_date」
        race_date = self.make_race_date(post_data)

        # バケットからデータ取得
        try:
            df = self.bucket.read_csv('daily_betting_results/{}/bettings.csv'.format(race_date))
            buy = int(df['amount'].sum()*100)
            return_sum = int(df['return'].sum())
            benefit = return_sum - buy
            benefit_rate = Decimal(str((Decimal(return_sum) / Decimal(buy)))) // Decimal('0.001') * Decimal('0.1')

            context = {
                'buy': buy, 
                'return_sum': return_sum, 
                'benefit': benefit, 
                'benefit_rate': benefit_rate, 
            }
            return context
        except Exception as e:
            context = {'error': e}
            return context
        
    def get_dividend_ratio_each_comb(
        self, 
        post_data: dict
    ) -> dict:
        """ 配当金においての、買い目に対する割合 """

        # 「race_date」
        race_date = self.make_race_date(post_data)

        dividend_each_comb = {}
        try:
            # 読み込み
            df = self.bucket.read_csv(f'daily_betting_results/{race_date}/results_about_bet_type.csv')

            # 買い目ごとの配当金を取得（実数）
            for key in DICT_BET_NUM.keys():
                bet_type = str(DICT_BET_NUM[key])
                dividend = int(df.loc[df['bet_type'] == bet_type, 'return'].iloc[-1])
                dividend_each_comb[key] = dividend
            
            # 買い目ごとの配当金の割合に変換
            buy_sum = Decimal(str(int(df.loc[df['bet_type'] == 'SUM', 'sum_buy'].iloc[-1])))
            dividend_sum = Decimal(str(int(df.loc[df['bet_type'] == 'SUM', 'return'].iloc[-1])))
            for key in dividend_each_comb.keys():
                # 割合
                dividend = Decimal(str(dividend_each_comb[key]))
                dividend_ratio = ((dividend / dividend_sum) * 100).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)

                # 購入金額
                buy = df.loc[df['bet_type'] == str(DICT_BET_NUM[key]), 'sum_buy'].iloc[-1]
                buy = (Decimal(str(buy)) / buy_sum).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
                
                # 配当金
                dividend_val = df.loc[df['bet_type'] == str(DICT_BET_NUM[key]), 'return'].iloc[-1]
                dividend_val = (Decimal(str(dividend_val)) / dividend_sum).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
                
                # 上書き
                dividend_each_comb[key] = [dividend_ratio, buy, dividend_val]
            
            return dividend_each_comb
        except:
            print(traceback.format_exc())
    
    def get_prob(
        self, 
        post_data: dict
    ) -> dict:
        """ 「１レースの各買い目に対する予測確率」を取得 """

        # race_date, place_id, race_no
        race_date = self.make_race_date(post_data)
        place_id = self.make_place_id(post_data)
        race_no = post_data['race_no']

        # データ取得
        filepath = f'prediction_result/{race_date}/{place_id}_{race_no}_prediction_result.csv'
        prob_dct = {}
        try:
            df = self.bucket.read_csv(filepath)

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
            prob_dct['error'] = e
        
        # 選手名取得
        try:
            url = f'https://www.boatrace.jp/owpc/pc/race/racelist?rno={race_no}&jcd={place_id}&hd={race_date}'
            html = requests.get(url).content
            soup = BeautifulSoup(html, 'html.parser')

            player_tbody = soup.find_all('tbody', {'class': 'is-fs12'})
            for i in range(len(player_tbody)):
                name = player_tbody[i].find_all('div', {'class': 'is-fs18'})[0].find('a').get_text()
                prob_dct['player_{}'.format(i+1)] = name
        except Exception as e:
            print(traceback.format_exc())
        return prob_dct
    
    def read_todays_race_count(
        self
    ) -> list:
        """ 本日の各場のレース数を keiba-ai バケットから取得する """

        # csv読み込み
        race_count_list = []
        try:
            df = self.bucket.read_csv('meta_data/todays_race_count_each_place.csv', encoding='utf-8')
            print(df)
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
    
    def get_betting_results(
        self, 
        race_date: str, 
        place_id: str, 
        race_no: str
    ) -> dict:
        """ betting_result バケットから各買い目の枠番、確率、期待値を取得 """

        print('\n\n------------------------------------------\n')
        print('【INFO】get_betting_results() starts.\n')

        filepath = f'betting_results/{race_date}/{place_id}_{race_no}_betting_result.csv'

        dct = {}
        try:
            df = self.bucket.read_csv(filepath)

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
        
        print(dct)
        print('\n------------------------------------------\n\n')

        return dct
    
    def get_race_result(
        self, 
        race_date: str, 
        place_id: str, 
        race_no: str
    ) -> dict:
        """ レース結果の各買い目の着順をスクレイピング、および予測時の確率、オッズを取得 """

        print('\n\n------------------------------------------\n')
        print('【INFO】get_race_result() starts.\n')

        # データベースエンジン
        db_engine = self.get_db_engine(os.getenv('GAE_APPLICATION', False))

        # レース結果URL
        place_id = '0' + place_id if len(str(place_id)) == 1 else place_id
        url = f'https://www.boatrace.jp/owpc/pc/race/raceresult?rno={race_no}&jcd={place_id}&hd={race_date}'

        # スクレイピング
        try:
            # parse
            soup = BeautifulSoup(requests.get(url).content, 'html.parser')
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
        except Exception as e:
            print('【ERROR】Failed to scrape race result page.')
            print(e)

        # GCS（boatrace）から、レース結果に対する予測結果を取得する。
        try:
            filepath = f'prediction_result/{race_date}/{place_id}_{race_no}_prediction_result.csv'
            df = self.bucket.read_csv(filepath)

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
        except Exception as e:
            print('【ERROR】Failed to get race_result from GCS.')
            print(e)
        
        # DBの「pre_odds」テーブルから、予測時のオッズを取得する.
        bet_type_list = ['win', 'quinella', 'exacta', 'triple', 'trifecta']
        for key in bet_type_list:
            bracket_no = container_dct[key]['comb'][0]
            bet_type = DICT_BET_NUM[key]
            query = f"select * from pre_odds where race_date = {race_date} and place_id = '{place_id}' and race_no = {race_no} and bet_type = {bet_type} and bracket_no = '{bracket_no}';"
            # DB接続
            res = None
            with db_engine.connect() as conn:
                try:
                    for _ in range(3):
                        res = conn.execute(text(query))
                        break
                except Exception as e:
                    print('【ERROR】Failed to connect to DB.')
                    print(e)
                    print(traceback.format_exc())
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
                    print('【ERROR】Failed to extract data from response.')
                    print(traceback.format_exc())
                    print('\n\n')

        print('レース結果をスクレイピングしたやつ')
        print(container_dct)
        print('\n------------------------------------------\n\n')
        
        return container_dct
    
    def get_current_balance(
        self
    ) -> dict:
        """ リアルタイムな収支情報を計算する """

        # 今日の日付を取得
        dt_now = {
            'year': datetime.now().year, 
            'month': datetime.now().month, 
            'day': datetime.now().day, 
        }
        race_date = self.make_race_date(dt_now)

        # 「betting_results/<今日の日付>/」配下のblob取得 → 古い順にソート
        blobs = [blob for blob in self.bucket.list_objects(f'betting_results/{race_date}')]
        blobs = sorted(blobs, key=lambda x: x.updated)

        # blobの更新時間をリストに格納
        update_time_list = [(blob.updated + timedelta(hours=9)).strftime('%H:%M') for blob in blobs]

        # 古い順にファイルのパスを取得
        paths = [blob.name for blob in blobs]

        # 収支など計算
        buy_sum = 0
        return_sum = 0
        buy_sum_list = []
        benefit_list = []
        for path in paths:
            # Reading blob.
            df = self.bucket.read_csv(path)
            
            # Calc.
            buy_sum += df['amount'].sum() * 100
            return_sum += df['return'].sum()

            # For graph.
            buy_sum_list.append(buy_sum)
            benefit_list.append(return_sum - buy_sum)
        
        dct_current_balance = {
            'buy_sum': int(buy_sum), 
            'return_sum': int(return_sum), 
            'benefit': int(return_sum - buy_sum), 
            'update_time_list': update_time_list, 
            'buy_sum_list': buy_sum_list, 
            'benefit_list': benefit_list, 
        }
        
        return dct_current_balance

    def get_todays_bettings_and_results(
        self
    ) -> dict:
        """ GCS（keiba-ai）から現在の投票結果やレース結果などの情報を取得 """

        # 読み取り
        todays_bettings_and_results = self.bucket.read_json('meta_data/todays_bettings_and_results.json')

        # 場名を追加、買い目の名称を日本語に
        for place_id in todays_bettings_and_results['bettings'].keys():
            todays_bettings_and_results['bettings'][place_id]['place_name'] = DICT_PLACE_NO[str(place_id)]

            for race_no in todays_bettings_and_results['bettings'][place_id].keys():
                if race_no != 'place_name':
                    for comb in DICT_BET_NAME.keys():
                        try:
                            todays_bettings_and_results['bettings'][place_id][race_no][DICT_BET_NAME[comb]] = todays_bettings_and_results['bettings'][place_id][race_no].pop(comb)
                        except:
                            print('miss')
                            print(todays_bettings_and_results['bettings'][place_id][race_no][comb])
        
        # race_no でソートする
        for place_id in todays_bettings_and_results['bettings'].keys():
            for race_no in range(1, 13):
                if todays_bettings_and_results['bettings'][place_id].get(str(race_no)) != None:
                    todays_bettings_and_results['bettings'][place_id][str(race_no)] = todays_bettings_and_results['bettings'][place_id].pop(str(race_no))

        return todays_bettings_and_results
