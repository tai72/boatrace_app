import logging
from django.shortcuts import render
from django.views import generic
from django.urls import reverse_lazy
from django.contrib import messages
from datetime import datetime
from pprint import pprint

from . import models
from .forms import InquiryForm
from .lib import DealBucketData

logger = logging.getLogger(__name__)


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
    """ GCSから一日の収支結果を取得し表示するためのフォーム """

    template_name = "form.html"

    def post(self, request):
        # Get posted data.
        post_data = {
            'year': request.POST['year'], 
            'month': request.POST['month'], 
            'day': request.POST['day'], 
        }

        # GCSからデータ取得
        bucket_dealer = DealBucketData('boat_race_ai', 'boat_race_ai')
        context = bucket_dealer.get_daily_betting_result(post_data)
        context['dividend_ratio_each_comb'] = bucket_dealer.get_dividend_ratio_each_comb(post_data)

        pprint(context)

        # エラーがなければ結果を表示、エラー（該当ファイルがないなど）があればエラーページを表示
        if context.get('error') == None:
            return render(request, 'result.html', context)
        else:
            return render(request, 'error_page.html', context)

class DailyResultView(generic.TemplateView):
    """ フォーム情報を受け取り、表示する """
    template_name = "result.html"

class ProbFormView(generic.TemplateView):
    """ 「１レースの各買い目に対する予測確率」を表示するための入力フォーム """

    template_name = "prob_form.html"

    def post(self, request):
        post_data = {
            'year': request.POST['year'], 
            'month': request.POST['month'], 
            'day': request.POST['day'], 
            'place_id': request.POST['place_id'], 
            'race_no': request.POST['race_no'], 
        }

        # GCSからデータ取得
        bucket_dealer = DealBucketData('boat_race_ai', 'boat_race_ai')
        context = bucket_dealer.get_prob(post_data)

        return render(request, 'prob.html', context)

class ProbView(generic.TemplateView):
    """ 確率出力 """
    template_name = "prob.html"

class RaceResultSelectView(generic.TemplateView):
    """ 見たいレース結果を選択するページ """

    template_name = "race_result_select.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # GCSからデータ取得
        bucket_dealer_boat = DealBucketData('boat_race_ai', 'boat_race_ai')
        bucket_dealer_keiba = DealBucketData('keiba-ai', 'keiba-ai')
        context["todays_race_count"] = bucket_dealer_keiba.read_todays_race_count()
        context["place_count"] = len(context["todays_race_count"])
        context["now_date"] = datetime.now().strftime('%Y%m%d')

        return context
    
class RaceResultView(generic.TemplateView):
    """ レース結果の詳細を表示 """

    template_name = "race_result.html"

    def get(self, request, **kwargs):

        # クエリパラメータ
        race_date = kwargs['race_date']
        place_id = kwargs['place_id']
        race_no = kwargs['race_no']

        # GCS（betting_results）からデータ取得
        bucket_dealer = DealBucketData('boat_race_ai', 'boat_race_ai')
        dct = bucket_dealer.get_betting_results(race_date, place_id, race_no)

        # contextに格納
        context = dct.copy()    # {trifecta: [{'first': '1', 'second': '2', ...}, {...}, ...]}}

        # レース結果のスクレイピング結果（実際のレース結果）
        context['race_result'] = bucket_dealer.get_race_result(race_date, place_id, race_no)    # {'trifecta': ['1-2-3'], 'triple': ['1-2-3'], 'exacta': ['1-2'], ...}

        # レース結果のアイコン表示用
        if len(context['race_result']['trifecta']) != 0:
            bracket_first = context['race_result']['trifecta']['comb'][0][0]
            bracket_second = context['race_result']['trifecta']['comb'][0][2]
            bracket_thrid = context['race_result']['trifecta']['comb'][0][4]

            context['bracketFirst'] = '{}.png'.format(bracket_first)
            context['bracketSecond'] = '{}.png'.format(bracket_second)
            context['bracketThird'] = '{}.png'.format(bracket_thrid)

        # レース情報
        context['place_name'] = DICT_PLACE[place_id]

        # 開発用
        context['race_date'] = race_date
        context['place_id'] = place_id
        context['race_no'] = race_no

        print('views')
        print(context)

        return self.render_to_response(context)

class InquiryView(generic.FormView):
    """お問合せ"""

    template_name = "inquiry.html"
    form_class = InquiryForm
    success_url = reverse_lazy('daily_result:inquiry')  # 正しく送信された時にリダイレクトされるとこ

    # フォームバリデーションに問題がなかったら実行されるメソッド（親クラスのメソッド）
    def form_valid(self, form):
        logger.info('Inquiry sent by {}'.format(form.cleaned_data['name']))
        form.send_email()
        messages.success(self.request, 'お問い合わせありがとうございました。')
        return super().form_valid(form)

class CurrentSituationView(generic.TemplateView):
    template_name = "current_situation.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # GCS（betting_results）からデータ取得
        bucket_dealer = DealBucketData('boat_race_ai', 'boat_race_ai')
        context['balance'] = bucket_dealer.get_current_balance()
        
        pprint(context)

        return context
