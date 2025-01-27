"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from . import views
from django.urls import path


urlpatterns = [
    # 新規登録
    path('register/', views.register, name='register'),

    # ログイン
    path('login/', views.login, name='login'),
    path('check_pass/', views.check_pass, name='check_pass'),

    # アカウント削除
    path('delete_account/', views.delete_account, name='delete_account'),

    # パスワードリセット
    path('password_reset/', views.password_reset, name='password_reset'), # パスワードリセットメール送信
    path('attestation_cd/', views.attestation_cd, name='attestation_cd'), # 認証コード確認
    path('new_pw/', views.new_pw, name='new_pw'), # パスワードリセットする

    # 通知
    path('notice_input/', views.notice_input, name='notice_input'), # 通知入力
    path('notice_view/', views.notice_view, name='notice_view'), # 通知一覧

    # 個人家計簿 と 共同家計簿　共有部分
    path('get_category/', views.get_category, name='get_category'), # カテゴリ取得
    path('category_total/', views.category_total, name='category_total'), # カテゴリ別の総計
    path('category_total_group/', views.category_total_group, name='category_total_group'), # 共同家計簿のカテゴリ別の総計


    # 個人家計簿
    path('account_book/', views.account_book, name='account_book'), # 当月の各収支表示
    path('account_book_detail/', views.account_book_detail, name='account_book_detail'), # 当月の各詳細収支表示
    path('account_book_input/', views.account_book_input, name='account_book_input'), # 収支登録
    path('account_book_item_update/', views.account_book_item_update, name='account_book_item_update'), # 収支更新
    path('account_book_item_delete/', views.account_book_item_delete, name='account_book_item_delete'), # 収支削除


    # 共同家計簿
    path('group/', views.group, name='group'), # グループ一覧
    path('group_create/', views.group_create, name='group_create'), # グループ作成
    path('group_delete/', views.group_delete, name='group_delete'), # グループ削除
    path('group_add/', views.group_add, name='group_add'), # グループ加入

    path('share_account_book/', views.share_account_book, name='share_account_book'), # 当月の各収支表示
    path('share_account_book_detail/', views.share_account_book_detail, name='share_account_book_detail'), # 当月の各詳細収支表示
    path('share_account_book_input/', views.share_account_book_input, name='share_account_book_input'), # 収支登録
    path('share_account_book_item_update/', views.share_account_book_item_update, name='share_account_book_item_update'), # 収支更新
    path('share_account_book_item_delete/', views.share_account_book_item_delete, name='share_account_book_item_delete'), # 収支削除
    path('share_account_book_calculation/', views.share_account_book_calculation, name='share_account_book_calculation'), # 収支分割計算

    # 公開
    path('public_all_contents/', views.public_all_contents, name='public_all_contents'), # 公開一覧
    path('public_status/', views.public_status, name='public_status'), # 公開状態一覧
    path('public_setting/', views.public_setting, name='public_setting'), # 公開状態変更（支出登録）
    path('public_comment_input/', views.public_comment_input, name='public_comment_input'), # コメント作成
    path('public_comment_delete/', views.public_comment_delete, name='public_comment_delete'), # コメント削除
    path('public_comment_detail/', views.public_comment_detail, name='public_comment_detail'), # コメント一覧
    path('public_like/', views.public_like, name='public_like'), # コメントいいね
]
