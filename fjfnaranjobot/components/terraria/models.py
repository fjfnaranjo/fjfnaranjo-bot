from fjfnaranjobot.db import DbField, DbRelation


class TerrariaProfile(DbRelation):
    fields = [
        DbField('id', 'INTEGER PRIMARY KEY'),
        DbField('aws_default_region'),
        DbField('aws_access_key_id'),
        DbField('aws_secret_access_key'),
        DbField('microapi_token'),
        DbField('tshock_token'),
        DbField('dns_name'),
    ]
