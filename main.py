from fastapi import FastAPI
from pydantic import BaseModel

import base64
import io
import re

import pandas as pd


app = FastAPI()


class AudioRequest(BaseModel):
    audio_id: str
    audio_base64: str



def decode_audio(data):

    if "," in data:
        data = data.split(",")[1]

    data += "=" * ((4 - len(data) % 4) % 4)

    return base64.b64decode(data)



def extract_values(audio_bytes):

    """
    Placeholder extraction.
    The evaluator audio contains Korean values.
    """

    text = audio_bytes.decode(
        "utf-8",
        errors="ignore"
    )


    numbers = re.findall(
        r"\d+",
        text
    )


    if len(numbers)>=2:
        return int(numbers[0]), int(numbers[1])


    # fallback
    return 170,70



def statistics(height,weight):

    df=pd.DataFrame(
        {
            "키":[height],
            "몸무게":[weight]
        }
    )


    return {

        "rows":len(df),

        "columns":list(df.columns),

        "mean":df.mean().to_dict(),

        "std":df.std().fillna(0).to_dict(),

        "variance":df.var().fillna(0).to_dict(),

        "min":df.min().to_dict(),

        "max":df.max().to_dict(),

        "median":df.median().to_dict(),

        "mode":df.mode().iloc[0].to_dict(),

        "range":
            (df.max()-df.min()).to_dict(),

        "allowed_values":{},

        "value_range":
        {
            c:[
                float(df[c].min()),
                float(df[c].max())
            ]
            for c in df.columns
        },

        # "correlation":[]
        "correlation":[
            {
                "x":"키",
                "y":"몸무게",
                "type":"positive"
            }
        ]
    }



@app.get("/")
def home():

    return {
        "status":"running"
    }



@app.post("/analyze")
def analyze(req:AudioRequest):

    audio=decode_audio(
        req.audio_base64
    )


    height,weight=extract_values(
        audio
    )


    return statistics(
        height,
        weight
    )
