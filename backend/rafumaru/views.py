from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpRequest
from . import models
from .serializers import UserSerializer

from .models import User, Category, Accountbook, Gp, Member, Shareaccountbook, Public, Comment, Notice, Prefectures, Chat
from django.db.models import Sum, Case, When, IntegerField, F
from django.utils import timezone
from datetime import datetime, date
from collections import defaultdict
import pandas as pd

from django.conf import settings
from django.core.mail import EmailMessage

import random
from django.contrib.auth.hashers import make_password, check_password

from django.contrib.auth import authenticate, login

from math import isnan, isinf
import re


# ユーザーログイン
@api_view(['GET', "POST"])
def login(request):
    user_id = request.data.get("user", None)
    password = request.data.get("pass", None)

    user = models.User.objects.filter(user_id = user_id)
    try:
        for i in user:
            hash_pass = i.password
        is_true = check_password(password, hash_pass)
    except:
        data = {"message":"error"}
        return Response(data)

    if is_true:
        data = {
            "user_id":f"{user[0].user_id}",
            "mail_address":f"{user[0].mail_address}",
            "password":f"{user[0].password}",
            "nickname":f"{user[0].nickname}",
            "last_login":f"{user[0].last_login}",
            "message":"success",
        }
    else:
        data = {"message":"error"}
    return Response(data)


# ユーザー登録
@api_view(['GET', "POST"])
def register(request):
    user_id = request.data.get("user_id", None)
    mail_address = request.data.get("mail_address", None)
    password = request.data.get("password", None)
    nick_name = request.data.get("nick_name", None)
    last_login = request.data.get("last_login", None)

    check_dupli = False
    test_data = models.User.objects.filter(user_id=user_id)
    for i in test_data:
        check_dupli = True
    test_data = models.User.objects.filter(mail_address=mail_address)
    for i in test_data:
        check_dupli = True
    if check_dupli:
        return Response({"message":"IDまたはメールアドレスがすでに登録済みです。"}, status=201)
    else:
        models.User.objects.create_user(user_id, mail_address, password, nick_name, last_login)
        data = {
            "user_id":user_id,
            "mail_address":mail_address,
            "password":password,
            "nickname":nick_name,
            "last_login":last_login,
            "message":"success",
        }
        return Response(data)


# ユーザーパスワード確認
@api_view(['GET', "POST"])
def check_pass(request):
    password = request.data.get("pass", None)
    hash_password = request.data.get("hash_pass", None)
    is_true_pass = check_password(password, hash_password)
    data ={"result":f"{is_true_pass}"}
    return Response(data)


# パスワードリセットメール
@api_view(['GET', "POST"])
def password_reset(request):
    user_id = request.data.get("user_id")
    print(f"Received user id: {user_id}")
    code = random.randint(100000, 999999) # ランダムで認証コード生成

    try:
        user = User.objects.get(user_id=user_id)

        if not User.objects.filter(user_id=user_id).exists():
            return Response({"error": "User does not exist"}, status=404)
        
        email = user.mail_address # メールアドレスを取得する

        subject = "[らふまる]認証コード"
        body = f"""
        <h1>パスワードリセット用認証コード</h1>
        <p>認証コード：{code}</p>
        <p>ご確認ください。</p>
        """
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [email]
        email = EmailMessage(subject, body, from_email, to_email,)
        email.content_subtype = 'html'  # HTMLメールとして設定
        email.send()
        print(f"Received email: {email}")
        print(code)
        
        request.session['user_id'] = user_id
        request.session['code'] = code

        return Response({"code": code, "user_id": user_id}, status=200)
    
    except User.DoesNotExist:
        return Response(status=400)


# 認証コード確認
@api_view(['GET', "POST"])
def attestation_cd(request):
    code = request.data.get('code') # 生成されたコードを受け取り
    user_id = request.data.get('user_id') # ユーザーIDを受け取り
    attestation_cd = request.data.get('attestation_cd') # Streamlitから受け取ったデータ

    print(f"Stored code: {code}")
    print(f"Received code: {attestation_cd}")
    print(f"{user_id}")

    request.session['user_id'] = user_id

    if str(code) == str(attestation_cd):
        return Response({"user_id": user_id}, status=200)
    else:
        return Response({"code": code, "user_id": user_id},status=400)


# パスワードリセット
@api_view(['GET', "POST"])
def new_pw(request):
    user_id = request.data.get('user_id')
    new_pass = request.data.get('new_pass') # Streamlitからパスワードを取得する

    print(user_id)
    print(new_pass)

    try:
        user = User.objects.get(user_id=user_id)
        hashed_password = make_password(new_pass)
        user.password = hashed_password
        user.save()

        return Response(status=200)
    except User.DoesNotExist:
        return Response(status=404)


# アカウント削除
@api_view(['GET', "POST"])
def delete_account(request):
    user_id = request.data.get('user_id')

    try:
        # 通知
        notice_delete = Notice.objects.filter(re_user_id=user_id)
        notice_delete.delete()

        # 個人家計簿
        account_book_delete = Accountbook.objects.filter(user_id=user_id)

        # 公開
        public_delete = Public.objects.filter(public_id__in=account_book_delete.values_list('public_no', flat=True))
        public_delete.delete()
        account_book_delete.delete()

        # コメント
        Comment.objects.filter(user_id=user_id).delete()

        # グループ
        member_delete = Member.objects.filter(user_id=user_id)
        gp_ids = member_delete.values_list('gp_id', flat=True)

        # 該当グループにメンバーが存在してない場合
        for gp_id in gp_ids:
            if not Member.objects.filter(gp_id=gp_id).exists():
                Gp.objects.filter(gp_id=gp_id).delete()
        member_delete.delete()

        share_account_book_delete = Shareaccountbook.objects.filter(user_id=user_id)
        share_account_book_delete.delete()

        user_delete = User.objects.get(user_id=user_id)
        print(user_delete)
        user_delete.delete()

        return Response(status=200)
    
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    except Exception as e:
        print(f"An error occurred: {e}")
        return Response({"error": f"An unexpected error occurred: {e}"}, status=500)

