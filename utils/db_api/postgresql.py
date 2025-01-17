from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from data import config
from enums.enums import ResourcesType


class Database:

    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME
        )

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=1)
        ])
        return sql, tuple(parameters.values())

# USERS TABLE QUERIES
    async def add_user(self, user_id):
        sql = "INSERT INTO users (user_id) VALUES ($1) returning *"
        return await self.execute(sql, user_id, fetch=True)

    async def select_all_users(self):
        sql = "SELECT * FROM users"
        return await self.execute(sql, fetch=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM Users"
        return await self.execute(sql, fetchval=True)

    async def update_user_status(self, user_id, status: str = 'passive'):
        sql = "UPDATE users SET status=$2 WHERE user_id=$1"
        return await self.execute(sql, user_id, status, execute=True)


# CHANNELS TABLE QUERIES
    async def add_channel(self, channel_id, channel_link):
        sql = "INSERT INTO channels (channel_id, channel_link) VALUES ($1, $2) returning *"
        return await self.execute(sql, channel_id, channel_link)

    async def select_all_channels(self):
        sql = "SELECT * FROM channels"
        return await self.execute(sql, fetch=True)

    async def select_channel(self, **kwargs):
        sql = "SELECT * FROM channels WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def delete_channel(self, channel_id):
        sql = "DELETE FROM channels WHERE channel_id=$1"
        return await self.execute(sql, channel_id, execute=True)


# SETTINGS TABLE QUERIES
    async def add_settings(self, name, value):
        sql = "INSERT INTO settings (name, value) VALUES ($1, $2) returning *"
        return await self.execute(sql, name, value)

    async def select_all_settings(self):
        sql = "SELECT * FROM settings"
        return await self.execute(sql, fetch=True)

    async def select_settings(self):
        sql = "SELECT * FROM settings"
        return await self.execute(sql, fetchrow=True)

    async def update_settings_status(self, id, value):
        sql = "UPDATE settings SET value=$1 WHERE id=$2"
        return await self.execute(sql, value, id, execute=True)

    async def delete_setting(self, name):
        sql = "DELETE FROM settings WHERE name=$1"
        return await self.execute(sql, name, execute=True)


# MAILING TABLE QUERIES
    async def add_new_mailing(self, user_id, message_id, reply_markup, mail_type, type):
        sql = "INSERT INTO mailing (user_id, message_id, reply_markup, mail_type, type) VALUES ($1, $2, $3, $4, $5) RETURNING *"
        return await self.execute(sql, user_id, message_id, reply_markup, mail_type, type, fetchrow=True)

    async def update_mailing_status(self, status, id):
        sql = "UPDATE mailing SET status=$1 WHERE id=$2"
        return await self.execute(sql, status, id, execute=True)

    async def update_mailing_results(self, send, not_send, offset, id):
        sql = """UPDATE mailing SET send=$1, not_send=$2, "offset"=$3 WHERE id=$4"""
        return await self.execute(sql, send, not_send, offset, id, execute=True)

    async def select_mailing(self):
        sql = "SELECT * FROM mailing"
        return await self.execute(sql, fetchrow=True)

    async def select_users_mailing(self, offset, status='active'):
        sql = "SELECT * FROM users WHERE status = $2 ORDER BY id OFFSET $1;"
        return await self.execute(sql, offset, status, fetch=True)

    async def delete_mailing(self):
        await self.execute("DELETE FROM mailing WHERE TRUE", execute=True)

# JOIN REQUESTS TABLE QUERIES
    async def add_join_requests(self, user_id, chat_id):
        sql = "INSERT INTO join_requests (user_id, chat_id) VALUES($1, $2) returning *"
        return await self.execute(sql, user_id, chat_id, fetchrow=True)

    async def select_join_requests(self, **kwargs):
        sql = "SELECT * FROM join_requests WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def delete_join_requests(self, **kwargs):
        sql = "DELETE FROM join_requests WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        await self.execute(sql, *parameters, execute=True)

# RESOURCES TABLE QUERIES
    async def add_resource(self, button_key, url):
        sql = "INSERT INTO resources (button_key, url) VALUES ($1, $2) returning *"
        return await self.execute(sql,button_key, url, fetchrow=True)

    async def select_all_resources(self):
        sql = "SELECT * FROM resources"
        return await self.execute(sql, fetch=True)

    async def select_resource(self, **kwargs):
        sql = "SELECT * FROM resources WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def get_all_resources_by_button_key(self, button_key):
        sql = "SELECT * FROM resources WHERE button_key=$1"
        return await self.execute(sql, button_key, fetch=True)

    async def select_all_resources_by_button_key(self, button_key):
        sql = "SELECT * FROM resources WHERE button_key=$1"
        return await self.execute(sql, button_key, fetch=True)

    async def delete_resource(self, **kwargs):
        sql = "DELETE FROM resources WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, execute=True)


# BUTTONS TABLE QUERIES
    async def add_button(self, text, key):
        sql = "INSERT INTO buttons (text, key) VALUES ($1, $2) returning *"
        return await self.execute(sql, text, key, fetchrow=True)

    async def select_all_buttons(self):
        sql = "SELECT * FROM buttons"
        return await self.execute(sql, fetch=True)

    async def select_button(self, **kwargs):
        sql = "SELECT * FROM buttons WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    async def update_button(self, text, key):
        sql = "UPDATE buttons SET text=$2 WHERE key=$1"
        return await self.execute(sql, text, key, execute=True)

    async def delete_button(self, **kwargs):
        sql = "DELETE FROM buttons WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, execute=True)


# COUNT FUNCTION
    async def count_all_users(self):
        res = {}
        all_res = await self.execute("SELECT COUNT(*) FROM users", fetchval=True)
        if all_res:
            res['all'] = all_res

        active_res = await self.execute("SELECT COUNT(*) FROM users WHERE status='active'", fetchval=True)
        if active_res:
            res['active'] = active_res
        else:
            res['active'] = 0

        count_daily_users = await self.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) = CURRENT_DATE;",
                                               fetchval=True)
        if count_daily_users:
            res['daily_users'] = count_daily_users
        else:
            res['daily_users'] = 0

        count_weekly_users = await self.execute(
            """SELECT COUNT(*) FROM users WHERE created_at >= CURRENT_DATE - INTERVAL '1 week' AND created_at < CURRENT_DATE + INTERVAL '1 day';""",
            fetchval=True)
        if count_weekly_users:
            res['weekly_users'] = count_weekly_users
        else:
            res['weekly_users'] = 0

        count_monthly_users = await self.execute(
            """SELECT COUNT(*) FROM users WHERE created_at >= CURRENT_DATE - INTERVAL '1 month' AND created_at < CURRENT_DATE + INTERVAL '1 day';""",
            fetchval=True)
        if count_monthly_users:
            res['monthly_users'] = count_monthly_users
        else:
            res['monthly_users'] = 0

        return res


    async def count_ads(self):
        return await self.execute("SELECT COUNT(*) FROM ads", fetchval=True)


