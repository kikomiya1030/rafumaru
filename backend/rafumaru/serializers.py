from . import models
# from django.contrib.auth.models import User
from rest_framework import serializers

from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):

    def __init__(self, *args, user_id, mail_address, password, nick_name, last_login, **kwargs):
        # デフォルトの初期化を呼び出し
        super().__init__(*args, **kwargs)
        
        self.user_id = user_id
        self.mail_address = mail_address
        self.password = make_password()
        self.nick_name = nick_name
        self.last_login = last_login

    def create(self):
        user = models.User.objects.create_user(
            user_id=self.user_id,
            mail_address=self.mail_address,
            password=self.password,
            nickname=self.nick_name,
            last_login=self.last_login
        )
        return user

    class Meta:
        model = models.User
        fields = ('user_id', 'mail_address', 'password', "nickname", "last_login")