from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()

router.register('categories', views.CategoryViewSet)
router.register('transactions', views.TransactionViewSet)
router.register('balances', views.BalanceViewSet)

urlpatterns = router.urls