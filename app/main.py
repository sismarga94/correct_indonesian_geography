import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from app.controllers.api_controller import api_router

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/try-api", response_class=HTMLResponse)
async def try_api(request: Request):
    return templates.TemplateResponse("try_api.html", {"request": request})


@app.get("/upload", response_class=HTMLResponse)
async def upload_form(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    # Process the file contents using the service layer
    # Example: processed_data = process_file(contents)
    return {"filename": file.filename, "contents": contents.decode('utf-8')}


# Custom OpenAPI documentation
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Geographic API",
        version="1.0.0",
        description="API to check Indonesian Geographic Data Errors",
        routes=[route for route in app.routes if route.path == "/api/check"],
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

# run in cmd
# uvicorn app.main:app --reload
