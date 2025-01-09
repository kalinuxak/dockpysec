import signal
import os
import subprocess
import requests
import re
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

load_dotenv()
bot_token = os.getenv("FW_TOKEN")
chat_id = os.getenv("ADMIN_ID")


class Firewallbuiltin:
    def __init__(self):
        self.init_firewallbuiltin()

    def run_command(self, command):
        try:
            subprocess.run(command, check=True, shell=True)
            time.sleep(0.1)
        except subprocess.CalledProcessError as e:
            print(f"Ошибка выполнения команды: {e}")

    def allow_tcport(self, port, protocol="tcp"):
        self.run_command(f"iptables -A INPUT -p {protocol} --dport {port} -j ACCEPT")

    def allow_udport(self, port, protocol="udp"):
        self.run_command(f"iptables -A INPUT -p {protocol} --dport {port} -j ACCEPT")

    def save_rules(self):
        self.run_command("iptables-save > /etc/iptables/rules.v4")

    def load_rules(self):
        self.run_command("iptables-restore < /etc/iptables/rules.v4")


    def init_firewallbuiltin(self):
        self.run_command("iptables -F")
        self.run_command("iptables -X")
        self.run_command("iptables -P INPUT DROP")
        self.run_command("iptables -P FORWARD DROP")
        self.run_command("iptables -P OUTPUT ACCEPT")
        self.run_command("iptables -A INPUT -p udp -s 0.0.0.0 -d 0.0.0.0 -j ACCEPT")
        self.run_command("iptables -A INPUT -p udp -s 255.255.255.255 -d 0.0.0.0 -j ACCEPT")
        self.run_command("iptables -A INPUT -p tcp -s 185.203.1.214 --dport 16661 -j ACCEPT")
        self.run_command("iptables -A INPUT -d 127.0.1.1 -s 127.0.0.1 -j ACCEPT")
        self.run_command("iptables -A INPUT -d 127.0.0.1 -s 127.0.1.1 -j ACCEPT")
        self.run_command("iptables -A INPUT -d 0.0.0.0 -s 127.0.0.1 -j ACCEPT")
        self.run_command("iptables -A INPUT -d 0.0.0.0 -s 127.0.1.1 -j ACCEPT")
        self.allow_tcport(80)
        self.allow_tcport(443)
        self.allow_tcport(16661)
        self.allow_tcport(6379)
        self.allow_tcport(6969)
        self.allow_tcport(53)
        self.allow_tcport(55)
        self.allow_tcport(5355)
        self.allow_tcport()
        self.allow_tcport(6969)


        self.run_command("iptables -A INPUT -p tcp -s 185.203.1.214 -j ACCEPT")


    def setup_firewall(self):
        self.run_command("iptables -A INPUT -i lo -j ACCEPT")
        self.run_command("iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT")
        self.run_command("iptables -A INPUT -p icmp -j ACCEPT")
        self.run_command("iptables -A INPUT -p tcp --dport 50000:60000 -j ACCEPT")
