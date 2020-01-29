from telegram.ext import BasePersistence
from config import STORE_CHAT_DATA, STORE_USER_DATA
from config import DATABASE_URL
from collections import defaultdict
from psycopg2 import connect
import logging
from pickle import dumps, loads
from app.utils import tuple_from_key


class DBPersistence(BasePersistence):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        super().__init__(store_chat_data=STORE_CHAT_DATA, store_user_data=STORE_USER_DATA)
        self.conn = connect(DATABASE_URL)

    def flush(self):
        self.conn.close()
        self.logger.info("DB connection closed")

    def update_chat_data(self, chat_id, data):
        pass

    def update_user_data(self, user_id, data):
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT user_id FROM user_data WHERE user_id=%s", (user_id,))
                if cur.rowcount > 0:
                    cur.execute("UPDATE user_data SET user_data=%s WHERE user_id=%s", (dumps(data), user_id))
                else:
                    cur.execute("INSERT INTO user_data VALUES (%s, %s)", (user_id, dumps(data)))
                self.conn.commit()
        except Exception as e:
            self.logger.error("Caught error \"%s\" - user data for %s wasn`t updated", e, user_id)
        else:
            self.logger.info("user_data for user %s updated", user_id)

    def update_conversation(self, name, key, new_state):
        self.logger.debug("update conversation \"%s\" with key \"%s\" to state %s", name, key, new_state)
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT state FROM conversations WHERE name=%s AND key=%s", (name, str(key)))
                if cur.rowcount > 0:
                    cur.execute("UPDATE conversations SET state=%s WHERE name=%s AND key=%s",
                                (new_state, name, str(key)))
                else:
                    cur.execute("INSERT INTO conversations VALUES (%s, %s, %s)", (name, str(key), new_state))
                self.conn.commit()
        except Exception as e:
            self.logger.error("Caught error \"%s\" - conversation \"%s\"[%s] wasn`t updated", e, name, str(key))
        else:
            self.logger.info("conversations \"%s\" updated", name)

    def get_chat_data(self):
        pass

    def get_conversations(self, name):
        convs = defaultdict(dict)
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT key, state FROM conversations WHERE name=%s", (name,))
                for key, state in cur:
                    convs[tuple_from_key(key)] = state
        except Exception as e:
            self.logger.exception("Caught error \"%s\" - conversation \"%s\" wasn`t loaded", e, name)
        else:
            self.logger.info("conversation \"%s\" was loaded", name)
        finally:
            self.logger.debug("conversation \"%s\" is: %s", name, convs)
            return convs

    def get_user_data(self):
        user_data = defaultdict(dict)
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT * FROM user_data")
                for user_id, data in cur:
                    if data is None:
                        data = {}
                    else:
                        data = loads(data)
                    user_data[user_id] = data
        except Exception as e:
            self.logger.exception("Caught error \"%s\" - user_data wasn`t loaded" % e)
        else:
            self.logger.info("user_data was loaded")
        finally:
            self.logger.debug("user_data is: %s", user_data)
            return user_data
