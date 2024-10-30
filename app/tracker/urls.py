"""
Urls for tracker api
"""

from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()

router.register("categories", views.CategoryViewSet, basename="categories")
router.register("transactions", views.TransactionViewSet, basename="transactions")
router.register("balances", views.BalanceViewSet, basename="balances")
router.register("projects", views.ProjectViewSet, basename="projects")
router.register("teams", views.TeamViewSet, basename="teams")

projects_router = routers.NestedDefaultRouter(router, "projects", lookup="projects")
projects_router.register("tasks", views.TaskViewSet, basename="tasks")

urlpatterns = router.urls + projects_router.urls
