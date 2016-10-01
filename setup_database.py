#!/usr/local/bin/python3.5

from sqlalchemy import Column, Integer, SmallInteger, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
 
Base = declarative_base()

class noise_test(Base):
    __tablename__ = 'noise_test'
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer)
    board_id = Column(Integer)

class noise_test_ch_result(Base):
    __tablename__ = 'noise_test_ch_result'
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer)
    fegain = Column(SmallInteger)
    feshape = Column(SmallInteger)
    baseline = Column(SmallInteger)
    ch_id = Column(SmallInteger)
    ch_rms = Column(Float)

# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///database_noiseMeasurement.db')
 
# Create all tables in the engine
Base.metadata.create_all(engine)
