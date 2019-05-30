"""
持久化层

包含各持久化类
"""
from django.db import models


class DetailModel(models.Model):
    """详单持久化类"""
    detail_id = models.IntegerField(primary_key=True)
    room_id = models.CharField(max_length=16)
    start_time = models.DateTimeField()
    finish_time = models.DateTimeField()
    speed = models.IntegerField()
    fee_rate = models.FloatField()
    fee = models.FloatField()


class Log(models.Model):
    """操作日志"""
    room_id = models.CharField(max_length=16)
    operation = models.CharField(max_length=32)
    op_time = models.DateTimeField()
