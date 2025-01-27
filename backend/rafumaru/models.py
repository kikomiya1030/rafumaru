# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import check_password, make_password

class CustomUserManager(BaseUserManager):
    def create_user(self, user_id, mail_address, password, nickname, last_login):
        mail_address = self.normalize_email(mail_address)
        new_password = make_password(str(password))
        user = self.model(mail_address=mail_address, user_id=user_id, password=new_password, nickname=nickname, last_login=last_login)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_id, mail_address, password, nickname, last_login):
        return self.create_user(user_id, mail_address, password, nickname, last_login)

class User(models.Model):
    user_id = models.CharField(unique=True, max_length=20)
    mail_address = models.CharField(unique=True, max_length=319)
    password = models.CharField(max_length=200)
    nickname = models.CharField(max_length=10)
    last_login = models.DateTimeField()

    is_active = models.BooleanField(default=True)  # is_activeフィールドを追加
    is_staff = models.BooleanField(default=False)  # 管理者権限のためにis_staffも追加
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    class Meta:
        managed = False
        db_table = 'user'

    def set_password(self, raw_password):
        """
        パスワードをハッシュ化して保存するメソッド
        """
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """
        ハッシュ化されたパスワードをチェックするメソッド
        """
        return check_password(raw_password, self.password)


class Accountbook(models.Model):
    user_id = models.CharField(max_length=20)
    item_no = models.AutoField(primary_key=True)
    category_id = models.IntegerField()
    public_no = models.IntegerField()
    amount = models.IntegerField()
    public = models.IntegerField()
    date = models.DateField()
    memo = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'accountbook'


class Category(models.Model):
    category_id = models.IntegerField(primary_key=True)
    category_name = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'category'


class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=100)
    public_no = models.IntegerField()
    like_point = models.IntegerField()
    user_id = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'comment'


class Public(models.Model):
    public_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'public'


class Gp(models.Model):
    gp_name = models.CharField(max_length=50)
    gp_pw = models.CharField(max_length=20)
    income_input = models.IntegerField()
    gp_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'gp'


class Member(models.Model):
    gp_id = models.IntegerField()
    user_id = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'member'


class Shareaccountbook(models.Model):
    shareditem_id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=20)
    category_id = models.IntegerField()
    amount = models.IntegerField()
    gp_id = models.IntegerField()
    date = models.DateField()
    memo = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'shareaccountbook'

class Notice(models.Model):
    notice_id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=20)
    re_user_id = models.CharField(max_length=20)
    notice_content = models.CharField(max_length=200)
    notice_date = models.DateTimeField()
    notice_title = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'notice'
