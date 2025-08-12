from fastapi import FastAPI,  Path, HTTPException, Query
import json
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal



app =  FastAPI()

class Patient(BaseModel):

    id: Annotated[str, Field(...,description='ID of the patient', examples= ['P001'])]
    name: Annotated[str, Field(..., description='Name of the patient')]
    city: Annotated[str, Field(..., description='City where the patient is living')]
    age:  Annotated[int, Field(..., description='This is the age of the patient')]
    gender: Annotated[Literal['male', 'female', 'others'], Field(..., description='This is the gender of the patient' )]
    height: Annotated[float, Field(..., gt=0, description='Height of the patient in mtrs') ]
    weight: Annotated[float, Field(..., gt=0, description='This is the weight of the patient in kgs')]

    @computed_field
    @property
    def bmi(self) -> float: 
       bmi = round(self.weight/(self.height**2),2)
       return bmi

    @computed_field
    @property
    def verdict(self) -> str:

        if self.bmi  < 18.5:
            return "Underweight"
        elif self.bmi <  25:
            return 'Normal'
        elif self.bmi < 30: 
            return 'Normal'
        else: 
            return 'Obese'
    





def load_data():
    with open('patients.json', 'r') as  f:
        data = json.load(f)

    return data

def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f)


@app.get("/")
def hello():
    return  {'message': 'Patient Management System API'}


@app.get("/about")
def about():
    return {'message': "A fully functional API to manage your patient records"}



@app.get('/view')
def view():
    data = load_data()

    return data


@app.get("/patient/{patient_id}")
def view_patient(patient_id:str = Path(..., description='This should be the id of the patient', example='P001')):
    ## load all the patients
    data = load_data()

    if patient_id in data:
        return data[patient_id]
    return HTTPException(status_code=404, detail="Patient not found")



@app.get('/sort')
def sort_patients(sort_by: str = Query(..., description='Sort on the basis of height, weight or bmi'), order: str = Query('asc', description='sort in asc or desc order')):
    
    valid_fields = ['height', 'weight', 'bmi']

    if sort_by not in  valid_fields:
        raise HTTPException(status_code=400, detail=f"invalid field, select from {valid_fields}")
    
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail='ivalid order select between asc and desc')
    
    data = load_data()

    sort_order = True if order=='desc' else False

    sorted_data = sorted(data.values(), key=lambda  x: x.get(sort_by, 0), reverse=sort_order)

    return sorted_data



@app.post('/create')
def create_patient(patient: Patient):
    
    ## load existing data 
    data = load_data()


    ## check if the patient already exists 
    if patient.id in data:
        raise HTTPException(status_code=400, detail='Patient already exists')


    ## new patient add to the database 
    data[patient.id] = patient.model_dump(exclude=['id'])

    ## save into the json file
    save_data(data)

    return JSONResponse(status_code=200, content={'message':  'patient created successfully'})


