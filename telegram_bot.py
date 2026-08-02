import json
import os
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_ALLOWED_USERS, IOT_DEVICES

TODO_FILE = "data/todos.json"


def load_todos():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE) as f:
            return json.load(f)
    return {"him": [], "her": []}


def save_todos(todos):
    with open(TODO_FILE, "w") as f:
        json.dump(todos, f, indent=2)


def is_allowed(update):
    return update.effective_user.id in TELEGRAM_ALLOWED_USERS


async def cmd_add(update, ctx):
    """Usage: /add him Buy milk   OR   /add her Call dentist"""
    if not is_allowed(update):
        return
    if len(ctx.args) < 2:
        await update.message.reply_text("Usage: /add him|her <task>")
        return
    who = ctx.args[0].lower()
    if who not in ("him", "her"):
        await update.message.reply_text("Second word must be him or her")
        return
    task = " ".join(ctx.args[1:])
    todos = load_todos()
    todos[who].append({"text": task, "done": False})
    save_todos(todos)

    from audio_manager import play_sound

    play_sound("todo_added")

    try:
        from audio_manager import play_sound

        play_sound("todo_added")
    except Exception:
        pass
    try:
        from app import notify_todo_update

        notify_todo_update()
    except Exception:
        pass
    await update.message.reply_text(f"Added to {who}'s list: {task}")


async def cmd_done(update, ctx):
    """Usage: /done him 0   OR   /done her 2"""
    if not is_allowed(update):
        return
    if len(ctx.args) < 2:
        await update.message.reply_text("Usage: /done him|her <number>")
        return
    who = ctx.args[0].lower()
    if who not in ("him", "her"):
        await update.message.reply_text("Second word must be him or her")
        return
    idx = int(ctx.args[1])
    todos = load_todos()
    if 0 <= idx < len(todos[who]):
        todos[who][idx]["done"] = True
        save_todos(todos)
        try:
            from app import notify_todo_update

            notify_todo_update()
        except Exception:
            pass
        await update.message.reply_text("Marked done!")
    else:
        await update.message.reply_text(f"Item {idx} not found. Use /list.")


async def cmd_list(update, ctx):
    if not is_allowed(update):
        return
    todos = load_todos()
    msg = "*Him's list:*\n"
    for i, t in enumerate(todos["him"]):
        icon = "\u2705" if t["done"] else "\u2b1c"
        msg += f'{icon} {i}. {t["text"]}\n'
    if not todos["him"]:
        msg += "_empty_\n"
    msg += "\n*Her's list:*\n"
    for i, t in enumerate(todos["her"]):
        icon = "\u2705" if t["done"] else "\u2b1c"
        msg += f'{icon} {i}. {t["text"]}\n'
    if not todos["her"]:
        msg += "_empty_\n"
    await update.message.reply_text(msg, parse_mode="Markdown")


async def cmd_clear(update, ctx):
    """Usage: /clear him  |  /clear her  |  /clear all"""
    if not is_allowed(update):
        return
    who = ctx.args[0].lower() if ctx.args else "all"
    todos = load_todos()
    if who in ("him", "all"):
        todos["him"] = [t for t in todos["him"] if not t["done"]]
    if who in ("her", "all"):
        todos["her"] = [t for t in todos["her"] if not t["done"]]
    save_todos(todos)
    await update.message.reply_text("Cleared completed items.")


async def handle_text(update, ctx):
    if not is_allowed(update):
        return
    text = update.message.text.lower().strip()
    if text in IOT_DEVICES:
        from iot_controller import send_iot_command
        from audio_manager import play_sound

        topic, payload = IOT_DEVICES[text]
        send_iot_command(topic, payload)
        play_sound("alert")
        await update.message.reply_text(f"Done: {text}")
    else:
        await update.message.reply_text("Commands: /add /done /list /clear")


def start_bot():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("add", cmd_add))
    app.add_handler(CommandHandler("done", cmd_done))
    app.add_handler(CommandHandler("list", cmd_list))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("Telegram bot started...")
    app.run_polling(stop_signals=None)


if __name__ == "__main__":
    start_bot()
