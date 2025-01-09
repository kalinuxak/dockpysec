import os
import subprocess
import re
import time
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Load environment variables
load_dotenv()
bot_token = os.getenv("TOKEN")
admin_chat_id = os.getenv("ADMIN_CHAT_ID")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# State storage for user interaction
user_states = {}

# Firewall management class class FirewallBuiltin: def __init__(self): self.init_firewallbuiltin() def run_command(self, command): try: subprocess.run(command, check=True, shell=True) time.sleep(0.1) except subprocess.CalledProcessError as e: logger.error(f"Command execution error: {e}") def allow_tcport(self, port, protocol="tcp"): if port: self.run_command(f"iptables -A INPUT -p {protocol} --dport {port} -j ACCEPT") def save_rules(self): self.run_command("iptables-save > /etc/iptables/rules.v4") def init_firewallbuiltin(self): self.run_command("iptables -F") self.run_command("iptables -X") self.run_command("iptables -P INPUT DROP") self.run_command("iptables -P FORWARD DROP") self.run_command("iptables -P OUTPUT ACCEPT") self.allow_tcport(80) self.allow_tcport(443) self.save_rules() def setup_firewall(self): self.run_command("iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT") self.run_command("iptables -A INPUT -p icmp -j ACCEPT") self.save_rules()

# Global firewall object
#firewall = FirewallBuiltin()


# Helper functions
async def send_message(update: Update, text: str, reply_markup=None):
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text(text, reply_markup=reply_markup)
        await update.callback_query.answer()


def clear_user_state(user_id):
    if user_id in user_states:
        del user_states[user_id]


async def check_admin(update: Update):
    if update.effective_user.id != admin_chat_id:
        await update.message.reply_text("You are not authorized to manage the firewall.")
        return False
    return True


# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    greeting_message = (
            "Welcome to the Firewall Bot! 🔥\n\n"
            "This bot allows you to manage firewall rules directly from Telegram.\n"
            "Please select an option below to get started."
    )
    buttons = [
        [InlineKeyboardButton("Add Rule", callback_data="menu_add_rule")],
        [InlineKeyboardButton("Help", callback_data="menu_help")],
        [InlineKeyboardButton("Exit", callback_data="menu_exit")],
    ]
    await send_message(update, greeting_message, InlineKeyboardMarkup(buttons))


async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if query.data == "menu_add_rule":
        await add_rule(update, context)
    elif query.data == "menu_help":
        await send_message(update, "Help is not implemented yet.")
    elif query.data == "menu_exit":
        await query.message.reply_text("Goodbye! 👋")
    await query.answer()


async def add_rule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_states[user_id] = {"direction": None, "protocol": None, "source_ip": None, "source_port": None,
                            "destination_ip": None, "destination_port": None}
    buttons = [
        [InlineKeyboardButton("INPUT", callback_data="rule_direction_input")],
        [InlineKeyboardButton("OUTPUT", callback_data="rule_direction_output")],
        [InlineKeyboardButton("FORWARD", callback_data="rule_direction_forward")],
    ]
    await send_message(update, "Select the rule direction:", InlineKeyboardMarkup(buttons))


async def handle_rule_direction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id

    direction = query.data.split("_")[-1].upper()
    user_states[user_id]["direction"] = direction

    buttons = [
        [InlineKeyboardButton("TCP", callback_data="rule_protocol_tcp")],
        [InlineKeyboardButton("UDP", callback_data="rule_protocol_udp")],
    ]
    await send_message(update, "Select the protocol for your rule:", InlineKeyboardMarkup(buttons))


async def handle_protocol_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id

    protocol = query.data.split("_")[-1].upper()
    user_states[user_id]["protocol"] = protocol

    buttons = [[InlineKeyboardButton("Any", callback_data="source_ip_any")]]
    await send_message(update, "Please enter the Source IP address:", InlineKeyboardMarkup(buttons))


async def handle_source_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    source_ip = update.message.text.strip()

    if source_ip.lower() == "any":
        user_states[user_id]["source_ip"] = "any"
    elif not re.match(r"^\d{1,3}(\.\d{1,3}){3}$", source_ip):
        await update.message.reply_text("Invalid IP address. Please enter a valid Source IP or select 'Any'.")
        return
    else:
        user_states[user_id]["source_ip"] = source_ip

    buttons = [[InlineKeyboardButton("Any", callback_data="source_port_any")]]
    await update.message.reply_text("Please enter the Source Port:", reply_markup=InlineKeyboardMarkup(buttons))


async def handle_rule_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    rule = user_states.get(user_id)

    if query.data == "confirm_rule" and rule:
        try:
            firewall.allow_tcport(rule["destination_port"], rule["protocol"].lower())
            result_message = "Rule executed successfully!"
        except Exception as e:
            result_message = f"Error executing rule: {e}"
        clear_user_state(user_id)
    else:
        result_message = "Rule creation canceled."
        clear_user_state(user_id)

    await query.message.reply_text(result_message)
    await query.answer()


# Main function
if __name__ == "__main__":
    app = ApplicationBuilder().token(bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_menu, pattern="^menu_"))
    app.add_handler(CallbackQueryHandler(handle_rule_direction, pattern="^rule_direction_"))
    app.add_handler(CallbackQueryHandler(handle_protocol_selection, pattern="^rule_protocol_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_source_ip))

    logger.info("Bot is running...")
    app.run_polling()
