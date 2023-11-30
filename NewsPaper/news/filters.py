from django_filters import FilterSet, DateTimeFilter, ModelMultipleChoiceFilter
from django.forms import DateTimeInput
from .models import Post, Category

class PostFilter(FilterSet):
    added_after = DateTimeFilter(
        field_name='date_time',
        lookup_expr='gt',
        label='Позже указываемой даты',
        widget=DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={'type': 'datetime-local'},
        ),
    )

    categoryType = ModelMultipleChoiceFilter(
        field_name='choice_category',
        queryset=Category.objects.all(),
        label='Категория',
    )

    class Meta:
       model = Post
       fields = {
           'head': ['icontains'],
       }