import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    FOOD_DAY = os.environ.get('FOOD_DAY')
