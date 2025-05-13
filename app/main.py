from app.presenters.rest.config import RestConfig
from app.presenters.rest.service import RestService

config = RestConfig()
app = RestService(config=config).create_application()
