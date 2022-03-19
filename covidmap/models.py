from django.db import models
from django.utils import timezone


# Create your models here.
class Location(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def natural_key(self):
        return self.__str__()

    class Meta:
        verbose_name = "地区"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CovidHistory(models.Model):
    id = models.AutoField(primary_key=True)
    created_time = models.DateTimeField(default=timezone.now)
    updated_time = models.DateTimeField(auto_now=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, primary_key=False, verbose_name='地区')
    total_confirmed = models.IntegerField(verbose_name='累计确诊人数', default=0)
    total_cured = models.IntegerField(verbose_name='累计治愈人数', default=0)
    total_dead = models.IntegerField(verbose_name='累计死亡人数', default=0)

    class Meta:
        # 改表名
        db_table = 'covid_history'
        # 修改后台admin对的显示信息的配置
        verbose_name_plural = '疫情数据汇总'

    def __str__(self):
        # 后台显示
        return '更新日期:' + str(self.updated_time.strftime("%Y-%m-%d")) + ' ,地区：' + str(self.location)


class CovidCurrent(models.Model):
    id = models.AutoField(primary_key=True)
    created_time = models.DateTimeField(default=timezone.now)
    updated_time = models.DateTimeField(auto_now=True)
    current_date = models.DateField(verbose_name='日期')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, primary_key=False, verbose_name='地区')
    incr_confirmed = models.PositiveIntegerField(verbose_name='新增确诊人数', default=0)
    incr_cured = models.PositiveIntegerField(verbose_name='新增治愈人数', default=0)
    incr_dead = models.PositiveIntegerField(verbose_name='新增死亡人数', default=0)
    incr_suspected = models.PositiveIntegerField(verbose_name='新增疑似人数', default=0)

    class Meta:
        # 改表名
        db_table = 'covid_current'
        # 修改后台admin对的显示信息的配置
        verbose_name_plural = '当日疫情数据'

    def __str__(self):
        return '日期:' + str(self.current_date) + ' ,地区：' + str(self.location)