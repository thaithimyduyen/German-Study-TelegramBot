from app.telegrambot import StudyGermanTelegramBot

TOKEN_FILE = "./token.txt"


def main():
    with open(TOKEN_FILE, 'r') as f:
        token = f.readline()
    bot = StudyGermanTelegramBot(token=token)
    bot.run()


if __name__ == "__main__":
    main()
