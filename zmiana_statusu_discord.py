import tkinter as tk
import json
import requests
import re
import threading
from cryptography.fernet import Fernet


class Application(tk.Frame):

    # zmienne
    autoryzacja = ''
    status_emoji_id = '800479551762989086'
    status_emoji_name = 'CheemsBurger1'
    dziala = False
    czas = None
    odstep = 0.0
    linika = 0
    tablica_z_tekstem = []

    def __init__(self, master=None):  # inicjalizacja
        super().__init__(master)
        self.master = master
        # enkrypcja klucza z config.json
        self.fernet = Fernet(
            key="GZWKEhHGNopxRdOHS4H4IyKhLQ8lwnyU7vRLrM3sebY=".encode())  # klucz do zaszyfrowania klucza autoryzacji w pliku config.js

        self.tablica_z_tekstem = self.czytaj_tekst_z_pliku()
        self.wczytaj_cofig()
        self.pack()
        self.wyswietl_elemeny()

    def wyswietl_elemeny(self):  # tworzenie widgetów
        self.wyswietl_zapisany_config()
       # guziczek zapisz
        self.zapisz_guzik = tk.Button(self)
        self.zapisz_guzik["text"] = "Zapisz"
        self.zapisz_guzik["command"] = self.akcja
        self.zapisz_guzik.grid(row=4)

        # guziczek
        self.rozpocznij_guzik = tk.Button(self)
        self.rozpocznij_guzik["text"] = "Rozpocznij"
        self.rozpocznij_guzik["command"] = self.rozpocznij
        self.rozpocznij_guzik.grid(row=6)

        # guziczek
        self.testowy = tk.Button(self)
        self.testowy["text"] = "Od nowa"
        self.testowy["command"] = self.test
        self.testowy.grid(row=5)
        # napisy
        self.napis_1 = tk.Label(self, text="Stan:").grid(row=7, column=0)
        self.napis_2 = tk.Label(self, text="Nie działa")
        self.napis_2.grid(row=7, column=1)
        self.napis_3 = tk.Label(
            self, text="Następny tekst do wyświetlenia:").grid(row=9, column=0)
        self.napis_4 = tk.Label(self, text=self.tablica_z_tekstem[self.linika])
        self.napis_4.grid(row=10, column=0)

        self.napis_5 = tk.Label(self, text="Odstęp:").grid(row=8, column=0)
        self.odstep_input = tk.Entry(self)
        self.odstep_input.insert(0, str(self.odstep))
        self.odstep_input.grid(row=8, column=1)

    def akcja(self):  # po kliknięcu guzika
        print("Wczytanie danych do configu i programu")
        self.aktualizuj_config(self.wprowadzanie_autoryzacja.get(
        ), float(self.odstep_input.get()))
        self.wczytaj_cofig()

    def czytaj_tekst_z_pliku(self):
        plik = open('tekst.txt', 'r', encoding='utf8')
        wynik = plik.readlines()
        plik.close()
        return wynik

    def rozpocznij(self):
        if (self.dziala):
            print("OFF")
            self.dziala = False
            self.napis_2['text'] = "Nie działa"
            self.napis_4['text'] = "-"

            if(self.czas != None):
                self.czas.cancel()
        else:
            print("ON")
            self.dziala = True
            self.napis_2['text'] = "Działa"
            zdanie = re.sub(
                r"\s+$", "", self.tablica_z_tekstem[self.linika], flags=re.UNICODE)
            self.napis_4['text'] = zdanie
            self.czas = threading.Thread(target=self.zaktualizuj_status, args=(
                self.tablica_z_tekstem[0], self.status_emoji_id, self.status_emoji_name,)).start()

    def test(self):
        self.linika = 0
        print("wyzerowano licznik")

    def obecny_status(self):
        self.napis_1 = "df"

    def wyswietl_zapisany_config(self):
        self.tekst_info_config = tk.Label(self)
        self.tekst_info_config['text'] = "Obecna konfiguracja:"
        self.tekst_info_config.grid(row=0)

        self.tekst_wprowadzanie_autoryzacja = tk.Label(self)
        self.tekst_wprowadzanie_autoryzacja['text'] = "authorization"
        self.tekst_wprowadzanie_autoryzacja.grid(row=1, column=0)
        self.wprowadzanie_autoryzacja = tk.Entry(self)
        self.wprowadzanie_autoryzacja.insert(0, self.autoryzacja)
        self.wprowadzanie_autoryzacja.grid(row=1, column=1)

    # aktualizacja statusu discorda
    def zaktualizuj_status(self, tekst, emoji_id, emoji_name):
        # print("wywołanie zaktualizuj_status()")
        glowa = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'authorization': self.autoryzacja,
            'content-type': 'application/json',
            'origin': 'https://discord.com',
            'referer': 'https://discord.com',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
        }
        dane = {
            'custom_status': {
                'text': tekst,
                'emoji_id': emoji_id,
                'emoji_name': emoji_name
            }
        }
        requests.patch('https://discord.com/api/v9/users/@me/settings',
                       headers=glowa, data=json.dumps(dane))
        if(self.dziala):
            if(len(self.tablica_z_tekstem) <= self.linika or self.linika == 0):
                self.linika = 0

            # print('Obecna inia Nr.{} - {}'.format(self.linika,self.tablica_z_tekstem[self.linika]))
            self.czas = threading.Timer(self.odstep, function=self.zaktualizuj_status, args=(
                self.tablica_z_tekstem[self.linika], self.status_emoji_id, self.status_emoji_name,)).start()

            zdanie = re.sub(
                r"\s+$", "", self.tablica_z_tekstem[self.linika], flags=re.UNICODE)
            self.napis_4['text'] = zdanie
            self.linika += 1

    def wczytaj_cofig(self):  # wczytanie configu
        plik = open('config.json')
        dane = json.load(plik)

        print("Wczytuję config do programu")

        zakodowane = dane['Dane'][0]['authorization'].encode()
        # self.autoryzacja = self.fernet.decrypt(zakodowane).decode()

        try:
            self.autoryzacja = self.fernet.decrypt(zakodowane).decode()
        except Exception as e:
            print(e)
            self.autoryzacja = "Błąd wczytywania klucza"

        self.odstep = dane['Dane'][0]['odstep']
        print("Wczytano")
        print(self.autoryzacja)
        print(self.odstep)
        plik.close()

    def aktualizuj_config(self, autoryzacja, odstep):
        autoryzacja_zakodowana = self.fernet.encrypt(autoryzacja.encode())
        siur = {}
        siur['Dane'] = []
        siur['Dane'].append({
            'odstep': odstep,
            'authorization': autoryzacja_zakodowana.decode()
        })
        with open('config.json', 'w') as outfile:
            json.dump(siur, outfile)

    def przy_zamknieciu(self):
        print("Closing")
        self.dziala = False


root = tk.Tk()
app = Application(master=root)
app.master.title("Zmiana statusu")
app.master.minsize(600, 300)
app.mainloop()
root.wm_protocol("WM_DELETE_WINDOW", app.przy_zamknieciu())
