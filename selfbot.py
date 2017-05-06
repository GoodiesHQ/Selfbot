#!/usr/bin/env python3
from collections import deque
from config import Settings
from contextlib import suppress
import asyncio
import discord
import os
import pickle

client = discord.Client()  # "Do not use global variables" - NSA Programming Recommendations

class Items:
    """Some locks that will be useful for preventing functions from being run twice"""
    INV_LOCK = asyncio.Lock()
    INV_QUEUE = asyncio.Queue()
    INV_SET = set()
    INC_TASK = None

class Utils:
    """Various utilities used throughout the program"""
    ALL_COMMANDS = ["say", "spam", "invite", "purge",]

    @staticmethod
    def user_invited(userid):
        if not os.path.isfile(Settings.INVITE_DB):
            invites = set()
            with open(Settings.INVITE_DB, "wb") as db:
                pickle.dump(invites, db)
        with open(Settings.INVITE_DB, "rb") as db:
            invites = pickle.load(db)
            return userid in invites

    @staticmethod
    def should_invite(userid):
        return not bool(Utils.user_invited(userid) or userid in Items.INV_SET)

    @staticmethod
    def escape(msg):
        """Prevents people from running commands that can potentially call other commands"""
        if any(msg.startswith(Utils.prefixed(cmd)) for cmd in Utils.ALL_COMMANDS):
            return "\u200b{}".format(msg)
        return msg

    @staticmethod
    def prefixed(s):
        """Returns s with the global prefix prefix"""
        return "{}{}".format(Settings.PREFIX, s)

    @staticmethod
    def trycast(new_type, value, default=None):
        """Function for casting that returns a default value on error"""
        try:
            default = new_type(value)
        finally:
            return default

    @staticmethod
    async def invite_user(message, user):
        await client.send_message(user, Settings.INVITE_MSG.format(username=user.name, servername=server.name, link=link))
        with suppress(KeyError):
            Items.INV_SET.remove(user.id)


async def worker(queue, coro, count:int=1, delay:float=1.0, loop:asyncio.AbstractEventLoop=None):
    """Creates an asynchronous worker task. Sort of simulates how I imagine an async pool would look"""
    if count <= 0:
        raise RuntimeError("count must be > 0")
    loop = loop or asyncio.get_event_loop()
    tasks = []
    while True:
        while len(tasks) < count and not queue.empty():
            tmp_args, tmp_kwargs = await queue.get()
            tasks.append(coro(*tmp_args, **tmp_kwargs))
        if tasks:
            await asyncio.gather(*tasks, loop=loop)
            tasks = []
        await asyncio.sleep(delay)


class Commands:
    @staticmethod
    async def say(message, args):
        msg = ' '.join(args) if args else ""
        msg = Utils.escape(msg)
        if msg:
            await client.send_message(message.channel, msg)

    @staticmethod
    async def spam(message, args):
        msg = ' '.join(args) if args else Settings.SPAM_MSG
        msg = Utils.escape(msg)
        for i in range(Settings.SPAM_CNT):
            await client.send_message(message.channel, msg)
            await asyncio.sleep(Settings.SPAM_DELAY)

    @staticmethod
    async def invite(message, args):
        for user in message.server.members:
            if Utils.should_invite(user.id):
                Items.INV_SET.add(user.id)
                args = (message, user)
                kwargs = dict()
                await Items.INV_QUEUE.put((args, kwargs))

    @staticmethod
    async def purge(message, args):
        cnt = Utils.trycast(int, args[0], Settings.PURGE_CNT) if args else Settings.PURGE_CNT
        if cnt <= 0:
            return
        async for msg in client.logs_from(message.channel, limit=9999):
            if cnt == 0:
                break
            if msg.author == client.user:
                await client.delete_message(msg)
                cnt -= 1

def cmd(message, command):
    """Returns true if the message 'message' is executing the command 'command'"""
    return message.content.startswith(Utils.prefixed(command))

def cmd_args(message, command):
    assert cmd(message, command)
    return [] if ' ' not in message.content else message.content.split(' ')[1:]

async def handle(command, message, coro):
    "A coroutine that handles commands by executing the provided coro"
    if cmd(message, command):
        await coro(message, cmd_args(message, command))
    return False

# Various message handlers that can be used in different contexts
async def private_message(message):
    assert message.server is None

async def server_message(message):
    assert message.server is not None

async def selfbot_private_message(message):
    assert message.server is None and message.author == client.user
    await handle("spam", message, Commands.spam)
    await handle("purge", message, Commands.purge)

async def selfbot_server_message(message):
    assert message.server is not None and message.author == client.user
    await handle("spam", message, Commands.spam)
    await handle("invite", message, Commands.invite)
    await handle("purge", message, Commands.purge)

@client.event
async def on_message(message):
    if not any(message.content.startswith(Utils.prefixed(cmd)) for cmd in Utils.ALL_COMMANDS):
        return
    if Settings.DELETE_CMD is True:
        await Commands.purge(message, ("1",))
    if message.server is not None:
        if message.author == client.user:
            await selfbot_server_message(message)
        await server_message(message)
    else:
        if message.author == client.user:
            await selfbot_private_message(message)
        await private_message(message)
    return True

@client.event
async def on_ready():
    print("Logged in as {} ({})".format(client.user.name, client.user.id))
    Items.INV_TASK = client.loop.create_task(worker(Items.INV_QUEUE, Utils.invite_user, 2, 60.0))

client.run("mfa.q8PZIZm7cCpWFBAnscsYZkY3aWYgXcR9994s4xnTq9WW3WDtS-_TdDiZ5Kq2AHxPHy11XaBNxPkjzaWg0A3K", bot=False) #gitignore
client.run("TOKEN", bot=False)
