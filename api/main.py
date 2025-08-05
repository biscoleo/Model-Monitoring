# copied from previous assignment - placeholder


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
import pandas as pd 
from typing import Dict


app = FastAPI()

df = pd.read_csv('IMDB Dataset.csv')

# if I use Field here and set min_length to 1, then i dont have to do manual if not input.text.strip() in my endpoint funcs becuase it will be caught here with pydantic!
class TextInput(BaseModel):
    text: str = Field(..., min_length=1)

class SentimentResponse(BaseModel):
    sentiment: str

class SentimentProbabilityResponse(BaseModel):
    sentiment: str
    probabilities: Dict[str, float]

# load the model just once at startup
try:
    model = joblib.load('sentiment_model.pkl')
except Exception:
    raise HTTPException(status_code=500, detail='Model could not be loaded')


# read_root from slideshow - i hear this is nice for setting up a friendly welcome or for tutorials
@app.get('/')
def read_root():
    return {'message': 'Welcome to the Sentiment Analysis API!'}

@app.get('/health')
def health_check():
    return{'status': 'ok'}



@app.post('/predict', response_model=SentimentResponse)
def predict_sentiment(input: TextInput):
    try:
        prediction = model.predict([input.text])[0]
        return {'sentiment': prediction}
    except Exception as e:
        raise HTTPException(status_code = 500, detail=f'Prediction failed: {str(e)}')



@app.post('/predict_proba', response_model=SentimentProbabilityResponse)
def predict_with_probability(input: TextInput):
    # prediction logic
    try:
        prediction = model.predict([input.text])[0]
        probabilities = model.predict_proba([input.text])[0]
        probability_dictionary = {
            'negative': round(probabilities[0], 2),
            'positive': round(probabilities[1], 2)
        }

        return {'sentiment': prediction, 
                'probabilities': probability_dictionary}
    except Exception as e:
        raise HTTPException(status_code = 500, detail=f'Prediction failed: {str(e)}')


@app.get('/example')
def get_example():
    random_row = df.sample(1).iloc[0]
    return {'review': random_row['review']}

