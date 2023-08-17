from django.core.exceptions import ValidationError


def validate_amount(value):
    '''
    Валидация для поля "amount": значение должно быть СТРОГО больше 0
    '''
    if value <= 0:
        raise ValidationError(
            'Количество ингредиента должно быть больше 0'
        )
