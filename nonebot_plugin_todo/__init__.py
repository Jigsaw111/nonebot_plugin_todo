from nonebot.plugin import on_shell_command, require
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import (
    unescape,
    Bot,
    Event,
    Message,
    PrivateMessageEvent,
    GroupMessageEvent,
)
from nonebot import get_bots

from .parser import todo_parser, handle_scheduler

scheduler = require("nonebot_plugin_apscheduler").scheduler

# 注册 shell_like 事件响应器
todo = on_shell_command("todo", parser=todo_parser, priority=5)

# 每分钟进行一次检测
@scheduler.scheduled_job("cron", minute="*", id="todo")
async def _():

    bots = get_bots()

    args = handle_scheduler()

    for bot in bots.values():
        for job in args.jobs:
            await bot.send_msg(
                user_id=job["user_id"],
                group_id=job["group_id"],
                message=Message(job["message"]),
            )


@todo.handle()
async def _(bot: Bot, event: Event, state: T_State):
    args = state["args"]
    args.user_id = event.user_id if isinstance(event, PrivateMessageEvent) else None
    args.group_id = event.group_id if isinstance(event, GroupMessageEvent) else None
    args.is_admin = (
        event.sender.role in ["admin", "owner"]
        if isinstance(event, GroupMessageEvent)
        else False
    )
    args.is_superuser = str(event.user_id) in bot.config.superusers
    if hasattr(args, "message"):
        args.message = unescape(args.message)

    if hasattr(args, "handle"):
        args = args.handle(args)
        if args.message:
            await bot.send_msg(
                user_id=args.user_id,
                group_id=args.group_id,
                message=Message(args.message),
            )
