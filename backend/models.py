# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class User(models.Model):
    user_id = models.CharField(unique=True, max_length=20)
    mail_address = models.CharField(unique=True, max_length=319)
    password = models.CharField(max_length=200)
    nickname = models.CharField(max_length=10)
    last_login = models.DateTimeField()
    is_active = models.IntegerField()
    is_staff = models.IntegerField()
    is_superuser = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'user'


class Accountbook(models.Model):
    user_id = models.CharField(max_length=20)
    item_no = models.AutoField(primary_key=True)
    category_id = models.IntegerField()
    public_no = models.IntegerField(blank=True, null=True)
    amount = models.IntegerField()
    public = models.IntegerField(blank=True, null=True)
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
    prefecture_id = models.IntegerField()

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


class Prefectures(models.Model):
    prefecture_name = models.CharField(max_length=8)
    block_name = models.CharField(max_length=8)

    class Meta:
        managed = False
        db_table = 'prefectures'


class Chat(models.Model):
    chat_id = models.AutoField(primary_key=True)
    gp_id = models.IntegerField()
    user_id = models.CharField(max_length=20)
    chat = models.CharField(max_length=200)
    chat_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'chat'
