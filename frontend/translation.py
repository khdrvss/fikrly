from modeltranslation.translator import register, TranslationOptions
from .models import BusinessCategory, Company


@register(BusinessCategory)
class BusinessCategoryTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Company)
class CompanyTranslationOptions(TranslationOptions):
    fields = ("name", "description")
