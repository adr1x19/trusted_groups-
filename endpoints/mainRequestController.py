from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from endpoints.cartEndpoint import cartRouter 

app = FastAPI(title="main request controller")

# Allow all origins so your frontend can communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(cartRouter)
