import os
from fastapi import FastAPI
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field
import uvicorn

import firebase_admin
from firebase_admin import credentials, auth
import pyrebase

from transformers import AutoTokenizer, AutoModelForCausalLM
import queue
from multiprocessing import get_context
from concurrent.futures.process import ProcessPoolExecutor

import asyncio
from concurrent.futures.process import ProcessPoolExecutor
from contextlib import asynccontextmanager


ctx = get_context("spawn")
pool = ProcessPoolExecutor(mp_context=ctx)

from dotenv import load_dotenv
load_dotenv()



@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.executor = ProcessPoolExecutor()
    yield
    app.state.executor.shutdown()

app = FastAPI(
    title="Program Generator",
    lifespan=lifespan
)

#server ok status display
@app.get("/")
async def root():
    return {"message":"Server OK"}

#importing variables
FIREBASE_WEB_API_KEY = os.environ.get("fbapiKey")
rest_api_url = os.environ.get("fb_auth_rest_api_url")
rest_api_url_bearer = os.environ.get("fb_auth_rest_api_url_bearer")

firebaseConfig = {
    'apiKey': os.getenv('fbapiKey'),
    'authDomain': os.getenv('fbauthDomain'),
    'projectId': os.getenv('fbprojectId'),
    'storageBucket': os.getenv('fbstorageBucket'),
    'messagingSenderId': os.getenv('fbmessagingSenderId'),
    'appId': os.getenv('fbappId'),
    'measurementId': os.getenv('fbmeasurementId'),
    'databaseURL':os.getenv('fbdatabaseURL')
    }


#init Firebase
if not firebase_admin._apps:
    print("Firebase app not initialized")
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)


firebase = pyrebase.initialize_app(firebaseConfig)
security = HTTPBearer()


async def get_current_user(token: str = Depends(security)):                  
    try:
        decoded_token = auth.verify_id_token(token.credentials)
        
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate your Bearer credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/protected")
async def protected_route(current_user=Depends(get_current_user)):
    return {"message": "Auth Success | Welcome, user!"}

#model use
tokenizer = AutoTokenizer.from_pretrained(os.getenv('tokenizer_model'), trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(os.getenv('model'), trust_remote_code=True).cuda()

#defining data structure for input
class iputData(BaseModel):
    text: str = Field(min_length=20)

    class Config:
        schema_extra = {
        "example": {
            "text": "Hello world"  
                }
        }

prediction_queue = queue.Queue()

def get_prediction():

    data = prediction_queue.get()

    # Tokenization of the input text
    tokens = tokenizer.apply_chat_template(
                                        [{'role': 'user', 'content': data}], 
                                        return_tensors="pt").to(model.device)
    
    # Generating the prediction
    outputs = model.generate(tokens,
                                max_new_tokens=512, 
                                do_sample=False, 
                                top_k=50, 
                                top_p=0.95, 
                                num_return_sequences=1, 
                                eos_token_id=32021)
    
    
    # Decoding the prediction
    decoded_prediction = tokenizer.decode(outputs[0][len(tokens[0]):], 
                                            skip_special_tokens=True)
    
    return decoded_prediction


@app.post("/predict/")
async def predict(data: iputData, current_user=Depends(get_current_user)):
    prediction_queue.put(data.text)
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
                                    pool,
                                    get_prediction
                                )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


