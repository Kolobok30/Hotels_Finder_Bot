from peewee import SqliteDatabase, Model, IntegerField, DateTimeField, TextField
from typing import Dict, List
from datetime import datetime

db = SqliteDatabase(r'database/history.db')


class History(Model):
    class Meta:
        database = db


class Result(History):
    user_id = IntegerField()
    command = TextField()
    date = DateTimeField()
    result = TextField()


Result.create_table()


def history_write(data: Dict, results: List) -> None:
    with db:
        while Result.select().where(Result.user_id == data['user_id']).count() > 4:
            first_result = Result.get(Result.user_id == data['user_id'])
            first_result.delete_instance()
        Result.create(
            user_id=data['user_id'],
            date=datetime.utcnow().replace(microsecond=0),
            command=data['cmd'],
            result=';\n'.join(results)
        )

