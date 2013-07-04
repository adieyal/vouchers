from django.conf.urls import patterns, include, url

from django.contrib import admin
import views
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'vouchers.views.home', name='home'),
    url(r'^$', views.EnterDetails.as_view(), name="enter_voucher"),
    url(r'^vouchers/$', views.VoucherAllocation.as_view(), name="allocation"),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
