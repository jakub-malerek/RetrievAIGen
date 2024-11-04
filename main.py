import uvicorn
from app.api.server import app  # Import the FastAPI app from app/api/server.py

if __name__ == "__main__":
    # Run the FastAPI app using Uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
