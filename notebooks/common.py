import sqlalchemy

url = 'postgresql://localhost:5432/cc_traces'
con = sqlalchemy.create_engine(url)