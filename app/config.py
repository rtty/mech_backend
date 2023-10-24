import os
from os.path import dirname, join


class Config:
    JWT_SECRET = os.getenv('JWT_SECRET', 'custom-secret')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    TEST_MAPPING_PATH = os.getenv(
        'TEST_MAPPING_PATH', join(dirname(__file__), '../app/parser/Data/Brake.xlsx')
    )
    PARSER_OUT_PATH = os.getenv(
        'PARSER_OUT_PATH', join(dirname(__file__), '../app/parser/parser_full.out')
    )
