import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from telebot import TeleBot, types


TOKEN = "6734052596:AAEHLzKAFFE-TwkRQIJgMcIKRCvAqFgNSjQ"
URL = "https://www.capitalethiopia.com"
bot = TeleBot(TOKEN)

user_state = {}  # Dictionary to keep track of user states

# Define states
STATE_CHOOSING_CATEGORY = 1


def get_news(category):
    response = requests.get(f"{URL}/category/{category}")
    soup = BeautifulSoup(response.text, "html.parser")
    news = soup.find_all(
        "div",
        class_="tdb_module_loop td_module_wrap td-animation-stack td-cpt-post",
    )
    print((len(news)))
    news_list = []
    for new in news:
        h3_tag = new.find("h3")
        title = h3_tag.text.strip() if h3_tag else "No Title"
        link = (
            h3_tag.find("a")["href"] if h3_tag and h3_tag.find("a") else None
        )  # Extracting href from <a> inside <h3>
        author = (
            new.find("span", class_="author").text
            if new.find("span", class_="author")
            else "Unknown Author"
        )
        image = (
            urljoin(URL, new.find("img")["src"]) if new.find("img") else None
        )
        video = (
            urljoin(URL, new.find("source")["src"])
            if new.find("source")
            else None
        )
        news_list.append(
            {
                "title": title,
                "author": author,
                "image": image,
                "video": video,
                "link": link,
            }
        )
    return news_list


def get_categories():
    return ["sports", "business-economy", "interview", "editorial", "society"]


@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        *[types.KeyboardButton(category) for category in get_categories()]
    )
    bot.send_message(message.chat.id, "Choose a category:", reply_markup=markup)
    bot.register_next_step_handler(message, process_category)
    user_state[message.chat.id] = STATE_CHOOSING_CATEGORY


@bot.message_handler(
    func=lambda message: user_state.get(message.chat.id)
    == STATE_CHOOSING_CATEGORY
)
def process_category(message):
    category = message.text
    if category not in get_categories():
        bot.send_message(
            message.chat.id, "Invalid category. Please choose a category again."
        )
        return

    news = get_news(category)
    for new in news:
        # Concatenating the link with the title and author
        message_text = f"{new['title']}\n{new['link']}"
        bot.send_message(message.chat.id, message_text)
        if new["image"]:
            try:
                bot.send_photo(message.chat.id, new["image"])
            except Exception as e:
                print(f"Error sending photo: {e}")
                # Optionally, send a message to the user that the image couldn't be loaded.
        if new["video"]:
            bot.send_video(message.chat.id, new["video"])


bot.polling()
