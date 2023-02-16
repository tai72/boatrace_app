import traceback
import itertools
import requests
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN
from bs4 import BeautifulSoup

from . import gcs_ex

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
