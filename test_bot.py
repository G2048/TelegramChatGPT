from os import getenv
import asyncio
import logging
from dotenv import load_dotenv
import telegram
from pprint import pprint

load_dotenv()
TOKEN = getenv('TELEGRAM_TOKEN')

FORMAT = '%(asctime)s::%(levelname)s::%(message)s'
logging.basicConfig(filename='telegram.log', format=FORMAT, level=logging.DEBUG)


async def main():
    bot = telegram.Bot(TOKEN)

    async with bot:
        get_me_info = await bot.get_me()
        get_info = (await bot.get_updates())[0]
        message = get_info["message"]
        userinform = message['from_user']
        chat_id = get_info.effective_chat.id
        update_id = get_info["update_id"]

        # pprint(f'{message}', depth=4, indent=4, width=4)
        print('\n')
        pprint(f'{get_info}', depth=4, indent=4, width=4)
        pprint(f'{dir(get_info.message)}', depth=4, indent=4, width=4)

        logging.debug('id: %s' % chat_id)
        # await bot.send_message(text='Hi!', chat_id=chat_id)
        # await bot.send_venue(chat_id=chat_id)


if __name__ == '__main__':
    asyncio.run(main())
