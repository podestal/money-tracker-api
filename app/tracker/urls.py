"""
Urls for tracker api
"""
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()

router.register('categories', views.CategoryViewSet, basename='categories')
router.register('transactions', views.TransactionViewSet, basename='transactions')
router.register('balances', views.BalanceViewSet, basename='balances')

urlpatterns = router.urls
