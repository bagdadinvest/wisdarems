from wagtail_content_import.mappers.converters import BaseConverter

class VideoBlockConverter(BaseConverter):
    def __call__(self, element, **kwargs):
        video_url = element['value']
        # Assuming a block with 'url' field to store the video URL
        return (self.block_name, {'url': video_url})
