import os

from flask import Flask
from app import app

if __name__ == '__main__':
    app = Flask(__name__, template_folder='../Frontend', static_folder='../Frontend')
