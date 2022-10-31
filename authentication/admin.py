from django.contrib import admin

from .models import CustomUser


# カスタムユーザーモデルを管理サイトで編集できるようにする.
admin.site.register(CustomUser)
