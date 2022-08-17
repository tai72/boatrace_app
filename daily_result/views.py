from django.shortcuts import render
from django.views import generic


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

        params = {
            "benefit": "もうちょいまってねん",
        }
        return render(request, 'result.html', params)

class DailyResultView(generic.TemplateView):
    """フォーム情報を受け取り、表示する"""
    template_name = "result.html"
