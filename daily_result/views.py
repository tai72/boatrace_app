import json
import matplotlib
from django.http.response import JsonResponse
from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse
from datetime import datetime

from . import models


DICT_PLACE = {
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
    '18': '徳山', 
    '19': '下関', 
    '20': '若松', 
    '21': '芦屋', 
    '22': '福岡', 
    '23': '唐津', 
    '24': '大村'
}


class IndexView(generic.TemplateView):
    template_name = "index.html"

class DailyResultFormView(generic.TemplateView):
    """GCPから一日の収支結果を取得し表示するためのフォーム."""
    template_name = "form.html"

    def post(self, request):
        context = {
            'race_date': request.POST['race_date'],
            # 'place_id': request.POST['place_id'],
            # 'race_no': request.POST['race_no'],
        }

        # models.pyからオブジェクト作成
        result = models.GetResult()
        info = result.get_daily_betting_result(context)

        # エラーがなければ結果を表示、エラー（該当ファイルがないなど）があればエラーページを表示
        if info.get('error') == None:
            return render(request, 'result.html', info)
        else:
            return render(request, 'error_page.html', info)

class DailyResultView(generic.TemplateView):
    """フォーム情報を受け取り、表示する"""
    template_name = "result.html"

class ProbFormView(generic.TemplateView):
    """予測確率を表示"""
    template_name = "prob_form.html"

    def post(self, request):
        context = {
            'race_date': request.POST['race_date'],
            'place_id': request.POST['place_id'],
            'race_no': request.POST['race_no'],
        }

        # models.py の　Probget_prob()から各買い目の確率を取得.
        prob = models.Prob()
        info = prob.get_prob(context)

        return render(request, 'prob.html', info)

class ProbView(generic.TemplateView):
    """確率出力"""
    template_name = "prob.html"

class RaceResultSelectView(generic.TemplateView):
    """見たいレース結果を選択するページ"""
    template_name = "race_result_select.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data'] = [1, 2, 3]

        # 本日のレース数
        result = models.RaceResultSelect()
        # context["todays_race_count"] = json.dumps(result.read_todays_race_count())
        context["todays_race_count"] = result.read_todays_race_count()
        context["place_count"] = len(context["todays_race_count"])
        context["now_date"] = datetime.now().strftime('%Y%m%d')

        return context

    def post(self, request):
        data = {
            'data1': [1, 2, 3], 
        }

        # return JsonResponse(data)
        return render(request, 'race_result_select.html', data)
    
class RaceResultView(generic.TemplateView):
    """レース結果の詳細を表示"""

    template_name = "race_result.html"

    def get(self, request, **kwargs):

        # urlから値取得
        race_date = kwargs['race_date']
        place_id = kwargs['place_id']
        race_no = kwargs['race_no']

        # betting_results取得（モデルの予測結果）
        result = models.RaceResult()
        dct = result.get_betting_results(race_date, place_id, race_no)

        # contextに格納
        context = dct.copy()    # {trifecta: [{'first': '1', 'second': '2', ...}, {...}, ...]}}

        # レース結果のスクレイピング結果（実際のレース結果）
        context['race_result'] = result.get_race_result(race_date, place_id, race_no)    # {'trifecta': ['1-2-3'], 'triple': ['1-2-3'], 'exacta': ['1-2'], ...}

        # レース情報
        context['place_name'] = DICT_PLACE[place_id]

        # 開発用
        context['race_date'] = race_date
        context['place_id'] = place_id
        context['race_no'] = race_no

        print(context)

        return self.render_to_response(context)
