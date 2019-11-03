from django.conf.urls import url

from . import views


app_name = 'depreciation_rate_classifier'  # https://docs.djangoproject.com/en/1.11/intro/tutorial03/#namespacing-url-names
urlpatterns = [
    # i.e. / site root given kebab_van/urls.py also registers root to this one
    url(r'^$', views.index, name='index'),
    # i.e. /api-ml/
    url(r'^api-ml/$', views.api_ml, name='api_ml'),
    # i.e. /5/ml-batch-result/
    url(r'^(?P<user_input_id>[0-9]+)/ml-batch-result/$', views.ml_batch_result, name='ml_batch_result'),
    # i.e. /add-confirmation/
    url(r'^add-confirmation/$', views.add_user_confirmation, name='add_user_confirmation'),
]
