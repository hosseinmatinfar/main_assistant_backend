from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Create the main application
app = FastAPI()

# A root route for testing
@app.get("/")
def read_root():
    return {"message": "Hello! Your assistant server is running."}

# This is the main route that the Flutter app will communicate with
@app.post("/process-audio/")
async def process_audio():
    # TODO: Later we will add AI logic here
    # For now, just return a test response
    print("A request was received!")
    return JSONResponse(content={"response_text": "Processing done, this is a test response."})
