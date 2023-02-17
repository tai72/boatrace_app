from django.core.mail import EmailMessage
from django import forms


class InquiryForm(forms.Form):
    name = forms.CharField(label='お名前', max_length=50)
    email = forms.EmailField(label='メールアドレス')
    title = forms.CharField(label='タイトル', max_length=50)
    message = forms.CharField(label='メッセージ', widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def send_email(self):
        """メール送信処理"""

        # ユーザー入力値の取得
        # self.cleaned_data['<フィールド名>'] とすることで、フォームバリデーションを通ったユーザー入力値を取得できる.
        name = self.cleaned_data['name']
        email = self.cleaned_data['email']
        title = self.cleaned_data['title']
        message = self.cleaned_data['message']

        # メール送信情報
        subject = f'お問合せ {title}'
        message = (
            '送信者: {}\n'.format(name) + 
            'メールアドレス: {}\n'.format(email) + 
            'メッセージ:\n{}'.format(message)
        )
        from_email = 'yamashi7227.04020105.7227@outlook.jp'
        to_list = ['yamashi7227.04020105.7227@outlook.jp']
        cc_list = [email]

        # メール送信（EmailMessageオブジェクトのインスタンス化 -> 送信）
        message = EmailMessage(subject=subject, body=message, from_email=from_email, to=to_list, cc=cc_list)
        message.send()
