from django.contrib.admin.filters import SimpleListFilter


class ProductStockFilter(SimpleListFilter):
    title = 'В наличии?'
    parameter_name = 'in_stock'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Да'),
            ('no', 'Нет'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(stock__gt=0)
        elif self.value() == 'no':
            return queryset.filter(stock__lte=0)
        return queryset
