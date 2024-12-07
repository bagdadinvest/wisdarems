from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from wagtail.blocks import RichTextBlock
from wagtail_content_import.models import ContentImportMixin
from empmanagement.views import GoogleDocsMapper

class BlogPage(ContentImportMixin, Page):
    body = StreamField([
        ('text', RichTextBlock())
    ], blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

    def create_from_import(self, parsed_data):
        """Use GoogleDocsMapper to map the parsed data into StreamField."""
        mapper = GoogleDocsMapper(self, parsed_data)
        return mapper.map()
