from django.contrib import admin

from .models import Article
from .models import Category
#from .models import Rank

#admin.site.register(Rank)
admin.site.register(Category)
admin.site.register(Article)
