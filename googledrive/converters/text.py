from wagtail_content_import.mappers.converters import BaseConverter

class HeadingBlockConverter(BaseConverter):
    def __call__(self, element, **kwargs):
        heading_text = element['value']
        size = element.get('size', 'h2')  # Default to h2 if size isn't provided
        return (self.block_name, {'heading_text': heading_text, 'size': size})

class ParagraphBlockConverter(BaseConverter):
    def __call__(self, element, **kwargs):
        paragraph_text = element['value']
        return (self.block_name, {'text': paragraph_text})
