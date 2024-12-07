from wagtail_content_import.mappers.converters import BaseConverter, ImageConverter

class ImageBlockConverter(BaseConverter):
    def __call__(self, element, user, *args, **kwargs):
        image_url = element['value']
        image_name, image_content = ImageConverter.fetch_image(image_url)
        image = ImageConverter.import_as_image_model(image_name, image_content, owner=user)
        return (self.block_name, {'show_full_image': None, 'image': image})
