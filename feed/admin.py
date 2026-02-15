from django.contrib import admin
from .models import FeedType, PondFeedStock, FeedUsageLog

admin.site.register(FeedType)
admin.site.register(PondFeedStock)
admin.site.register(FeedUsageLog)
