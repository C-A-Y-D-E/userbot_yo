# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for managing events.
 One of the main components of the userbot. """

from telethon import events
import asyncio
from userbot import bot, BOTLOG, BOTLOG_CHATID
from traceback import format_exc
from time import gmtime, strftime
import math
import subprocess
import sys
import traceback
import datetime


def register(**args):
    """ Register a new event. """
    pattern = args.get('pattern', None)
    disable_edited = args.get('disable_edited', False)
    ignore_unsafe = args.get('ignore_unsafe', False)
    forwards = args.get('forwards', False)
    unsafe_pattern = r'^[^/!#@\$A-Za-z]'

    if pattern is not None and not pattern.startswith('(?i)'):
        args['pattern'] = '(?i)' + pattern

    if "disable_edited" in args:
        del args['disable_edited']

    if "ignore_unsafe" in args:
        del args['ignore_unsafe']

    if "forwards" in args:
        del args['forwards']

    if pattern:
        if not ignore_unsafe:
            args['pattern'] = pattern.replace('^.', unsafe_pattern, 1)

    def decorator(func):
        if not disable_edited:
            bot.add_event_handler(func, events.MessageEdited(**args))
        bot.add_event_handler(func, events.NewMessage(**args))

        return func

    return decorator


def errors_handler(func):
    async def wrapper(errors):
        try:
            await func(errors)
        except BaseException:

            date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            new = {
                'error': str(sys.exc_info()[1]),
                'date': datetime.datetime.now()
            }

            text = "**USERBOT ERROR REPORT**\n\n"

            link = "[here](https://t.me/PaperplaneExtendedSupport)"
            text += "If you wanna you can report it"
            text += f"- just forward this message {link}.\n"
            text += "Nothing is logged except the fact of error and date\n"

            ftext = "\nDisclaimer:\nThis file uploaded ONLY here,"
            ftext += "\nwe logged only fact of error and date,"
            ftext += "\nwe respect your privacy,"
            ftext += "\nyou may not report this error if you've"
            ftext += "\nany confidential data here, no one will see your data\n\n"

            ftext += "--------BEGIN USERBOT TRACEBACK LOG--------"
            ftext += "\nDate: " + date
            ftext += "\nGroup ID: " + str(errors.chat_id)
            ftext += "\nSender ID: " + str(errors.sender_id)
            ftext += "\n\nEvent Trigger:\n"
            ftext += str(errors.text)
            ftext += "\n\nTraceback info:\n"
            ftext += str(traceback.format_exc())
            ftext += "\n\nError text:\n"
            ftext += str(sys.exc_info()[1])
            ftext += "\n\n--------END USERBOT TRACEBACK LOG--------"

            command = "git log --pretty=format:\"%an: %s\" -5"

            ftext += "\n\n\nLast 5 commits:\n"

            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await process.communicate()
            result = str(stdout.decode().strip()) \
                + str(stderr.decode().strip())

            ftext += result

            file = open("error.log", "w+")
            file.write(ftext)
            file.close()

            if BOTLOG:
                await errors.client.send_file(
                    BOTLOG_CHATID,
                    "error.log",
                    caption=text,
                )
                return

    return wrapper
