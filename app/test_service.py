import random,time
from fastapi import FastAPI,HTTPException
app=FastAPI(title='Intelligent Monitor Test Service')
@app.get('/health')
def health():return {'status':'healthy'}
@app.get('/users')
def users():return {'users':[{'id':1,'name':'Alice'},{'id':2,'name':'Bob'}]}
@app.get('/products')
def products():return {'products':[{'id':101,'name':'Laptop'},{'id':102,'name':'Phone'}]}
@app.get('/slow')
def slow():
    delay=random.uniform(3,5); time.sleep(delay); return {'status':'slow','delay_seconds':round(delay,2)}
@app.get('/error')
def error():raise HTTPException(status_code=500,detail='Simulated internal server error')
