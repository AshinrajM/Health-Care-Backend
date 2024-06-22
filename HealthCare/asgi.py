"""
ASGI config for HealthCare project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

# import os
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# from dotenv import load_dotenv

# load_dotenv()

# from chat.routing import websocket_urlpatterns
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HealthCare.settings")



# django_asgi_app = get_asgi_application()



# application = ProtocolTypeRouter(
#     {
#         "http": get_asgi_application(),
#         "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
#     }
# )

import os
from django.core.asgi import get_asgi_application
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HealthCare.settings")

django_asgi_app = get_asgi_application()

from .routing import application