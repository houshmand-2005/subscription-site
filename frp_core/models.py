from django.db import models
import uuid
# Create your models here.

subtypes = (
    ("1", "1day"),
    ("7", "7days"),
    ("15", "15days"),
    ("30", "30days"),
    ("60", "60days"),
)
payment_stat = (
    ("true", "true"),
    ("false", "false"),
)


class GenKey(models.Model):
    key_code = models.CharField(max_length=255)
    phonenumber = models.CharField(max_length=255)
    buytime = models.DateTimeField(auto_now_add=True)
    subtype = models.CharField(
        max_length=255,
        choices=subtypes,
        default='1'
    )
    money_currency = models.IntegerField()
    payment_ok = models.CharField(
        max_length=255,
        choices=payment_stat,
        default='false'
    )
    trackingcode = models.CharField(
        max_length=255, blank=True, unique=True, default=uuid.uuid4)
