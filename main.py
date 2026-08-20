from fastapi import FastAPI

from routers import items, projects, tags, tasks, users

app = FastAPI()

app.include_router(items.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(tags.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Hello World"}
