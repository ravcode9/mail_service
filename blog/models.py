from django.db import models


class Blog(models.Model):
    title = models.CharField(max_length=50, verbose_name='заголовок')
    text = models.TextField(verbose_name='текст')
    image = models.ImageField(upload_to='blog/', verbose_name='изображение', blank=True, null=True, default='static/blog.jpg')
    count_of_view = models.IntegerField(default=0, verbose_name='Просмотры')
    date = models.DateTimeField(auto_now_add=True, verbose_name='дата публикации')

    def __str__(self):
        return f'{self.title} {self.count_of_view}'

