from app.controllers.rest.config import RestConfig
from app.controllers.rest.service import RestService

config = RestConfig()
app = RestService(config=config).create_application()
