from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.admin.models import LogEntry

from .models import Post, Category, Tag
from .adminforms import PostAdminForm
from windy.base_admin import BaseOwnerAdmin
from windy.custom_site import custom_site


class PostInline(admin.TabularInline):  # stackedInline样式不同

    fields = ('title', 'desc')
    extra = 1
    model = Post


@admin.register(Category, site=custom_site)
class CategoryAdmin(BaseOwnerAdmin):

    inlines = [PostInline, ]
    list_display = ('name', 'status', 'is_nav', 'created_time', 'post_count', 'owner')
    fields = ('name', 'status', 'is_nav', )  # 'owner'

    def post_count(self, obj):
        return obj.post_set.count()
    post_count.short_description = '文章数量'


@admin.register(Tag, site=custom_site)
class TagAdmin(BaseOwnerAdmin):

    list_display = ('name', 'status', 'created_time', 'owner')
    fields = ('name', 'status', )


class CategoryOwnerFilter(admin.SimpleListFilter):

    """自定义过滤器只展示当前用户"""

    title = '自定义分类器'
    parameter_name = 'owner_category'

    def lookups(self, request, model_admin):
        return Category.objects.filter(owner=request.user).values_list('id', 'name')

    def queryset(self, request, queryset):
        category_id = self.value()
        if category_id:
            return queryset.filter(category_id=category_id)
        return queryset


@admin.register(Post, site=custom_site)
class PostAdmin(BaseOwnerAdmin):

    forms = PostAdminForm
    list_display = [
        'title', 'category', 'status',
        'created_time', 'owner', 'operator',
    ]
    list_display_links = []
    list_filter = [CategoryOwnerFilter]
    search_fields = ['title', 'category_name']
    actions_on_top = True
    # actions_on_bottom = True

    # 编辑页面
    # save_on_top = True

    """exclude = ('owner',)
    
    fields = (
        ('category', 'title'),
        'desc',
        'status',
        'content',
        'tag',
    )"""

    fieldsets = (  # fieldsets 的格式是有两个元素的tuple，第一个是板块名称， 第二个是板块描述
        ('基础配置', {
            'description': '',
            'fields': (
                ('title', 'category'),
                'status'
            ),
        }),
        ('内容', {
            'fields': (
                'desc',
                'content',
            ),
        }),
        ('额外信息', {
            'classes': ('collapse', ),
            'fields': ('tag', ),
        })
    )
    filter_vertical = ('tag',)

    def operator(self, obj):
        return format_html(
            '<a href="{}">编辑</a>',
            reverse('cus_admin:blog_post_change', args=(obj.id, ))
        )
    operator.short_description = '操作'

    class Media:
        css = {
            'all': ("https://cdn.bootstrap/4.0.0-bata.2/css/bootstrap/min.css", ),
        }
        js = ("https://cdn.bootcss.com/bootstrap/4.0.0-bata.2/js/bootstrap.bundle.js", )


@admin.register(LogEntry, site=custom_site)
class LogEntryAdmin(admin.ModelAdmin):

    list_display = ['object_repr', 'object_id', 'action_flag', 'user', 'change_message']


