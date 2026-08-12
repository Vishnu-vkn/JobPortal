import logging

from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):

    response = exception_handler(exc, context)

    if response is not None:

        logger.error(
            "API Error: %s",
            exc,
            exc_info=True
        )

        response.data = {
            "success": False,
            "message": "Request Failed",
            "errors": response.data
        }

    return response