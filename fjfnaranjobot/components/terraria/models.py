from fjfnaranjobot.db import DbField, DbRelation


class TerrariaProfile(DbRelation):
    fields = [
        DbField('id', 'INTEGER PRIMARY KEY'),
        DbField('name', 'UNIQUE'),
        DbField('aws_default_region'),
        DbField('aws_access_key_id'),
        DbField('aws_secret_access_key'),
        DbField('instance_id'),
        DbField('microapi_token'),
        DbField('tshock_token'),
        DbField('dns_name'),
        DbField('status', 'BOOLEAN DEFAULT(0)', False),
        DbField('chat_id'),
    ]


class TerrariaActivityLogPortions(DbRelation):
    fields = [
        DbField('id', 'INTEGER PRIMARY KEY'),
        DbField('nickname'),
        DbField('username'),
        DbField('date', 'date'),
        DbField('portion'),
    ]


class TerrariaActivityLogDaily(DbRelation):
    fields = [
        DbField('id', 'INTEGER PRIMARY KEY'),
        DbField('nickname'),
        DbField('username'),
        DbField('date', 'date'),
        DbField('portions'),
    ]
