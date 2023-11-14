from django import template

register = template.Library()

words = ["музыка", "Музыка", "музыки", "музыка.", "музыка,"]

@register.filter
def censor(text):
    if type(text) == str:
        text = text.split()
        for i, word in enumerate(text):
            if word in words:
                text[i] = word[0] + '*' * len(word[1:])
        return ' '.join(text)
    else:
        return "Ошибка!"