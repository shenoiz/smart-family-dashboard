import json
import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_ALLOWED_USERS, IOT_DEVICES

TODO_FILE = "data/todos.json"


def load_todos():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE) as f:
            return json.load(f)

    return {"yours": [], "wife": []}


def save_todos(todos):
    with open(TODO_FILE, "w") as f:
        json.dump(todos, f, indent=2)


def is_allowed(update: Update) -> bool:
    return update.effective_user.id in TELEGRAM_ALLOWED_USERS


async def cmd_add(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Usage: /add me Buy milk OR /add wife Call dentist"""

    if not is_allowed(update):
        return

    if len(ctx.args) < 2:
        await update.message.reply_text("Usage: /add me|wife <task>")
        return

    who = ctx.args[0].lower()
    task = " ".join(ctx.args[1:])
    person = "yours" if who == "me" else "wife"

    todos = load_todos()
    todos[person].append({"text": task, "done": False})
    save_todos(todos)

    try:
        from app import notify_todo_update

        notify_todo_update()
    except Exception:
        pass

    await update.message.reply_text(
        f"Added to {who}'s list: {task}"
    )


async def cmd_done(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Usage: /done me 0 (marks item 0 in your list done)"""

    if not is_allowed(update):
        return

    if len(ctx.args) < 2:
        await update.message.reply_text(
            "Usage: /done me|wife <item_number>"
        )
        return

    who = ctx.args[0].lower()
    idx = int(ctx.args[1])

    person = "yours" if who == "me" else "wife"

    todos = load_todos()

    if 0 <= idx < len(todos[person]):
        todos[person][idx]["done"] = True
        save_todos(todos)

        try:
            from app import notify_todo_update

            notify_todo_update()
        except Exception:
            pass

        await update.message.reply_text("Marked done!")
    else:
        await update.message.reply_text(
            f"Item {idx} not found. Use /list."
        )


async def cmd_list(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        return

    todos = load_todos()

    msg = "*Your list:*\n"

    for i, t in enumerate(todos["yours"]):
        status = "✓" if t["done"] else "□"
        msg += f"{status} {i}. {t['text']}\n"

    msg += "\n*Wife's list:*\n"

    for i, t in enumerate(todos["wife"]):
        status = "✓" if t["done"] else "□"
        msg += f"{status} {i}. {t['text']}\n"

    await update.message.reply_text(
        msg,
        parse_mode="Markdown",
    )


async def cmd_clear(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Usage: /clear me | /clear wife | /clear all"""

    if not is_allowed(update):
        return

    who = ctx.args[0].lower() if ctx.args else "all"

    todos = load_todos()

    if who in ("me", "all"):
        todos["yours"] = [
            t for t in todos["yours"]
            if not t["done"]
        ]

    if who in ("wife", "all"):
        todos["wife"] = [
            t for t in todos["wife"]
            if not t["done"]
        ]

    save_todos(todos)

    await update.message.reply_text(
        "Cleared completed items."
    )


async def handle_text(
    update: Update,
    ctx: ContextTypes.DEFAULT_TYPE,
):
    """Handle plain-text IoT commands like 'lights on'"""

    if not is_allowed(update):
        return

    text = update.message.text.lower().strip()

    if text in IOT_DEVICES:
        from iot_controller import send_iot_command

        topic, payload = IOT_DEVICES[text]
        send_iot_command(topic, payload)

        await update.message.reply_text(
            f"Done: {text}"
        )
    else:
        await update.message.reply_text(
            "Commands: /add /done /list /clear"
        )


def start_bot():
    app = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler("add", cmd_add)
    )
    app.add_handler(
        CommandHandler("done", cmd_done)
    )
    app.add_handler(
        CommandHandler("list", cmd_list)
    )
    app.add_handler(
        CommandHandler("clear", cmd_clear)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_text,
        )
    )

    print("Telegram bot started...")
    app.run_polling()


if __name__ == "__main__":
    start_bot()
