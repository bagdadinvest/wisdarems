# home/wagtail_hooks.py (or in your chosen app directory)
from wagtail import hooks
from django.utils.html import format_html
from wagtail import hooks
from wagtail.admin.menu import MenuItem
from django.urls import reverse

@hooks.register('insert_global_admin_css')
def global_admin_css():
    return format_html('<link rel="stylesheet" href="/static/css/custom-admin.css">')

@hooks.register('insert_editor_css')
def custom_logo_css():
    return format_html('''
        <style>
            .wagtail-branding__logo {
                background-image: url("/static/images/custom-logo.png");
                background-size: contain;
                width: 200px;  /* Adjust size accordingly */
                height: 40px;  /* Adjust height accordingly */
            }
        </style> 
    ''')


@hooks.register('register_admin_menu_item')
def register_google_docs_menu_item():
    return MenuItem('Google Docs List', reverse('google_docs_list'), classnames='icon icon-doc-full', order=10000)
