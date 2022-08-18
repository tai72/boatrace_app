from django.shortcuts import render
from django.views import generic

from . import models


class IndexView(generic.TemplateView):
    template_name = "index.html"

class DailyResultFormView(generic.TemplateView):
    """GCPから一日の収支結果を取得し表示するためのフォーム."""
    template_name = "form.html"

    def post(self, request):
        message = 'メッセージ受け取りしました！'
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
