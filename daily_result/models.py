from django.db import models

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
    
    def get_prob(self, param):
        # キー
        race_date = param['race_date']
        place_id = param['place_id']
        race_no = param['race_no']

        prob = {
            "123": 999,
        }

        return prob
