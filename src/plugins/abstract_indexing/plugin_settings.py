from django.contrib.contenttypes.models import ContentType

from utils import models as utils_models


PLUGIN_NAME = "abstract_indexing"
DISPLAY_NAME = "Abstract Indexing"
DESCRIPTION = (
    "Homepage element for managing abstracting and indexing services for journals."
)
AUTHOR = "Custom Plugin"
VERSION = "1.0"
JANEWAY_VERSION = "1.8.0"


def install():
    import core.models as core_models
    import journal.models as journal_models

    plugin, created = utils_models.Plugin.objects.get_or_create(
        name=PLUGIN_NAME,
        defaults={
            "version": VERSION,
        },
    )

    plugin.display_name = DISPLAY_NAME
    plugin.version = VERSION
    plugin.enabled = True
    plugin.homepage_element = True
    plugin.save()

    journals = journal_models.Journal.objects.all()

    for journal in journals:
        content_type = ContentType.objects.get_for_model(journal)

        element, created = core_models.HomepageElement.objects.get_or_create(
            name=DISPLAY_NAME,
            content_type=content_type,
            object_id=journal.pk,
            defaults={
                "configure_url": "abstract_indexing_config",
                "template_path": "journal/homepage_elements/indexing.html",
                "has_config": True,
                "available_to_press": True,
            },
        )

        if not created:
            element.configure_url = "abstract_indexing_config"
            element.template_path = "journal/homepage_elements/indexing.html"
            element.has_config = True
            element.save()


def hook_registry():
    return {
        "yield_homepage_element_context": {
            "module": "plugins.abstract_indexing.hooks",
            "function": "yield_homepage_element_context",
            "name": DISPLAY_NAME,
        }
    }


def register_for_events():
    pass