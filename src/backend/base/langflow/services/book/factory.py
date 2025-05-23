from langflow.services.factory import ServiceFactory

from .service import BookService


class BookServiceFactory(ServiceFactory):
    """Factory for creating BookService instances."""

    def __init__(self):
        super().__init__(BookService)
