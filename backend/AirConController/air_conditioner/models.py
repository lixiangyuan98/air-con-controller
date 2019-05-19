"""
持久化层

包含各持久化类
"""
from django.db import models


class DetailModel(models.Model):
    """详单持久化类"""
    pass


class InvoiceModel(models.Model):
    """账单持久化类"""
    pass


class ReportModel(models.Model):
    """报表持久化类"""
    pass
