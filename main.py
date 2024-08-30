import os
import telebot
import requests
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# Initialize the bot with your token
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# API endpoint
API_URL = "https://berita-indo-api-next.vercel.app/api/cnn-news/"


# Command handler for /start and /hello
@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    name = message.from_user.first_name
    button = InlineKeyboardButton(text="Lihat Berita Terbaru",
                                  callback_data="get_news:0")
    markup = InlineKeyboardMarkup([[button]])
    bot.send_message(
        message.chat.id,
        f"<b>Halo {name}</b>\n\nBot ini bisa menampilkan list berita terbaru dari CNN Indonesia\n\n<i>This bot is under development</i>\n<i>feedback @hsbrdnt</i>",
        reply_markup=markup,
        parse_mode="HTML")


# Function to send news with pagination
def send_news_paginated(chat_id, page):
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        news_data = response.json()
        articles = news_data.get('data', [])

        if articles:
            # Paginate the articles, showing 3 per page
            start = page * 3
            end = start + 3
            current_articles = articles[start:end]

            for news_item in current_articles:
                title = news_item.get('title')
                link = news_item.get('link')
                description = news_item.get('contentSnippet')
                image_url = news_item.get('image', {}).get('large', None)
                button = InlineKeyboardButton(text="Read More", url=link)
                markup = InlineKeyboardMarkup([[button]])
                news_message = f"**{title}**\n\n{description}"
                if image_url:
                    bot.send_photo(chat_id,
                                   image_url,
                                   caption=news_message,
                                   reply_markup=markup,
                                   parse_mode='Markdown')
                else:
                    bot.send_message(chat_id,
                                     news_message,
                                     reply_markup=markup,
                                     parse_mode='Markdown')

            # Create navigation buttons
            nav_buttons = []
            if page > 0:
                nav_buttons.append(
                    InlineKeyboardButton(text="Prev",
                                         callback_data=f"get_news:{page-1}"))
            if end < len(articles):
                nav_buttons.append(
                    InlineKeyboardButton(text="Next",
                                         callback_data=f"get_news:{page+1}"))
            if nav_buttons:
                nav_markup = InlineKeyboardMarkup([nav_buttons])
                bot.send_message(chat_id,
                                 "Lihat Berita lainnya:",
                                 reply_markup=nav_markup)

        else:
            bot.send_message(chat_id, "No news articles found.")

    except requests.exceptions.RequestException as e:
        bot.send_message(chat_id, f"Failed to fetch news. Error: {str(e)}")
    except ValueError:
        bot.send_message(chat_id, "Failed to parse JSON response.")


# Handle callback queries from inline buttons
@bot.callback_query_handler(func=lambda call: call.data.startswith("get_news"))
def callback_get_news(call):
    # Extract the page number from the callback data
    page = int(call.data.split(":")[1])
    send_news_paginated(call.message.chat.id, page)


bot.infinity_polling()
