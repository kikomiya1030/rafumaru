from django.contrib import admin
from .models import User, Accountbook, Category, Comment, Public, Gp, Member, Shareaccountbook, Notice

class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'mail_address', 'password', 'nickname', 'last_login')  # 表示したいフィールドを指定
    search_fields = ['user_id']  # 検索フィールドを設定
class AccuntbookAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'item_no', 'category_id', 'public_no', 'amount', 'public', 'date', 'memo')  # 表示したいフィールドを指定
    search_fields = ['user_id']  # 検索フィールドを設定
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("category_id", "category_name")  # 表示したいフィールドを指定
    search_fields = ["category_name"]  # 検索フィールドを設定
class CommentAdmin(admin.ModelAdmin):
    list_display = ("comment_id", "comment", "public_no", "like_point", "user_id")  # 表示したいフィールドを指定
    search_fields = ["comment", "user_id"]  # 検索フィールドを設定
class PublicAdmin(admin.ModelAdmin):
    list_display = ("public_id", "title")  # 表示したいフィールドを指定
    search_fields = ["title"]  # 検索フィールドを設定
class GpAdmin(admin.ModelAdmin):
    list_display = ("id", "gp_name", "gp_pw", "income_input", "gp_id")  # 表示したいフィールドを指定
    search_fields = ["gp_name"]  # 検索フィールドを設定
class MemberAdmin(admin.ModelAdmin):
    list_display = ("id", "gp_id", "user_id")  # 表示したいフィールドを指定
    search_fields = ["user_id"]  # 検索フィールドを設定
class ShareaccountbookAdmin(admin.ModelAdmin):
    list_display = ("shareditem_id", "user_id", "category_id", "amount", "gp_id", "date", "memo")  # 表示したいフィールドを指定
    search_fields = ["title"]  # 検索フィールドを設定
class NoticeAdmin(admin.ModelAdmin):
    list_display = ("notice_id", "user_id", "re_user_id", "notice_title", "notice_content", "notice_date")
    search_fields = ["user_id"]

admin.site.register(User, UserAdmin)
admin.site.register(Accountbook, AccuntbookAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Public, PublicAdmin)
admin.site.register(Gp, GpAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Shareaccountbook, ShareaccountbookAdmin)
admin.site.register(Notice, NoticeAdmin)