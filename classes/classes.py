from bs4 import BeautifulSoup
import requests
import asyncio
import sqlite3

jager_email = "hunterbot.jager@bk.ru"
jager_password = "Jagerthebest01"
url_tracker = "https://r6.tracker.network/profile/pc/"
r6_data = []


def to_digital(word):
    res = ""
    for symbol in word:
        if '0' <= symbol <= '9':
            res += symbol
    return int(res)

rank_icons = {
            "-": "https://i.imgur.com/sB11BIz.png",  # unranked
            "COOPER I": "https://i.imgur.com/0J0jSWB.jpg",  # copper 1
            "COOPER II": "https://i.imgur.com/eI11lah.jpg",  # copper 2
            "COOPER III": "https://i.imgur.com/6CxJoMn.jpg",  # copper 3
            "COOPER IV": "https://i.imgur.com/ehILQ3i.jpg",  # copper 4
            "COOPER V": "https://i.imgur.com/B8NCTyX.png",  # copper 5
            "BRONZE I": "https://i.imgur.com/hmPhPBj.jpg",  # bronze 1
            "BRONZE II": "https://i.imgur.com/9AORiNm.jpg",  # bronze 2
            "BRONZE III": "https://i.imgur.com/QD5LYD7.jpg",  # bronze 3
            "BRONZE IV": "https://i.imgur.com/42AC7RD.jpg",  # bronze 4
            "BRONZE V": "https://i.imgur.com/TIWCRyO.png",   # bronze 5
            "SILVER I": "https://i.imgur.com/KmFpkNc.jpg",  # silver 1
            "SILVER II": "https://i.imgur.com/EswGcx1.jpg",  # silver 2
            "SILVER III": "https://i.imgur.com/m8GToyF.jpg",  # silver 3
            "SILVER IV": "https://i.imgur.com/D36ZfuR.jpg",  # silver 4
            "SILVER V": "https://i.imgur.com/PY2p17k.png",  # silver 5
            "GOLD I": "https://i.imgur.com/ffDmiPk.jpg",  # gold 1
            "GOLD II": "https://i.imgur.com/ELbGMc7.jpg",  # gold 2
            "GOLD III": "https://i.imgur.com/B0s1o1h.jpg",  # gold 3,
            "GOLD IV": "https://i.imgur.com/6Qg6aaH.jpg",  # gold 4
            "PLAT I": "https://i.imgur.com/qDYwmah.png",  # plat 1
            "PLAT II": "https://i.imgur.com/CYMO3Er.png",  # plat 2
            "PLAT III": "https://i.imgur.com/tmcWQ6I.png",  # plat 3
            "DIAMOND": "https://i.imgur.com/37tSxXm.png",  # diamond
            "CHAMPION": "https://i.imgur.com/VlnwLGk.png",  # champion
}

class PlayerR6:
    def __init__(self, nickname, member_id = -1):
        """
        Класс игрока R6.
        Имеет статистику: убийства, смерти, победы, проигрыши, время игры, ММР.
        Дополнительная информация: ID участника сервера, URL аватара аккаунта UPlay.

        При инициализации подгружаются все данные.
        """
        self.nickname = nickname
        self.member_id = member_id
        self.parser_data = ["PVPKills", "PVPDeaths", "PVPMatchesWon", "PVPMatchesLost", "PVPTimePlayed"]

        # Основная статистика
        self.kills, self.kills, self.wins, self.loses, self.time_player = None, None, None, None, None
        self.mmr, self.rank_name, self.rank_url = None, None, None
        self.icon_url  = None

        # Предыдущая статистика
        self.last_kills, self.last_kills, self.last_wins, \
        self.last_loses, self.last_mmr = None, None, None, None, None

        self.load_stats()

    def load_stats(self):
        """
        Загружает основную статистику
        """
        url = url_tracker + self.nickname
        full_page = requests.get(url)
        soup = BeautifulSoup(full_page.content, 'html.parser')
        stats = []
        for item in self.parser_data:
            stats.append(to_digital(soup.find('div', {'data-stat': item}).contents[0]))
        self.icon_url = soup.find('div', {'class': 'trn-profile-header__avatar'}).find('img').attrs['src']
        trn_defstat = soup.find_all('div', {'class': 'trn-defstat'})
        for item in trn_defstat:
            div_text = item.find('div', {'class': 'trn-defstat__name'})
            if div_text.next_element == "MMR":
                stats.append(to_digital(item.find('div', {'class': 'trn-defstat__value'}).contents[0]))
            if div_text.next_element == "Rank":
                self.rank_name = item.find('div', {'class': 'trn-defstat__value'}).contents[0]

        self.rank_url = rank_icons[self.rank_name]
        self.kills, self.deaths, self.wins, self.loses, \
        self.time_played, self.mmr = (item for item in stats)


    def update_daily_stats(self):
        self.load_stats()
        self.last_kills = self.kills
        self.last_deaths = self.deaths
        self.last_wins = self.wins
        self.last_loses = self.loses
        self.last_mmr = self.mmr

    def get_data(self):
        data = (self.member_id, self.nickname, self.kills, self.deaths, self.wins, self.loses, self.mmr)
        return data

class DataBaseR6:
    def __init__(self):
        self.conn = sqlite3.connect("r6_players.db")
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS R6_players 
        (discord_id INT PRIMARY KEY,
        nickname TEXT, 
        kills INT, 
        deaths INT, 
        wins INT,
        loses INT,
        mmr INT
        );""")

    def add_players(self, player_data):
        self.cursor.execute("INSERT INTO R6_players VALUES (?,?,?,?,?,?,?);", player_data)
        self.conn.commit()

# def main():
#     player = PlayerR6("KriptYashka", 280414805439807489)
#     db = DataBaseR6()
#     db.add_players(player.get_data())
#     print(player.mmr)
#
# main()