#        self.run_command("iptables -t nat -A POSTROUTING -s 10.10.177.0/24 -j SNAT --to 10.10.188.232")
#        self.run_command("iptables -t nat -A PREROUTING -d 10.10.188.232 -p tcp --dport 80 -j DNAT --to 10.10.177.232:80")
        self.run_command("iptables -A INPUT -p tcp --syn --dport 80 -m connlimit --connlimit-above 100 -j REJECT")
        self.run_command("iptables -A INPUT -m limit --limit 3/hour --limit-burst 10 -j ACCEPT")
        self.run_command("iptables -A INPUT -p tcp --tcp-flags ALL FIN -j DROP")
        self.run_command("iptables -A INPUT -p tcp --tcp-flags ALL FIN,PSH,URG -j DROP")
        self.run_command("iptables -A INPUT -p tcp --tcp-flags ALL SYN,FIN,PSH,URG -j DROP")
        self.run_command("iptables -A INPUT -p tcp --tcp-flags SYN,RST SYN,RST -j DROP")
        self.run_command("iptables -A INPUT -j LOG --log-prefix 'Blocked Input:' --log-level 4")
        self.run_command("iptables -A INPUT -f -j DROP")
        self.run_command("iptables -A INPUT -m state --state INVALID -j DROP")
        self.run_command("iptables -A INPUT -p tcp -s 127.0.0.1 --dport 6379 -j ACCEPT")
        self.run_command("iptables -A INPUT -p tcp --tcp-flags ALL NONE -j DROP")
        self.run_command("iptables -A INPUT -p tcp --tcp-flags ALL ALL -j DROP")
        self.run_command("iptables -A INPUT -p tcp --tcp-flags ALL FIN -j DROP")
        self.run_command("iptables -A INPUT -p tcp --tcp-flags SYN,FIN SYN,FIN -j DROP")
        self.run_command("iptables -A INPUT -p tcp --tcp-flags FIN,URG,PSH FIN,URG,PSH -j DROP")
        self.run_command("iptables -A INPUT -p tcp --syn -m connlimit --connlimit-above 10 -j REJECT")
        self.run_command("iptables -A INPUT -p tcp --syn -m limit --limit 1/s --limit-burst 3 -j ACCEPT")
        self.run_command("iptables -A INPUT -p tcp --syn -j DROP")
        self.run_command("iptables -A INPUT -p tcp --tcp-flags ALL ACK -m limit --limit 5/s --limit-burst 10 -j ACCEPT")
        self.run_command("iptables -A INPUT -p tcp --tcp-flags ALL ACK -j DROP")
        self.run_command("iptables -A INPUT -p tcp --dport 80 -m connlimit --connlimit-above 20 -j DROP")
        self.run_command("iptables -A INPUT -p tcp --dport 80 -m conntrack --ctstate NEW -m limit --limit 10/s --limit-burst 20 -j ACCEPT")
        self.run_command("iptables -A INPUT -p tcp --dport 80 -j DROP")
        self.run_command("iptables -A INPUT -p tcp --syn -m limit --limit 1/s --limit-burst 4 -j ACCEPT")
        self.run_command("iptables -A INPUT -p tcp --syn -j DROP")
        self.run_command("iptables -A INPUT -p tcp --dport 80 -m string --string 'User-Agent: Slowloris' --algo bm -j DROP")
        self.run_command("iptables -A INPUT -p icmp -m limit --limit 1/s --limit-burst 5 -j ACCEPT")
        self.run_command("iptables -A INPUT -p icmp -j DROP")


        self.save_rules()


    firewallbuiltin = Firewallbuiltin()
    firewallbuiltin.setup_firewall()






-------------------------

