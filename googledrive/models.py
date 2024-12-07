from wagtail.blocks import StreamBlock
from .blocks import HeadingBlock, ParagraphBlock, ImageBlock, VideoBlock

class BaseBodyStreamBlock(StreamBlock):
    heading_block = HeadingBlock()
    paragraph_block = ParagraphBlock()
    image_block = ImageBlock()
    video_block = VideoBlock()
