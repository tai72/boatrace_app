import traceback
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN

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