# 個人情報修正
@api_view(['GET', "POST"])
def rev_account(request):
    user_id = request.data.get('user_id')
    nickname = request.data.get('nickname')
    email = request.data.get('email')

    try:
        user_info = User.objects.get(user_id=user_id)
        user_info.nickname = nickname
        user_info.mail_address = email
        user_info.save()

        return Response(status=200)

    except Exception as e:
        print(f"An error occurred: {e}")
        return Response({"error": f"An unexpected error occurred: {e}"}, status=500)

# 通知登録
@api_view(["GET", "POST"])
def notice_input(request):
    user_id = request.data.get("user_id")
    group_id = request.data.get("group_id")
    re_user_id = request.data.get("re_user_id")
    status = request.data.get("status")
    notice_date = timezone.localtime(timezone.now())

    try:
        user = User.objects.get(user_id=user_id)
        group = Gp.objects.get(gp_id=group_id)

        if Member.objects.filter(gp_id=group_id, user_id=re_user_id).exists():
            return Response({"reply": "このユーザーはすでにグループのメンバーです。"}, status=201)

        if not User.objects.filter(user_id=re_user_id).exists():
            return Response({"reply": "指定されたユーザーIDが見つかりません。"}, status=202)

        if status == "group_invite":
            notice_title = f"{user_id}（{user.nickname}さん）からのグループ招待です！"
            notice_content = f"""
            こんにちは！{user.nickname}さんからのグループ招待連絡です。\n
            グループ番号は{group_id}、パスワードは{group.gp_pw}です。\n
            ぜひご加入いただければ嬉しいです。
            """

        Notice.objects.create(
            user_id = user_id, # 送信
            re_user_id = re_user_id, # 受信
            notice_title = notice_title,
            notice_content = notice_content,
            notice_date = notice_date
        )

        return Response({"reply": "送信成功しました。"},status=200)
    except Exception:
        return Response(status=404)
    
# 通知表示
@api_view(["GET", "POST"])
def notice_view(request):
    re_user_id = request.data.get("user_id")

    try:
        notice_data = Notice.objects.filter(re_user_id=re_user_id)

        data = []
        for notice in notice_data:
            notices = {
                "user_id": notice.user_id,
                "re_user_id": notice.re_user_id,
                "notice_id": notice.notice_id,
                "notice_title": notice.notice_title,
                "notice_content": notice.notice_content,
                "notice_date": notice.notice_date, 
            }
            data.append(notices)


        return Response(data, status=200)
    except Exception:
        return Response(status=404)


# 通知削除・拒否
@api_view(["GET", "POST"])
def notice_delete(request):
    re_user_id = request.data.get("user_id")
    notice_id = request.data.get("notice_id")

    try:
        item = Notice.objects.get(re_user_id=re_user_id, notice_id=notice_id)
        item.delete()

        return Response(status=200)
    except Notice.DoesNotExist:
        return Response(status=404)
    
# 通知のグループ取得
@api_view(["GET", "POST"])
def notice_gp(request):
    re_user_id = request.data.get("user_id")
    notice_id = request.data.get("notice_id")

    try:
        item = Notice.objects.get(re_user_id=re_user_id, notice_id=notice_id)

        pattern = r"グループ番号は\s*(\d+)\s*、パスワードは\s*(\d+)\s*です。"
        match = re.search(pattern, item.notice_content)

        if match:
            gp_id = match.group(1)  # Group ID
            gp_pw = match.group(2)  # Group Password
        
        gp_confirm = Gp.objects.filter(gp_id=gp_id, gp_pw=gp_pw)
        if not gp_confirm.exists():
            return Response({"status": "success"}, status=201)
        
        return Response({"gp_id": gp_id, "gp_pw": gp_pw}, status=200)
    except Notice.DoesNotExist:
        return Response(status=404)

# 共同機能
# カテゴリ取得
@api_view(["GET", "POST"])
def get_category(request):
    categories = Category.objects.all()
    data = []
    for categorie in categories:
        category_data = {
            "id": categorie.category_id,
            "name": categorie.category_name,
        }
        data.append(category_data)
    return Response(data)


