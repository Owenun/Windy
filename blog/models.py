from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除')
    )

    name = models.CharField(max_length=128, verbose_name='名称')
    status = models.PositiveIntegerField(default=STATUS_NORMAL, choices=STATUS_ITEMS, verbose_name='状态')
    is_nav = models.BooleanField(default=False, verbose_name='是否为导航')
    owner = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return self.name

    @classmethod
    def get_navs(cls):
        categories = cls.objects.filter(status=Category.STATUS_NORMAL)
        """
        navs = categories.filter(is_nav=True)
        normal_categories = categories.filter(is_nav=False)
        #这种方法向数据库产生两次请求，改用如下写法
        """
        navs = []
        normal_categories = []
        for cate in categories:
            if cate.is_nav:
                navs.append(cate)
            else:
                normal_categories.append(cate)
        return {
                'navs': navs,
                'categories': normal_categories,
                }

    class Meta:
        verbose_name = verbose_name_plural = '分类'


class Tag(models.Model):
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除')
    )

    name = models.CharField(max_length=10, verbose_name='名称')
    status = models.PositiveIntegerField(default=STATUS_NORMAL, choices=STATUS_ITEMS, verbose_name='状态')
    owner = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = verbose_name_plural = '标签'


class Post(models.Model):

    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_DRAFT = 2
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除'),
        (STATUS_DRAFT, '草稿'),
    )

    title = models.CharField(max_length=255, verbose_name='标题')
    desc = models.CharField(max_length=1024, blank=True, verbose_name='摘要')
    content = models.TextField(verbose_name='正文', help_text='正文必须为MarkDown格式')
    status = models.PositiveIntegerField(default=STATUS_NORMAL, choices=STATUS_ITEMS, verbose_name='状态')
    category = models.ForeignKey(Category, verbose_name='分类', on_delete=models.CASCADE)
    tag = models.ManyToManyField(Tag, verbose_name='标签')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    owner = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE)
    pv = models.PositiveIntegerField(default=1)  # 用于统计每篇文章访问量
    pu = models.PositiveIntegerField(default=1)  # 用于统计每篇文章访问量

    def __str__(self):
        return self.title

    @staticmethod
    def get_by_tag(tag_id):
        try:
            tag = Tag.objects.get(id=tag_id)
        except Tag.DoesNotExist:
            tag = None
            post_ls = []
        else:
            post_ls = tag.post_set.filter(status=Post.STATUS_NORMAL).select_related('category', 'owner')
            # 这里的.select_related()方法解决 数据库N+1问题
        return post_ls, tag

    @staticmethod
    def get_by_category(category_id):
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            category = None
            post_ls = None
        else:
            post_ls = category.post_set.filter(status=Post.STATUS_NORMAL).select_related('category', 'owner')
            # 对于category实例才有post_set属性，而Category.objects.filter()这是QuerySet对象，无
        return post_ls, category

    @classmethod  # 用于推送最热文章的类方法 # 返回queryset对象
    def hot_post(cls):
        return cls.objects.filter(status=cls.STATUS_NORMAL).order_by('-pv')

    @classmethod
    def latest_posts(cls):  # 返回queryset对象
        queryset = cls.objects.filter(status=cls.STATUS_NORMAL)
        return queryset

    class Meta:
        verbose_name = verbose_name_plural = '文章'
        ordering = ['id']  # 根据id降序排序