class Firewall_builder:
    def __init__(self):
       self.init_firewall_builder()
       start_builder()
        # Start command with greeting and main menu

    async def start_builder(update: Update, context: ContextTypes.DEFAULT_TYPE):
        greeting_message = (
            "Welcome to the Firewall Bot! 🔥\n\n"
            "This bot allows you to manage firewall rules directly from Telegram.\n"
            "Please select an option below to get started."
        )
        buttons = [
            [InlineKeyboardButton("Add Rule", callback_data="menu_add_rule")],
            [InlineKeyboardButton("Help", callback_data="menu_help")],
            [InlineKeyboardButton("Exit", callback_data="menu_exit")]
        ]
        await send_message(update, greeting_message, InlineKeyboardMarkup(buttons))
        logger.info(f"User {update.effective_user.id} accessed the start menu.")
        user_states = {}

        # Helper function to clear user state
    def clear_user_state(user_id):
        if user_id in user_states:
            del user_states[user_id]

    # Helper function to send a message, handling both message and callback updates
    async def send_message(update: Update, text: str, reply_markup=None):
        if update.message:
            await update.message.reply_text(text, reply_markup=reply_markup)
        elif update.callback_query:
            await update.callback_query.message.reply_text(text, reply_markup=reply_markup)
            await update.callback_query.answer()

    # Handle start menu options
    async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user_id = update.effective_user.id

        if query.data == "menu_add_rule":
            await add_rule(update, context)
        elif query.data == "menu_help":
            await help_command(update, context)
        elif query.data == "menu_exit":
            await query.message.reply_text("Goodbye! 👋")
        await query.answer()

    # Start rule creation process: Step 1 - Select Direction
    async def add_rule(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user_states[user_id] = {"direction": None, "protocol": None, "source_ip": None, "source_port": None,
                                "destination_ip": None, "destination_port": None}
        logger.info(f"User {user_id} started rule creation.")

        buttons = [
            [InlineKeyboardButton("INPUT", callback_data="rule_direction_input")],
            [InlineKeyboardButton("OUTPUT", callback_data="rule_direction_output")],
            [InlineKeyboardButton("FORWARD", callback_data="rule_direction_forward")]
        ]
        await send_message(update, "Select the rule direction:", InlineKeyboardMarkup(buttons))

    # Handle rule direction selection: Step 2 - Select Protocol
    async def handle_rule_direction(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user_id = update.effective_user.id

        direction = query.data.split("_")[-1].upper()
        user_states[user_id]["direction"] = direction
        logger.info(f"User {user_id} selected direction: {direction}")

        buttons = [
            [InlineKeyboardButton("TCP", callback_data="rule_protocol_tcp")],
            [InlineKeyboardButton("UDP", callback_data="rule_protocol_udp")]
        ]
        await send_message(update, "Select the protocol for your rule:", InlineKeyboardMarkup(buttons))

    # Handle protocol selection: Step 3 - Input Source IP and Port
    async def handle_protocol_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user_id = update.effective_user.id

        protocol = query.data.split("_")[-1].upper()
        user_states[user_id]["protocol"] = protocol
        logger.info(f"User {user_id} selected protocol: {protocol}")

        # Prompt for Source IP with option to skip (Any)
        buttons = [[InlineKeyboardButton("Any", callback_data="source_ip_any")]]
        await send_message(update, "Please enter the Source IP address:", InlineKeyboardMarkup(buttons))

    # Handle source IP input, then prompt for source port
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

        # Prompt for Source Port with option to skip (Any)
        buttons = [[InlineKeyboardButton("Any", callback_data="source_port_any")]]
        await update.message.reply_text("Please enter the Source Port:", reply_markup=InlineKeyboardMarkup(buttons))

    # Handle source port input, then prompt for destination IP
    async def handle_source_port(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        source_port = update.message.text.strip()

        if source_port.lower() == "any":
            user_states[user_id]["source_port"] = "any"
        elif not source_port.isdigit() or not (1 <= int(source_port) <= 65535):
            await update.message.reply_text("Invalid port. Please enter a valid Source Port or select 'Any'.")
            return
        else:
            user_states[user_id]["source_port"] = source_port

        # Prompt for Destination IP with option to skip (Any)
        buttons = [[InlineKeyboardButton("Any", callback_data="destination_ip_any")]]
        await update.message.reply_text("Please enter the Destination IP address:", reply_markup=InlineKeyboardMarkup(buttons))

    # Handle destination IP input, then prompt for destination port
    async def handle_destination_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        destination_ip = update.message.text.strip()

        if destination_ip.lower() == "any":
            user_states[user_id]["destination_ip"] = "any"
        elif not re.match(r"^\d{1,3}(\.\d{1,3}){3}$", destination_ip):
            await update.message.reply_text("Invalid IP address. Please enter a valid Destination IP or select 'Any'.")
            return
        else:
            user_states[user_id]["destination_ip"] = destination_ip

        # Prompt for Destination Port with option to skip (Any)
        buttons = [[InlineKeyboardButton("Any", callback_data="destination_port_any")]]
        await update.message.reply_text("Please enter the Destination Port:", reply_markup=InlineKeyboardMarkup(buttons))

    # Handle destination port input, confirm rule creation
    async def handle_destination_port(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        destination_port = update.message.text.strip()

        if destination_port.lower() == "any":
            user_states[user_id]["destination_port"] = "any"
        elif not destination_port.isdigit() or not (1 <= int(destination_port) <= 65535):
            await update.message.reply_text("Invalid port. Please enter a valid Destination Port or select 'Any'.")
            return
        else:
            user_states[user_id]["destination_port"] = destination_port

        rule = user_states[user_id]
        confirmation_message = (
            f"Your rule:\nDirection: {rule['direction']}\nProtocol: {rule['protocol']}\n"
            f"Source IP: {rule['source_ip']} Port: {rule['source_port']}\n"
            f"Destination IP: {rule['destination_ip']} Port: {rule['destination_port']}\n\n"
            "Do you want to execute this rule?"
        )
        buttons = [
            [InlineKeyboardButton("Confirm", callback_data="confirm_rule")],
            [InlineKeyboardButton("Cancel", callback_data="cancel_rule")]
        ]
        await send_message(update, confirmation_message, InlineKeyboardMarkup(buttons))

    # Execute or cancel rule
    async def handle_rule_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user_id = update.effective_user.id
        rule = user_states.get(user_id)

        if query.data == "confirm_rule" and rule:
            try:
                # Execute rule based on saved parameters in user_states
                firewall.allow_port(rule["destination_port"], rule["protocol"].lower())  # Example for destination port
                result_message = "Rule executed successfully!"
                logger.info(f"User {user_id} executed rule: {rule}")
            except Exception as e:
                result_message = f"Error executing rule: {e}"
                logger.error(result_message)
            clear_user_state(user_id)
        else:
            result_message = "Rule creation canceled."
            clear_user_state(user_id)

        await query.message.reply_text(result_message)
        await query.answer()

    # Register commands and handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add_rule", add_rule))
    app.add_handler(CallbackQueryHandler(handle_menu, pattern="^menu_"))
    app.add_handler(CallbackQueryHandler(handle_rule_direction, pattern="^rule_direction_"))
    app.add_handler(CallbackQueryHandler(handle_protocol_selection, pattern="^rule_protocol_"))
    app.add_handler(CallbackQueryHandler(handle_rule_confirmation, pattern="^(confirm_rule|cancel_rule)$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_source_ip))

if __name__ == "__main__":
    firewall_builder()
