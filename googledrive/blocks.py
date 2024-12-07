from wagtail.blocks import CharBlock, ChoiceBlock, StructBlock, TextBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from django.utils.safestring import mark_safe

# Define HeadingBlock (for headings like h2, h3, h4)
class HeadingBlock(StructBlock):
    heading_text = CharBlock(classname="title", required=True)
    size = ChoiceBlock(choices=[
        ('', 'Select a header size'),
        ('h2', 'H2'),
        ('h3', 'H3'),
        ('h4', 'H4')
    ], blank=True, required=False)

    class Meta:
        icon = "title"
        template = "blocks/heading_block.html"

# Define ParagraphBlock (for normal text/paragraphs)
class ParagraphBlock(TextBlock):
    class Meta:
        icon = "pilcrow"
        template = "blocks/paragraph_block.html"

# Define ImageBlock (for images)
class ImageBlock(StructBlock):
    show_full_image = ChoiceBlock(required=False)
    image = ImageChooserBlock()

    class Meta:
        icon = "image"
        admin_text = mark_safe("<b>Image Block</b>")
        template = "blocks/image_block.html"

# Define VideoBlock (for embedding videos)
class VideoBlock(StructBlock):
    url = EmbedBlock(help_text="Paste the video URL")

    class Meta:
        icon = "media"
        template = "blocks/video_block.html"
