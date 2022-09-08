from django.shortcuts import render
from django.views import generic

from . import models


class IndexView(generic.TemplateView):
    template_name = "index.html"

class DailyResultFormView(generic.TemplateView):
    """GCPから一日の収支結果を取得し表示するためのフォーム."""
    template_name = "form.html"

    def post(self, request):
        context = {
            'race_date': request.POST['race_date'],
            'place_id': request.POST['place_id'],
            'race_no': request.POST['race_no'],
        }

        # models.pyからオブジェクト作成
        result = models.GetResult()
        info = result.get_daily_betting_result(context)

        return render(request, 'result.html', info)

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