# カテゴリ別計算
@api_view(["GET", "POST"])
def category_total(request):
    user_id = request.data.get('user_id')
    year = request.data.get('year')
    month = request.data.get('month')
    week = request.data.get('week')

    # 当月のユーザーデータをすべて取得する
    try:
        # 当月のユーザーデータをすべて取得する
        account_book = Accountbook.objects.filter(
            user_id=user_id,
            date__year=year,
            date__month=month
        )

        if not account_book.exists():
            category_total_result = []
            return Response(category_total_result,status=200)

        # Pandasを使用する用の前処理（dateをdatetime型に変更）
        data = [{"item_no": item.item_no, "date": item.date, "public_no": item.public_no, "public": item.public, "category_id": item.category_id, "amount": item.amount} for item in account_book]
        df = pd.DataFrame(data)

        # 週ごと処理
        df['date'] = pd.to_datetime(df['date'])
        df['week'] = df['date'].dt.day.apply(lambda x: (x - 1) // 7 + 1)

        # 週計算
        if week:
            week_entries = df[df['week'] == week]
            category_total = week_entries.groupby('category_id').agg(total_amount=('amount', 'sum')).reset_index()
        # 月計算
        else:
            category_total = df.groupby('category_id').agg(total_amount=('amount', 'sum')).reset_index()

        # カテゴリ取得
        categories = Category.objects.all()
        category_dict = {category.category_id: category.category_name for category in categories}

        # カテゴリ計算結果を保存
        category_total_result = []
        for category_id, category_name in category_dict.items():
            total_amount = next((cat['total_amount'] for cat in category_total.to_dict(orient='records') if cat['category_id'] == category_id), 0)
            category_total_result.append({
                "category_id": category_id,
                "category_name": category_name,
                "total_amount": total_amount
            })

        return Response(category_total_result, status=200)

    except Category.DoesNotExist or Accountbook.DoesNotExist:
        return Response(status=404)


# カテゴリ別計算・共同家計簿
@api_view(["GET", "POST"])
def category_total_group(request):
    group_id = request.data.get('group_id')
    year = request.data.get('year')
    month = request.data.get('month')

    # 当月のユーザーデータをすべて取得する
    try:
        account_book = Shareaccountbook.objects.filter(
            gp_id = group_id,
            date__year=year,
            date__month=month
        )

        # カテゴリ別計算
        category_total = account_book.values('category_id').annotate(total_amount=Sum('amount'))

        # カテゴリ取得
        categories = Category.objects.all()
        category_dict = {category.category_id: category.category_name for category in categories}

        # カテゴリ計算結果を保存
        category_total_result = []
        for category_id, category_name in category_dict.items():
            total_amount = next((cat['total_amount'] for cat in category_total if cat['category_id'] == category_id), 0)
            category_total_result.append({
                "category_id": category_id,
                "category_name": category_name,
                "total_amount": total_amount
            })

        return Response(category_total_result, status=200)
    except Category.DoesNotExist or Accountbook.DoesNotExist:
        return Response(status=404)


# 都道府県取得
@api_view(["GET", "POST"])
def get_prefecture(request):
    prefectures = Prefectures.objects.all()
    prefecture_data = []
    for prefecture in prefectures:
        data = {
            "prefecture_id": prefecture.id,
            "prefecture_name": prefecture.prefecture_name,
            "block_name": prefecture.block_name,
        }
        prefecture_data.append(data)

    return Response(prefecture_data)


# 個人家計簿：収支入力
@api_view(['GET', "POST"])
def account_book_input(request):
    user_id = request.data.get('user_id')
    category_id = request.data.get('category_id')
    amount = request.data.get('amount')
    date = request.data.get('date')
    memo = request.data.get('memo')
    
    try:
        new_date = pd.to_datetime(date)
        new_month = new_date.month
        new_year = new_date.year

        monthly_data = Accountbook.objects.filter(
            user_id=user_id, 
            date__year=new_year, 
            date__month=new_month
        )

        # Pandasを使用する用の前処理（dateをdatetime型に変更）
        data = [{"item_no": item.item_no, "date": item.date, "public_no": item.public_no, "public": item.public,} for item in monthly_data]
        df = pd.DataFrame(data)

        # 公開情報番号のデフォルト設定
        public = False
        public_no = None

        # 当週のデータ確認
        if df.empty:
            public = False
        else:
            # 週ごと処理
            df['date'] = pd.to_datetime(df['date'])
            df['week'] = df['date'].dt.day.apply(lambda x: (x - 1) // 7 + 1)

            new_item_week = (new_date.day - 1) // 7 + 1
            week_entries = df[df['week'] == new_item_week]

            if not week_entries.empty:
                for entry in week_entries.itertuples():
                    if entry.public and entry.public_no is not None:  # 公開中、公開情報番号あり
                        public_no = entry.public_no
                        public = True
                        break
                    elif not entry.public and entry.public_no is not None:  # 未公開、公開情報番号なし
                        public = False
                        break
                else:
                    # データなし
                    public = False
            else:
                # 当週のデータのデータなし
                public = False


        # データベースに登録する
        new_entry = Accountbook.objects.create(
            user_id = user_id,
            category_id = category_id,
            amount = amount,
            public = public, # 公開状態設定
            date = date,
        )

        # 公開情報番号ある場合、設定する
        if public_no:
            new_entry.public_no = public_no
            new_entry.save()
        
        if memo:
            new_entry.memo = memo
            new_entry.save()
        


        return Response(status=200)
    except User.DoesNotExist or Accountbook.DoesNotExist:
        return Response(status=404)


# 個人家計簿：収支参照（当月の収支参照表示）
@api_view(['GET', "POST"])
def account_book(request):
    user_id = request.data.get('user_id')
    year = request.data.get('year')
    month = request.data.get('month')
    today = request.data.get('today')

    try:
        # 当月のユーザーデータをすべて取得する
        account_book = Accountbook.objects.filter(
            user_id = user_id,
            date__year=year,
            date__month=month
        )

        # カテゴリロジック設定
        account_book = account_book.annotate(
            adjusted_amount=Case(
                When(category_id=1, then=F('amount')),  #収入(category=1)なら足す
                default=-1 * F('amount'),  # その他のカテゴリなら減らす
                output_field=IntegerField(),
            )
        )
        today_date = datetime.strptime(today, "%Y-%m-%d").date()
        
        # 当月の総計
        total_month = account_book.aggregate(total_month_amount=Sum('adjusted_amount'))['total_month_amount']
        
        # 今週の総計
        start_of_week = today_date - timezone.timedelta(days=today_date.weekday())
        weekly_data = account_book.filter(date__gte=start_of_week, date__lte=today_date)
        total_week_today = weekly_data.aggregate(total_week_today_amount=Sum('adjusted_amount'))['total_week_today_amount']

        # 今日の総計
        total_today = account_book.filter(date=today_date).aggregate(total_today_amount=Sum('adjusted_amount'))['total_today_amount']

        # 総計をリストに保存する
        response_data = {
            "total_month": total_month if total_month is not None else 0,
            "total_today": total_today if total_today is not None else 0,
            "total_week_today": total_week_today if total_week_today is not None else 0,
        }

        return Response(response_data, status=200)
    
    except Accountbook.DoesNotExist:
        return Response(status=400)
    
# 個人家計簿：収支詳細参照
@api_view(['GET', "POST"])
def account_book_detail(request):
    user_id = request.data.get('user_id')
    year = request.data.get('year')
    month = request.data.get('month')
    input_date = request.data.get('date')

    try:
        # 当月のユーザーデータをすべて取得する
        if input_date is not None:
            account_book_detail = Accountbook.objects.filter(
                user_id=user_id,
                date=input_date
            )
        else:
            account_book_detail = Accountbook.objects.filter(
                user_id=user_id,
                date__year=year,
                date__month=month
            )

        # カテゴリ取得
        categories = Category.objects.all()
        category_dict = {category.category_id: category.category_name for category in categories}

        # カテゴリロジック設定
        account_book_detail = account_book_detail.annotate(
            adjusted_amount=Case(
                When(category_id=1, then=F('amount')),  #収入(category=1)なら足す
                default=-1 * F('amount'),  # その他のカテゴリなら減らす
                output_field=IntegerField(),
            )
        )

        # データをリストに保存する
        account_book_detail_data = []
        for detail_data in account_book_detail:
            data = {
                "user_id": detail_data.user_id,
                "item_no": detail_data.item_no,
                "category_id": detail_data.category_id,
                "category_name": category_dict.get(detail_data.category_id, 'Unknown'),
                "amount": detail_data.amount,
                "adjusted_amount": detail_data.adjusted_amount, # ロジックより修正金額
                "memo": detail_data.memo,
                "date": detail_data.date,
            }
            account_book_detail_data.append(data)

        # Pandasを使用する用の前処理（dateをdatetime型に変更）
        for item in account_book_detail_data:
            if isinstance(item['date'], date):
                item['date'] = datetime.combine(item['date'], datetime.min.time())
        df = pd.DataFrame(account_book_detail_data)

        # 当月のデータが存在してない場合、空白のデータを返す
        if 'date' not in df.columns:
            return Response({'weekly_data': {}, 'weekly_totals': {}})
        
        # 週ごと処理
        df['week'] = df['date'].apply(lambda x: (x.day - 1) // 7 + 1) # 週番号は1から

        weekly_data = {}
        weekly_totals = {}
        for week, group in df.groupby('week'):
            week_data = group.drop(columns=['week']).to_dict(orient='records')
            for item in week_data: # datatime型からdate型に戻す
                item['date'] = item['date'].date()

            # 週総計
            week_total = group['adjusted_amount'].sum()

            weekly_data[week] = week_data
            weekly_totals[week] = week_total

        response_data = {
            "weekly_data": weekly_data,  # 週詳細
            "weekly_totals": weekly_totals  # 週総計
        }

        return Response(response_data, status=200)
    
    except Accountbook.DoesNotExist or Category.DoesNotExist:
        return Response(status=400)

# 個人家計簿：収支更新
@api_view(['GET', "POST"])
def account_book_item_update(request):
    user_id = request.data.get('user_id')
    item_no = request.data.get('item_no')
    updated_date = request.data.get('date')
    updated_category_id = request.data.get('category_id')
    updated_amount = request.data.get('amount')
    updated_memo = request.data.get('memo')

    # 項目更新
    try:
        item = Accountbook.objects.get(user_id=user_id, item_no=item_no)
        item.date = updated_date
        item.category_id = updated_category_id
        item.amount = updated_amount
        item.memo = updated_memo
        item.save()

        return Response(status=200)
    except Accountbook.DoesNotExist:
        return Response(status=404)

# 個人家計簿：収支削除
@api_view(['GET', "POST"])
def account_book_item_delete(request):
    user_id = request.data.get('user_id')
    item_no = request.data.get('item_no')

    # 項目削除
    try:
        item = Accountbook.objects.get(user_id=user_id, item_no=item_no)
        item.delete()

        return Response(status=200)
    except Accountbook.DoesNotExist:
        return Response(status=404)
    
# 共同家計簿：グループ一覧
@api_view(['GET', "POST"])
def group(request):
    user_id = request.data.get('user_id')
    try:
        # ユーザーが所属グループを取得
        user_groups = Member.objects.filter(user_id=user_id)

        # グループリストに保存する
        member_group_list = []
        for user_group in user_groups:
            # グループの名前を取得する
            group = Gp.objects.get(gp_id=user_group.gp_id)
            data = {
                "group_id": group.gp_id,
                "group_name": group.gp_name,
                "income_input": group.income_input,
            }
            member_group_list.append(data)

        return Response(member_group_list, status=200)

    except Gp.DoesNotExist:
        return Response(status=404)
    
# 共同家計簿：グループ作成
@api_view(['GET', "POST"])
def group_create(request):
    user_id = request.data.get('user_id')
    group_name = request.data.get('group_name')
    group_password = request.data.get('group_password')
    income_input = request.data.get('income_input')

    # データベースに登録する
    try:
        # グループ番号の重複確認
        gp_id = None
        while True:
            gp_id = random.randint(100000000, 999999999)
            if not Gp.objects.filter(gp_id=gp_id).exists():
                break

        # グループを登録
        group = Gp.objects.create(
            gp_id = gp_id,
            gp_name = group_name,
            gp_pw = group_password,
            income_input = income_input, 
        )
        # メンバーを登録
        Member.objects.create(
            gp_id = group.gp_id,
            user_id = user_id
        )
        return Response(status=200)
    except Gp.DoesNotExist or Member.DoesNotExist:
        return Response(status=404)

# 共同家計簿：グループ削除
@api_view(['GET', "POST"])
def group_delete(request):
    user_id = request.data.get('user_id')
    group_id = request.data.get('group_id')

    # 項目削除
    try:
        Shareaccountbook.objects.filter(user_id=user_id, gp_id=group_id).delete()
        Member.objects.filter(user_id=user_id, gp_id=group_id).delete()
        # 該当グループにメンバーが存在してない場合
        if not Member.objects.filter(gp_id=group_id).exists():
            Chat.objects.filter(gp_id=group_id).delete() # チャット記録を削除
            Gp.objects.filter(gp_id=group_id).delete() # グループを削除

            # 共同家計簿を削除
            Shareaccountbook.objects.filter(gp_id=group_id).delete()

        return Response(status=200)

    except Gp.DoesNotExist or Member.DoesNotExist or Shareaccountbook.DoesNotExist:
        return Response(status=404)
    
# 共同家計簿：グループ加入
@api_view(['GET', "POST"])
def group_add(request):
    user_id = request.data.get('user_id')
    group_id = request.data.get('group_id')
    group_password = request.data.get('group_password')

    try:
        if Gp.objects.filter(gp_id=group_id, gp_pw=group_password).exists():
            if not Member.objects.filter(gp_id=group_id, user_id=user_id).exists():
                # メンバーを登録
                Member.objects.create(
                    gp_id = group_id,
                    user_id = user_id
                )
                return Response(status=200)
            else:
                return Response(status=201) # 存在しているユーザーを登録しない
        else:
            return Response(status=202) # グループ番号、またはパスワードが間違っている
    except Gp.DoesNotExist or Member.DoesNotExist or Shareaccountbook.DoesNotExist:
        return Response(status=404)
    
# 共同家計簿：参照
@api_view(['GET', "POST"])
def share_account_book(request):
    user_id = request.data.get('user_id')
    group_id = request.data.get('group_id')
    year = request.data.get('year')
    month = request.data.get('month')
    today = request.data.get('today')

    try:
        # 当月のユーザーデータをすべて取得する
        account_book = Shareaccountbook.objects.filter(
            gp_id = group_id,
            date__year=year,
            date__month=month
        )

        # カテゴリロジック設定
        account_book = account_book.annotate(
            adjusted_amount=Case(
                When(category_id=1, then=F('amount')),  #収入(category=1)なら足す
                default=-1 * F('amount'),  # その他のカテゴリなら減らす
                output_field=IntegerField(),
            )
        )
        today_date = datetime.strptime(today, "%Y-%m-%d").date()
        
        # 当月の総計
        total_month = account_book.aggregate(total_month_amount=Sum('adjusted_amount'))['total_month_amount']
        
        # 今週の総計
        start_of_week = today_date - timezone.timedelta(days=today_date.weekday())  # 月曜日を週の初日に設定
        weekly_data = account_book.filter(date__gte=start_of_week, date__lte=today_date)
        total_week_today = weekly_data.aggregate(total_week_today_amount=Sum('adjusted_amount'))['total_week_today_amount']

        # 今日の総計
        total_today = account_book.filter(date=today_date).aggregate(total_today_amount=Sum('adjusted_amount'))['total_today_amount']

        # ユーザー別の計算
        user_data = defaultdict(lambda: {"total_month": 0, "total_income": 0, "total_expense": 0})
        for user_entry in account_book.values('user_id').distinct():
            user_id = user_entry['user_id']
            nickname = User.objects.filter(user_id=user_id).values_list('nickname', flat=True).first()

            # 各ユーザーの当月の総計
            user_total_month = account_book.filter(user_id=user_id).aggregate(total=Sum('adjusted_amount'))['total']
            # 各ユーザーの収入合計 (category_id=1)
            user_total_income = account_book.filter(user_id=user_id, category_id=1).aggregate(total=Sum('amount'))['total']
            # 各ユーザーの支出合計 (その他のカテゴリ)
            user_total_expense = account_book.filter(user_id=user_id).exclude(category_id=1).aggregate(total=Sum('amount'))['total']

            #ユーザーデータをリストに保存する
            user_data[user_id]["user_id"] = user_id if user_id else "Unknown"
            user_data[user_id]["nickname"] = nickname if nickname else "Unknown"
            user_data[user_id]["total_month"] = user_total_month if user_total_month else 0
            user_data[user_id]["total_income"] = user_total_income if user_total_income else 0
            user_data[user_id]["total_expense"] = user_total_expense if user_total_expense else 0

        # グループ内のメンバーがデータを入力してない場合、0表示の設定
        members = Member.objects.filter(gp_id=group_id)
        for member in members:
            if member.user_id not in user_data:
                user = User.objects.filter(user_id=member.user_id).first()
                user_data[member.user_id] = {
                    "nickname": user.nickname if user else "Unknown",
                    "total_month": 0,
                    "total_income": 0,
                    "total_expense": 0
                }

        # 総計をリストに保存する
        response_data = {
            "total_month": total_month if total_month is not None else 0,
            "total_today": total_today if total_today is not None else 0,
            "total_week_today": total_week_today if total_week_today is not None else 0,
            "user_data": user_data,
        }

        return Response(response_data, status=200)
    
    except Accountbook.DoesNotExist:
        return Response(status=400)


# 共同家計簿：入力
@api_view(['GET', "POST"])
def share_account_book_input(request):
    group_id = request.data.get('group_id')
    user_id = request.data.get('user_id')
    category_id = request.data.get('category_id')
    amount = request.data.get('amount')
    date = request.data.get('date')
    memo = request.data.get('memo')
    
    # データベースに登録する
    try:
        share_account_book = Shareaccountbook.objects.create(
            user_id = user_id,
            category_id = category_id,
            amount = amount,
            gp_id = group_id,
            date = date,
        )

        if memo:
            share_account_book.memo = memo
            share_account_book.save()

        return Response(status=200)
    except User.DoesNotExist:
        return Response(status=404)


# 共同家計簿：詳細参照
@api_view(['GET', "POST"])
def share_account_book_detail(request):
    group_id = request.data.get('group_id')
    year = request.data.get('year')
    month = request.data.get('month')
    input_date = request.data.get('date')

    try:
        # 当月のユーザーデータをすべて取得する
        if input_date is not None:
            share_account_book_detail = Shareaccountbook.objects.filter(
                gp_id=group_id,
                date=input_date
            )

        else:
            share_account_book_detail = Shareaccountbook.objects.filter(
                gp_id=group_id,
                date__year=year,
                date__month=month
            )

        # カテゴリ取得
        categories = Category.objects.all()
        category_dict = {category.category_id: category.category_name for category in categories}

        # ユーザー名前を取得
        users = User.objects.all()
        user_dict = {user.user_id: user.nickname for user in users}

        # カテゴリロジック設定
        share_account_book_detail = share_account_book_detail.annotate(
            adjusted_amount=Case(
                When(category_id=1, then=F('amount')),  #収入(category=1)なら足す
                default=-1 * F('amount'),  # その他のカテゴリなら減らす
                output_field=IntegerField(),
            )
        )

        # データをリストに保存する
        account_book_detail_data = []
        for detail_data in share_account_book_detail:
            data = {
                "user_id": detail_data.user_id,
                "nickname": user_dict.get(detail_data.user_id,'Unknown'),
                "group_id": detail_data.gp_id,
                "shareditem_id": detail_data.shareditem_id,
                "category_id": detail_data.category_id,
                "category_name": category_dict.get(detail_data.category_id, 'Unknown'),
                "amount": detail_data.amount,
                "adjusted_amount": detail_data.adjusted_amount, # ロジックより修正金額
                "date": detail_data.date,
                "memo": detail_data.memo,
            }
            account_book_detail_data.append(data)

        # Pandasを使用する用の前処理（dateをdatetime型に変更）
        for item in account_book_detail_data:
            if isinstance(item['date'], date):
                item['date'] = datetime.combine(item['date'], datetime.min.time())
        df = pd.DataFrame(account_book_detail_data)

        # 当月のデータが存在してない場合、空白のデータを返す
        if 'date' not in df.columns:
            return Response({'weekly_data': {}, 'weekly_totals': {}})
        
        # 週ごと処理
        df['week'] = df['date'].apply(lambda x: (x.day - 1) // 7 + 1) # 週番号は1から

        weekly_data = {}
        weekly_totals = {}
        for week, group in df.groupby('week'):
            week_data = group.drop(columns=['week']).to_dict(orient='records')
            for item in week_data: # datatime型からdate型に戻す
                item['date'] = item['date'].date()

            # 週総計
            week_total = group['adjusted_amount'].sum()

            weekly_data[week] = week_data
            weekly_totals[week] = week_total

        response_data = {
            "weekly_data": weekly_data,  # 週詳細
            "weekly_totals": weekly_totals  # 週総計
        }


        return Response(response_data, status=200)
    
    except Accountbook.DoesNotExist or Category.DoesNotExist:
        return Response(status=400)
    

# 共同家計簿：収支更新
@api_view(['GET', "POST"])
def share_account_book_item_update(request):
    group_id = request.data.get('group_id')
    user_id = request.data.get('user_id')
    shareditem_id = request.data.get('shareditem_id')
    updated_date = request.data.get('date')
    updated_category_id = request.data.get('category_id')
    updated_amount = request.data.get('amount')
    updated_memo = request.data.get('memo')

    # 項目更新
    try:
        item = Shareaccountbook.objects.get(gp_id=group_id, user_id=user_id, shareditem_id=shareditem_id)
        item.date = updated_date
        item.category_id = updated_category_id
        item.amount = updated_amount
        item.memo = updated_memo
        item.save()

        return Response(status=200)
    except Accountbook.DoesNotExist:
        return Response(status=404)

# 共同家計簿：収支削除
@api_view(['GET', "POST"])
def share_account_book_item_delete(request):
    group_id = request.data.get('group_id')
    user_id = request.data.get('user_id')
    shareditem_id = request.data.get('shareditem_id')


    # 項目削除
    try:
        item = Shareaccountbook.objects.filter(gp_id=group_id, user_id=user_id, shareditem_id=shareditem_id)
        item.delete()

        return Response(status=200)
    except Accountbook.DoesNotExist:
        return Response(status=404)

# 共同家計簿：収支分割計算
@api_view(['GET', "POST"])
def share_account_book_calculation(request):
    group_id = request.data.get('group_id')
    year = request.data.get('year')
    month = request.data.get('month')
    percentages = request.data.get('percent')

    try:
        # グループメンバーのデータを取得
        group_members = Member.objects.filter(gp_id=group_id).values_list('user_id', flat=True)

        # 共同家計簿のデータを取得
        share_account_book = Shareaccountbook.objects.filter(gp_id=group_id, date__year=year,date__month=month)

        # 各ユーザーの支出合計 (その他のカテゴリ)
        total_expense = share_account_book.exclude(category_id=1).aggregate(total=Sum('amount'))['total'] or 0

        result = []
        for user_id in group_members:
            print(user_id)
            user_income = share_account_book.filter(user_id=user_id, category_id=1).aggregate(total=Sum('amount'))['total'] or 0

            # ユーザー% 取得
            user_percent = percentages.get(str(user_id), 0)
            
            # 各ユーザー別の計算
            share_expense = int(total_expense * (user_percent / 100))
            
            share_result = user_income - share_expense # 負担額

            # リストに保存する
            result.append({
                'user_id': user_id,
                'share_income': round(user_income, 2),
                'share_expense': round(share_expense, 2),
                'share_result': round(share_result, 2),
            })

        return Response({'data': result}, status=200)
    except Shareaccountbook.DoesNotExist:
        return Response(status=404)

# 公開：公開一覧
@api_view(['GET', "POST"])
def public_all_contents(request):
    user_id = request.data.get('user_id')
    selected_date = request.data.get('selected_date')

    # 日付検索設定
    if selected_date:
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d")
        selected_week = (selected_date.day - 1) // 7 + 1
        selected_year = selected_date.year
        selected_month = selected_date.month
    else:
        selected_week = None
        selected_year = None
        selected_month = None
    
    # 投稿人設定
    if user_id:
        public_true_data = Accountbook.objects.filter(user_id=user_id, public=True)
    else:
        public_true_data = Accountbook.objects.filter(public=True)
    
    if selected_year and selected_month and selected_week:
        public_true_data = public_true_data.filter(date__year=selected_year, date__month=selected_month)
        public_true_data = public_true_data.filter(date__day__gte=(selected_week - 1) * 7 + 1)
        public_true_data = public_true_data.filter(date__day__lt=selected_week * 7 + 1)

    if not public_true_data.exists():
        grouped_data_serialized=[]
        return Response(grouped_data_serialized, status=200)

    data = []
    for entry in public_true_data:
        user = User.objects.get(user_id=entry.user_id)
        public = Public.objects.get(public_id=entry.public_no)
        prefecture = Prefectures.objects.get(id=public.prefecture_id)

        data.append({
                "user_id": user.user_id,
                "nickname": user.nickname,
                "public_no": entry.public_no,
                "title": public.title if public.title else "タイトルなし",
                "date": entry.date,
                "item_no": entry.item_no,
                "category_id": entry.category_id,
                "prefecture_id": prefecture.id,
                "prefecture_name": prefecture.prefecture_name,
            })

    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])

    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['week'] = df['date'].dt.day.apply(lambda x: (x - 1) // 7 + 1)

    # 週データ確認
    for user in df['user_id'].unique():
        user_data = df[df['user_id'] == user]
        unique_weeks = user_data['week'].unique()
        for week_num in unique_weeks:
            week_entries = user_data[user_data['week'] == week_num]
            
            # 当週は全部「収入」の場合、公開状態「未公開」に設定する
            if all(week_entries['category_id'] == 1):
                for entry in week_entries.itertuples():
                    accountbook_entry = Accountbook.objects.get(item_no=entry.item_no)
                    if accountbook_entry.public:
                        accountbook_entry.public = False
                        accountbook_entry.save()

    grouped_data = df.groupby(['user_id', 'year', 'month', 'week']).apply(lambda x: x[['user_id', 'nickname', 'title', 'year', 'month', 'week', 'public_no', 'prefecture_id', 'prefecture_name']].drop_duplicates().to_dict(orient="records")).to_dict()
    grouped_data_serialized = {f"{key[0]}-{key[1]}-{key[2]}-{key[3]}": value for key, value in grouped_data.items()}

    return Response(grouped_data_serialized, status=200)


# InfinityやNaNなどのNull処理
def clean_value(value):
    if isinstance(value, float) and (isnan(value) or isinf(value)):
        return None
    return value

# 公開：公開情報一覧
@api_view(['GET', "POST"])
def public_status(request):
    user_id = request.data.get('user_id')
    year = request.data.get('year')
    month = request.data.get('month')
    week_num = int(request.data.get('week'))
    
    try:
        monthly_data = Accountbook.objects.filter(
            user_id=user_id,
            category_id__gt = 1, # category_id 1以上のデータ取得
            date__year=year,
            date__month=month,
        )

        # 当月のデータ確認
        if not monthly_data.exists():
            return Response({"status": "データなし", "title": None}, status=200)

        # Pandasを使用する用の前処理（dateをdatetime型に変更）
        data = [{"item_no": item.item_no, "date": item.date, "public_no": item.public_no, "public": item.public}for item in monthly_data]
        df = pd.DataFrame(data)

        # 週ごと処理
        df['date'] = pd.to_datetime(df['date'])
        df['week'] = df['date'].dt.day.apply(lambda x: (x - 1) // 7 + 1)
        week_entries = df[df['week'] == week_num]

        # データあり
        if not week_entries.empty:
            entry = week_entries.iloc[0]
            public_status = entry['public'] # 公開状態
            public_no = entry["public_no"] # 公開情報番号
            title = None
            prefecture_id = 48
            if not pd.isna(public_no):
                public_entry = Public.objects.filter(public_id=entry['public_no']).first()
                title = public_entry.title if public_entry else None
                prefecture_id = public_entry.prefecture_id if public_entry else None

            # データ再処理
            response_data = {
                "public": clean_value(public_status),
                "status": "公開中" if public_status else "未公開",
                "title": clean_value(title),
                "public_no": clean_value(public_no),
                "prefecture_id": prefecture_id,
            }

            return Response(response_data, status=200)
        # データなし
        else:
            return Response({"status": "データなし"}, status=200)
        
    except Exception as e:
        return Response({"status": "error"}, status=500)


# 公開：公開状態変更（支出登録）
@api_view(['GET', "POST"])
def public_setting(request):
    user_id = request.data.get('user_id')
    year = request.data.get('year')
    month = request.data.get('month')
    week_num = int(request.data.get('week'))
    public = request.data.get('public')
    title = request.data.get('title')
    prefecture_id = request.data.get('prefecture_id')

    try:
        monthly_data = Accountbook.objects.filter(
            user_id = user_id,
            date__year=year,
            date__month=month
        )

        # Pandasを使用する用の前処理（dateをdatetime型に変更）
        data = [{"item_no": item.item_no, "date": item.date, "public_no": item.public_no, "public": item.public} for item in monthly_data]
        df = pd.DataFrame(data)

        # 週ごと処理
        df['date'] = pd.to_datetime(df['date'])
        df['week'] = df['date'].dt.day.apply(lambda x: (x - 1) // 7 + 1)
        week_entries = df[df['week'] == week_num]

        # 当週のデータ存在してない場合スキップ
        if week_entries.empty:
            print(f"No data found for week {week_num}. Skipping.")
            return Response(status=200)
        
        existing_public_no = None # 現在の公開番号確認用

        # 公開状態確認
        for entry in week_entries.itertuples():
            accountbook_entry = Accountbook.objects.get(item_no=entry.item_no)
            if accountbook_entry.public_no:
                existing_public_no = accountbook_entry.public_no
                break
            
        if public == "true":  # 公開
            if existing_public_no:  # 公開番号が存在している場合
                public_id = existing_public_no
                # タイトル修正
                public_entry = Public.objects.get(public_id=existing_public_no)
                public_entry.title = title
                public_entry.prefecture_id = prefecture_id
                public_entry.save()

            else:  # 公開番号が存在しない場合
                new_public = Public.objects.create(title=title, prefecture_id=prefecture_id)
                public_id = new_public.public_id

            for entry in week_entries.itertuples():
                accountbook_entry = Accountbook.objects.get(item_no=entry.item_no)
                accountbook_entry.public_no = public_id
                accountbook_entry.public = True
                accountbook_entry.save()

            if not existing_public_no:
                public_entry = Public.objects.get(public_id=public_id)
                public_entry.title = title
                public_entry.prefecture_id=prefecture_id
                public_entry.save()

        elif public == "false":  # 未公開
            for entry in week_entries.itertuples():
                accountbook_entry = Accountbook.objects.get(item_no=entry.item_no)
                accountbook_entry.public = False
                accountbook_entry.save()

        return Response(status=200)

    except (Public.DoesNotExist, Accountbook.DoesNotExist) as e:
        return Response({"message": f"Error: {str(e)}"}, status=404)

    except Exception as e:
        return Response({"message": f"Unexpected error: {str(e)}"}, status=500)


# 公開：コメント作成
@api_view(['GET', "POST"])
def public_comment_input(request):
    user_id = request.data.get('user_id')
    public_no = request.data.get('public_no')
    comment = request.data.get('comment')

    try:
        Comment.objects.create(
            user_id = user_id,
            public_no = public_no,
            comment = comment,
            like_point = 0
        )
        return Response(status=200)
    except Comment.DoesNotExist:
        return Response(status=404)


# 公開：コメント削除
@api_view(['GET', "POST"])
def public_comment_delete(request):
    comment_id = request.data.get('comment_id')
    try:
        item = Comment.objects.get(comment_id=comment_id)
        item.delete()
        return Response(status=200)
    except Comment.DoesNotExist:
        return Response(status=404)


# 公開：コメント一覧
@api_view(['GET', "POST"])
def public_comment_detail(request):
    public_no = request.data.get('public_no')

    try:
        # コメント取得
        comment_data = Comment.objects.filter(public_no=public_no)
        
        if not comment_data.exists():
            return Response("status: no comment", status=200)

        # ユーザー名前を取得
        users = User.objects.all()
        user_dict = {user.user_id: user.nickname for user in users}
        
        all_comment_data = []
        for cm in comment_data:
            data = {
                "user_id": cm.user_id,
                "nickname": user_dict.get(cm.user_id,'Unknown'),
                "comment_id": cm.comment_id,
                "comment": cm.comment,
                "like_point": cm.like_point
            }
            all_comment_data.append(data)
        return Response(all_comment_data, status=200)
    except Comment.DoesNotExist or User.DoesNotExist:
        return Response(status=404)

# 公開：コメントいいね
@api_view(['GET', "POST"])
def public_like(request):
    comment_id = request.data.get('comment_id')

    try:
        # コメント取得
        comment_data = Comment.objects.get(comment_id=comment_id)
        
        like_point = comment_data.like_point
        like_point+=1

        comment_data.like_point = like_point
        comment_data.save()

        return Response(status=200)
    except Comment.DoesNotExist or User.DoesNotExist:
        return Response(status=404)


# チャット：入力
@api_view(['GET', "POST"])
def chat_input(request):
    group_id = request.data.get('group_id')
    user_id = request.data.get("user_id")
    chat = request.data.get("chat")
    chat_time = timezone.localtime(timezone.now())

    try:
        Chat.objects.create(
            gp_id = group_id,
            user_id = user_id,
            chat = chat,
            chat_time = chat_time,
        )
        return Response("status: chat", status=200)
    except Chat.DoesNotExist:
        return Response(status=404)


# チャット：表示
@api_view(['GET', "POST"])
def chat_view(request):
    group_id = request.data.get('group_id')

    try:
        chat_data = Chat.objects.filter(gp_id=group_id)
        user_dict = User.objects.all()

        data = []
        for chat in chat_data:
            user = user_dict.filter(user_id=chat.user_id).first()
            nickname = user.nickname if user else "名無しさん"

            chats = {
                "chat_id": chat.chat_id,
                "user_id": chat.user_id if chat.user_id else None,
                "nickname": nickname,
                "group_id": chat.gp_id,
                "chat": chat.chat,
                "chat_time": chat.chat_time,
            }
            data.append(chats)
        return Response(data, status=200)
    except Exception:
        return Response(status=404)