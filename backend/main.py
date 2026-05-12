import uvicorn
from nexsentia.api.server import app


if __name__ == "__main__":
    uvicorn.run(
        "nexsentia.api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )

