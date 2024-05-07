import asyncio
import logging
import os
import re
from pathlib import Path
import psycopg2
from psycopg2 import Error
import paramiko
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, html, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message


def create_db_connection():
    logger.info("Creating database connection")
    host = os.getenv('DB_HOST')
    port = int(os.getenv('DB_PORT'))
    username = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_DATABASE')
    print(username, password)
    connection = psycopg2.connect(user=username,
                                  password=password,
                                  host=host,
                                  port=port,
                                  database=db_name)
    return connection



logger = logging.getLogger(__name__)
db_connection = create_db_connection()
TOKEN = os.getenv('TOKEN')
chat_id = os.getenv('CHAT_ID')

dp = Dispatcher()
search_router = Router()
password_router = Router()
linux_router = Router()
postgres_router = Router()


class EmailTextForm(StatesGroup):
    email = State()


class PhoneTextForm(StatesGroup):
    number = State()


class PasswordTextForm(StatesGroup):
    password = State()


async def connect_and_execute(cmd: str) -> str:
    logger.info("Got request to execute command: %s", cmd)
    host = os.getenv('RM_HOST')
    port = int(os.getenv('RM_PORT'))
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=host, username=username, password=password, port=port)
    except paramiko.SSHException as e:
        logger.error("Got exception while connecting via ssh: %s", e.__dict__)
        return "SSH error"
    else:
        logger.info("SSH connection established")

    stdin, stdout, stderr = client.exec_command(cmd)
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    return data


async def pretty_select(data: list):
    out = ""
    for item in data:
        out += " ".join(str(i) for i in item) + "\n"
    return out


async def find_only_repl_log(text: str) -> str:
    repl_log_lines = []
    for line in text.splitlines():
        if "replication" in line.lower():
            repl_log_lines.append(line)
    return "\n".join(repl_log_lines)


async def add_phone_if_not_exist(phone: str) -> str:
    data = await execute_sql(f"insert into phone(phone_number) values ('{phone}') on conflict do nothing",
                             commit=True)
    return data


async def add_email_if_not_exist(email: str) -> str:
    data = await execute_sql(f"insert into email(email) values ('{email}') on conflict do nothing",
                             commit=True)
    return data


async def execute_sql(sql: str, commit=False):
    try:
        cursor = db_connection.cursor()
        cursor.execute(sql)
        if commit:
            db_connection.commit()
            return "Успешно добавил в бд"
        data = cursor.fetchall()
        return data
    except Error as e:
        logger.error("Got exception while executing sql: %s. Exception: %s", sql, e)
        return "Ошибка выполнения SQL"
    finally:
        cursor.close()


@search_router.message(Command("find_email"))
async def find_email(message: Message, state: FSMContext):
    logger.info("Got email search request from %s", message.from_user.id)
    await message.answer("Введите текст для поиска email-адресов:")
    await state.set_state(EmailTextForm.email)


@search_router.message(EmailTextForm.email)
async def process_email_search(message: Message, state: FSMContext):
    text = message.text
    logger.info("Got email reply from %s. Text: %s", message.from_user.id, text)
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    if emails:
        logger.debug("Found emails: %s from user %s", emails, message.from_user.id)
        out = "Найденные email-адреса:\n"
        for i, email in enumerate(emails):
            write_message = await add_email_if_not_exist(email)
            out += f"{i + 1}. {email} | Статус записи: {write_message}\n"
        await message.answer(out)
    else:
        logger.debug("Not found emails from user %s", message.from_user.id)
        await message.answer("Email-адреса не найдены.")
    await state.clear()


@search_router.message(Command("find_phone_number"))
async def find_phone_number(message: Message, state: FSMContext):
    logger.info("Got phone search request from %s", message.from_user.id)
    await message.answer("Введите текст для поиска номеров телефонов:")
    await state.set_state(PhoneTextForm.number)


@search_router.message(PhoneTextForm.number)
async def process_phone_number_search(message: Message, state: FSMContext):
    text = message.text
    logger.info("Got phone reply from %s. Text: %s", message.from_user.id, text)
    phone_numbers = re.findall(r'(\+7|8)[\s\(\-]?(\d{3})[\s\)\-]?(\d{3})[\s\-\)]?(\d{2})[\s\-]?(\d{2})', text)
    if phone_numbers:
        logger.debug("Found numbers: %s from user %s", phone_numbers, message.from_user.id)
        out = "Найденные номера телефонов:\n"
        for i, phone in enumerate(phone_numbers):
            formatted_phone = "".join(phone).replace("+7", "8")
            write_message = await add_phone_if_not_exist(formatted_phone)
            out += f"{i + 1}. {formatted_phone} | Статус записи: {write_message}\n"
        await message.answer(out)
    else:
        logger.debug("Not found numbers from user %s", message.from_user.id)
        await message.answer("Номера телефонов не найдены.")
    await state.clear()


@password_router.message(Command("verify_password"))
async def verify_password(message: Message, state: FSMContext):
    await message.answer("Введите пароль для проверки:")
    await state.set_state(PasswordTextForm.password)


@password_router.message(PasswordTextForm.password)
async def process_password_verification(message: Message, state: FSMContext):
    password = message.text
    logger.info("Got password reply from %s. Text: %s", message.from_user.id, password)
    if re.match(r'(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()]).{8,}', password):
        logger.debug("Password hard from %s", message.from_user.id)
        await message.answer("Пароль сложный")
    else:
        logger.debug("Password easy from %s", message.from_user.id)
        await message.answer("Пароль простой")
    await state.clear()


@linux_router.message(Command("get_release"))
async def get_release(message: Message):
    out = await connect_and_execute("lsb_release -a")
    await message.answer(out)


@linux_router.message(Command("get_uname"))
async def get_uname(message: Message):
    out = await connect_and_execute("uname -a")
    await message.answer(out)


@linux_router.message(Command("get_uptime"))
async def get_uptime(message: Message):
    out = await connect_and_execute("uptime")
    await message.answer(out)


@linux_router.message(Command("get_df"))
async def get_df(message: Message):
    out = await connect_and_execute("df -h")
    await message.answer(out)


@linux_router.message(Command("get_free"))
async def get_free(message: Message):
    out = await connect_and_execute("free -h")
    await message.answer(out)


@linux_router.message(Command("get_mpstat"))
async def get_mpstat(message: Message):
    out = await connect_and_execute("mpstat")
    await message.answer(out)


@linux_router.message(Command("get_w"))
async def get_w(message: Message):
    out = await connect_and_execute("w | head -n 50")
    await message.answer(out)


@linux_router.message(Command("get_auths"))
async def get_auths(message: Message):
    out = await connect_and_execute("last -n 10")
    await message.answer(out)


@linux_router.message(Command("get_critical"))
async def get_critical(message: Message):
    out = await connect_and_execute("journalctl -p crit -n 5")
    await message.answer(out)


@linux_router.message(Command("get_ps"))
async def get_ps(message: Message):
    out = await connect_and_execute("ps | head -n 50")
    await message.answer(out)


@linux_router.message(Command("get_ss"))
async def get_ss(message: Message):
    out = await connect_and_execute("ss | head -n 20")
    await message.answer(out)


@linux_router.message(Command("get_apt_list"))
async def get_apt_list(message: Message, command: CommandObject):
    args = command.args
    if args is None:
        out = await connect_and_execute("dpkg -l | head -n 20")
        await message.answer(out)
    else:
        out = await connect_and_execute(f"apt-cache show {args.split()[0]} | head -n 10")
        await message.answer(out)


@linux_router.message(Command("get_services"))
async def get_services(message: Message):
    out = await connect_and_execute("systemctl list-units --state=running | head -n 20")
    await message.answer(out)


@postgres_router.message(Command("get_repl_logs"))
async def get_repl_logs(message: Message):
    data = await connect_and_execute("cat /var/log/postgres/postgres.log")
    #out = await find_only_repl_log(data)
    await message.answer("\n".join(data.split("\n")[-10:]))


@postgres_router.message(Command("get_emails"))
async def get_emails(message: Message):
    data = await execute_sql("select * from email;")
    out = await pretty_select(data)
    await message.answer(out)


@postgres_router.message(Command("get_phone_numbers"))
async def get_phone_numbers(message: Message):
    data = await execute_sql("select * from phone;")
    out = await pretty_select(data)
    await message.answer(out)


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN)
    dp.include_router(search_router)
    dp.include_router(password_router)
    dp.include_router(linux_router)
    dp.include_router(postgres_router)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == '__main__':
    # logging.basicConfig(filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    logger.info('Starting bot...')
    asyncio.run(main())
