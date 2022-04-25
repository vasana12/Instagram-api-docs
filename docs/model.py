import certifi
from mongoengine import connect, disconnect_all
from mongoengine import document, fields
from setting import ACCOUNT_DB_HOST, DATA_DB_HOST, IS_WINDOWS

if IS_WINDOWS:
    connect(host=ACCOUNT_DB_HOST,
            alias='instagram_account', tlsCAFile=certifi.where())
    connect(host=DATA_DB_HOST,
            alias='instagram_data', tlsCAFile=certifi.where())
else:
    connect(host=ACCOUNT_DB_HOST,
            alias='instagram_account')
    connect(host=DATA_DB_HOST,
            alias='instagram_data')

#instagram_account

class Proxy(document.Document):
    username = fields.StringField()
    password = fields.StringField()
    host = fields.StringField()
    port = fields.StringField()
    status = fields.StringField(choices=['available', "using", 'unavailable'])
    meta = {
            'db_alias': 'instagram_data',
            'collection': 'proxy',
            'strict': False
            }
class Config(document.Document):
    sig_key_version = fields.StringField()
    ig_sig_key = fields.StringField()
    api_domain = fields.StringField()
    api_url = fields.StringField()
    meta = {
            'db_alias': 'instagram_data',
            'collection': 'config',
            'strict': False
            }
class Device(document.Document):
    app_version = fields.StringField()
    android_version = fields.StringField()
    android_release = fields.StringField()
    dpi = fields.StringField()
    resolution = fields.StringField()
    manufacturer = fields.StringField()
    model = fields.StringField()
    cpu = fields.StringField()
    version_code = fields.StringField()
    user_agent = fields.StringField()

    meta = {
            'db_alias': 'instagram_data',
            'collection': 'device',
            'strict': False
            }

class DeviceSetting(document.EmbeddedDocument):
    app_version = fields.StringField()
    android_version = fields.StringField()
    android_release = fields.StringField()
    dpi = fields.StringField()
    resolution = fields.StringField()
    manufacturer = fields.StringField()
    model = fields.StringField()
    cpu = fields.StringField()
    version_code = fields.StringField()
    user_agent = fields.StringField()


class RawAccount(document.Document):
    username = fields.StringField(required=True)
    password = fields.StringField(required=True)
    status = fields.StringField(choices=['setting_before', 'setting_done'])

    meta = {
        'db_alias': 'instagram_data',
        'collection': 'raw_account',
        'indexes': ['#status'],
        'strict': False
    }



class Session(document.EmbeddedDocument):
    csrftoken = fields.StringField()
    ds_user_id = fields.StringField()
    ig_did = fields.StringField()
    ig_nrcb = fields.StringField()
    mid = fields.StringField()
    rur = fields.StringField()
    sessionid = fields.StringField()


class Uuids(document.EmbeddedDocument):
    phone_id = fields.StringField()
    uuid = fields.StringField()
    client_session_id = fields.StringField()
    advertising_id = fields.StringField()
    device_id = fields.StringField()


class BlockedActions(document.EmbeddedDocument):
    likes = fields.BooleanField()
    unlikes = fields.BooleanField()
    follows = fields.BooleanField()
    unfollows = fields.BooleanField()
    comments = fields.BooleanField()
    blocks = fields.BooleanField()
    unblocks = fields.BooleanField()
    messages = fields.BooleanField()


class Total(document.EmbeddedDocument):
    likes = fields.IntField()
    unlikes = fields.IntField()
    follows = fields.IntField()
    unfollows = fields.IntField()
    comments = fields.IntField()
    blocks = fields.IntField()
    unblocks = fields.IntField()
    messages = fields.IntField()
    archived = fields.IntField()
    unarchived = fields.IntField()
    stories_viewed = fields.IntField()


class Checkpoint(document.EmbeddedDocument):
    blocked_actions = fields.EmbeddedDocumentField(BlockedActions)
    start_time = fields.DateTimeField()
    total = fields.EmbeddedDocumentField(Total)
    total_requests = fields.IntField()
    meta = {
        'strict': False #시벌.. 이거때매 한참 고생했네
    }


class Account(document.Document):
    username = fields.StringField(required=True)
    password = fields.StringField(required=True)
    channel = fields.StringField(required=True)
    client_name = fields.StringField()
    last_login = fields.DateTimeField()
    checkpoint = fields.EmbeddedDocumentField(Checkpoint)
    status = fields.StringField(choices=['available', 'login', 'checkpoint_required', 'unavailable'])
    device_setting = fields.EmbeddedDocumentField(DeviceSetting)
    mobile_session = fields.BooleanField()
    session = fields.EmbeddedDocumentField(Session)
    user_agent = fields.StringField()
    uuids = fields.EmbeddedDocumentField(Uuids)

    meta = {'db_alias': 'instagram_account',
            'collection': 'account',
            'indexes': ['#status'],
            'ordering': ['last_login'],
            'strict': False}



# raw datas
class Like(document.EmbeddedDocument):
    username = fields.StringField(required=True)


class Comment(document.EmbeddedDocument):
    username = fields.StringField(required=True)
    text = fields.StringField()
    hashtags = fields.ListField()


class Post(document.EmbeddedDocument):
    link = fields.StringField(required=True)
    crawled_at = fields.DateTimeField()
    rank = fields.IntField()
    username = fields.StringField(required=True)
    posted_at = fields.DateTimeField()
    media_type = fields.StringField()
    n_like = fields.IntField()
    n_comment = fields.IntField()
    hashtags = fields.ListField()
    comments = fields.EmbeddedDocumentListField(Comment)
    likes = fields.EmbeddedDocumentListField(Like)


class Hashtag(document.Document):
    keyword = fields.StringField(required=True)
    max_recent_post = fields.IntField()
    max_top_post = fields.IntField()
    crawled_at = fields.DateTimeField()
    n_post = fields.IntField()
    recent_posts = fields.EmbeddedDocumentListField(Post)
    top_posts = fields.EmbeddedDocumentListField(Post)
    meta = {'db_alias': 'instagram_data',
            'collection': 'hashtag',
            'indexes': ['#keyword'],
            'ordering': ['crawled_at'],
            'strict': False}


class User(document.Document):
    username = fields.StringField(required=True)
    max_post = fields.IntField()
    max_follower = fields.IntField()
    max_followee = fields.IntField()
    max_comment = fields.IntField()
    crawled_at = fields.DateTimeField()
    userid = fields.StringField(required=True)
    n_post = fields.IntField()
    n_follower = fields.IntField()
    n_followee = fields.IntField()
    recent_posts = fields.EmbeddedDocumentListField(Post)
    followers = fields.ListField()
    followees = fields.ListField()
    meta = {'db_alias': 'instagram_data',
            'collection': 'user',
            'indexes': ['#username'],
            'ordering': ['crawled_at'],
            'strict': False}

#
# if __name__ == '__main__':
#     '''
#     test
#     '''
#     query = {"status": "available", "mobile_session": True}
#     account = Account.objects(**query).first()
#     print(account.username)

