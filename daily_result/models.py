import itertools
import traceback
import requests
from django.db import models
from bs4 import BeautifulSoup

from . import gcs_ex


class GetResult:
    def __init__(self):
        self.bucket = gcs_ex.GCSBucket('boat_race_ai', 'boat_race_ai')
    
    def get_daily_betting_result(self, param):
        # キー
        race_date = param['race_date']
        place_id = param['place_id']
        race_no = param['race_no']

        df = self.bucket.read_csv('daily_betting_results/{}/bettings.csv'.format(race_date))
        buy = int(df['amount'].sum()*100)
        return_sum = int(df['return'].sum())
        benefit = return_sum - buy

        info = {
            "buy": buy, 
            "return_sum": return_sum, 
            "benefit": benefit, 
        }

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
