from django.contrib import admin


class BaseOwnerAdmin(admin.ModelAdmin):
    """
    用于自动填充Model的Owner字段
    用于针对queryset过滤当前用户的数据
    """
    exclude = ('owner', )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(owner=request.user)

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super().save_model(request, obj, form, change)
