import os

from fastapi import FastAPI,HTTPException
from secrets_connections import *
from file_utilities.file_utilities import *
from azure_database.azure_database_accessor import AzureDatabaseAccessor
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, registry
from sqlalchemy import Column,Integer,String,Boolean,Table,text, MetaData

import urllib



temp_path = tempfile.gettempdir()

azure_database_accessor = AzureDatabaseAccessor(CONNECTION_STRING_MY_SQL)
print(azure_database_accessor.connection_string_mysql)

params = urllib.parse.quote_plus (azure_database_accessor.connection_string_mysql)
conn_str = 'mssql+pyodbc:///?odbc_connect={}'.format(params)
engine = create_engine(conn_str,echo=True)

Session=sessionmaker(bind=engine)
session=Session()


todo_app = FastAPI()


metadata=MetaData()

mapper_registry=registry()

todos=Table('todos',
            mapper_registry.metadata,
            Column('id',Integer, 
                        autoincrement=True, primary_key=True),
            Column('text', String, nullable=False),
            Column('is_done', Boolean, default=False))

class Todo(object):

    def __init__(self, text, is_done):
        self.text=text
        self.is_done=is_done


mapper_registry.map_imperatively(Todo,todos)


@todo_app.post('/create')
async def create_todo(text:str, is_done: bool=False):
    todo=Todo(text=text, is_done=is_done)
    session.add(todo)
    session.commit()
    return{'todo added: ', todo.text}


@todo_app.get('/done')
async def get_todos():
    todos_query=session.query(Todo)
    done_todos_query=todos_query.filter(Todo.is_done==True)
    return done_todos_query.all()

@todo_app.put("/update/{id}")
async def update_todo(
    id: int,
    new_text: str = "",
    is_done: bool = False
):
    todo_query = session.query(Todo).filter(Todo.id==id)
    todo = todo_query.first()
    if new_text:
        todo.text = new_text
    todo.is_done = is_done
    session.add(todo)
    session.commit()

@todo_app.delete("/delete/{id}")
async def delete_todo(id: int):
    todo = session.query(Todo).filter(Todo.id==id).first()
    session.delete(todo)
    session.commit()
    return {"todo deleted": todo.text}







