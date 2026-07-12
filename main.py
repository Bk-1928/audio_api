from fastapi import FastAPI
from pydantic import BaseModel

import base64
import io
import os
import re
import tempfile

import pandas as pd
import whisper
import soundfile as sf


app = FastAPI()


# Load whisper once when server starts
print("Loading Whisper model...")

model = whisper.load_model("tiny")

print("Whisper loaded")


class AudioRequest(BaseModel):
    audio_id: str
    audio_base64: str



def decode_base64_audio(data):

    # remove prefix
    if "," in data:
        data = data.split(",")[1]

    data = data.strip()

    # fix padding
    data += "=" * ((4 - len(data) % 4) % 4)


    return base64.b64decode(data)



def transcribe_audio(audio_bytes):

    temp = tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    )

    temp.write(audio_bytes)
    temp.close()


    result = model.transcribe(
        temp.name,
        language="ko"
    )


    os.remove(temp.name)


    return result["text"]



def extract_height_weight(text):

    print("TEXT:", text)


    numbers = re.findall(
        r'\d+',
        text
    )


    if len(numbers) < 2:
        raise Exception(
            "Could not extract height and weight"
        )


    height = int(numbers[0])
    weight = int(numbers[1])


    return height, weight



def calculate_statistics(height, weight):


    df = pd.DataFrame(
        {
            "키":[height],
            "몸무게":[weight]
        }
    )


    result = {

        "rows": int(df.shape[0]),


        "columns":
            list(df.columns),


        "mean":
            df.mean().to_dict(),


        "std":
            df.std().fillna(0).to_dict(),


        "variance":
            df.var().fillna(0).to_dict(),


        "min":
            df.min().to_dict(),


        "max":
            df.max().to_dict(),


        "median":
            df.median().to_dict(),


        "mode":
            df.mode().iloc[0].to_dict(),


        "range":
            (df.max()-df.min()).to_dict(),


        "allowed_values":
            {},


        "value_range":
            {
                col:[
                    float(df[col].min()),
                    float(df[col].max())
                ]
                for col in df.columns
            },


        "correlation":
            []

    }


    return result



@app.get("/")
def home():

    return {
        "status":"running"
    }



@app.post("/analyze")
def analyze(req:AudioRequest):


    audio_bytes = decode_base64_audio(
        req.audio_base64
    )


    text = transcribe_audio(
        audio_bytes
    )


    height, weight = extract_height_weight(
        text
    )


    response = calculate_statistics(
        height,
        weight
    )


    return response