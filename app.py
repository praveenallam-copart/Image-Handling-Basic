from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import router_modules
from logs import get_app_logger, get_error_logger, setup_logging

setup_logging()
app_logger = get_app_logger()
error_logger = get_error_logger()

app = FastAPI(
    title='Walter',
    description='NA',
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    contact={
        "name": "Praveen Allam",
        "email": "saipraveen.allam@copart.com"
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

for router_module in router_modules:
    app.include_router(router_module.router)
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host = "0.0.0.0", port = 8000, reload = True)