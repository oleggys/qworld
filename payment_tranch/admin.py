from django.contrib import admin
from django.utils.html import format_html
# Register your models here.
from payment_tranch.models import Promocode, Order, Part_Order, Application


class PromocodeAdmin(admin.ModelAdmin):
    list_display = [
        'code',
        'discount',
    ]


class ApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'user_id',
        'amount',
        'purse',
        'account_actions', 
    ]
    def account_actions(self, obj):
        args = {}
        args['obj'] = obj
        return format_html(
            '<div id="pay_admin_form_{3}"><input type="hidden" name="receiver" value="{0}"> <input type="hidden" name="quickpay-form" value="shop"><input type="hidden" name="targets" value="Снятие суммы с баланса пользователя – id {1}"><input type="hidden" name="sum" value="{2}" data-type="number"><input type="hidden" name="paymentType" value="PC"><input type="hidden" name="successURL" value="https://oleggys.ru/admin/payment_tranch/application/{3}/change/"><button type="submit" >Оплатить</button></div><script>$("#pay_admin_form_{3}").wrap( "<form method=POST action=https://money.yandex.ru/quickpay/confirm.xml ></form>" );</script>'.format(str(obj.purse), str(obj.user_id), str(obj.amount), str(obj.id))
        )


admin.site.register(Promocode, PromocodeAdmin)
admin.site.register(Order)
admin.site.register(Part_Order)
admin.site.register(Application, ApplicationAdmin)