from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.label import Label
from kivy.lang import Builder
import requests
import webbrowser
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivy.clock import Clock
from kivy.garden.graph import Graph, MeshLinePlot

Builder.load_file('styles.kv')

class ScrButton(Button):
    pass

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')

        # Create and add buttons with custom positions
        button1 = Button(text='Bitcoin Price', size_hint=(None, None), size=(150, 50), pos=(50, 500))
        button2 = Button(text='Ethereum Price', size_hint=(None, None), size=(150, 50), pos=(50, 250))
        button3 = Button(text='LTC Price', size_hint=(None, None), size=(150, 50), pos=(50, 150))
        site_button = Button(text='Open Website', size_hint=(None, None), size=(150, 50), pos=(50, 0))

        button1.bind(on_release=self.update_bitcoin_price)
        button2.bind(on_release=self.update_ethereum_price)
        button3.bind(on_release=self.update_ltc_price)
        site_button.bind(on_release=self.open_website)

        layout.add_widget(button1)
        layout.add_widget(button2)
        layout.add_widget(button3)
        layout.add_widget(site_button)

        self.add_widget(layout)

        self.price_label = Label(
    halign='center',
    valign='middle',
    color=(2, 2, 2, 1),  # Зеленый цвет текста
    font_size='32sp',  # Размер шрифта (24sp)
)
        self.add_widget(self.price_label)

        self.update_in_progress = False  # Флаг для индикатора обновления

        Clock.schedule_interval(self.update_prices_periodic, 60)  # Обновление каждые 5 минут

    def show_no_internet_dialog(self):
        dialog = MDDialog(
            title="Ошибка подключения",
            text="Нет подключения к Интернету. Пожалуйста, проверьте свою сеть.",
            buttons=[
                MDRaisedButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()

    def update_bitcoin_price(self, *args):
        if not self.update_in_progress and self.check_internet_connection():
            self.update_in_progress = True  # Устанавливаем флаг обновления
            bitcoin_chart_screen = self.manager.get_screen('bitcoin_chart')
            btc_price = bitcoin_chart_screen.fetch_crypto_price()
            self.price_label.text = f"Bitcoin Price: ${btc_price}"
            self.update_in_progress = False  # Сбрасываем флаг после обновления
        elif not self.check_internet_connection():
            self.show_no_internet_dialog()

    def update_ethereum_price(self, *args):
        if not self.update_in_progress and self.check_internet_connection():
            self.update_in_progress = True  # Устанавливаем флаг обновления
            ethereum_chart_screen = self.manager.get_screen('ethereum_chart')
            eth_price = ethereum_chart_screen.fetch_crypto_price()
            self.price_label.text = f"Ethereum Price: ${eth_price}"
            self.update_in_progress = False  # Сбрасываем флаг после обновления
        elif not self.check_internet_connection():
            self.show_no_internet_dialog()

    def update_ltc_price(self, *args):
        if not self.update_in_progress and self.check_internet_connection():
            self.update_in_progress = True
            ltc_chart_screen = self.manager.get_screen('ltc_chart')
            ltc_price = ltc_chart_screen.fetch_crypto_price()
            self.price_label.text = f"LTC Price: ${ltc_price}"
            self.update_in_progress = False
        elif not self.check_internet_connection():
            self.show_no_internet_dialog()

    def open_website(self, instance):
        webbrowser.open("https://www.youtube.com/watch?v=xm3YgoEiEDc")

    def check_internet_connection(self):
        try:
            response = requests.get("http://www.google.com", timeout=5)
            return True
        except requests.ConnectionError:
            return False

    def update_prices_periodic(self, dt):
        # Метод для периодического обновления цен
        self.update_bitcoin_price()
        self.update_ethereum_price()
        self.update_ltc_price()

class Screen2(Screen):
    def __init__(self, **kwargs):
        super(Screen2, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Button(text='Back', on_release=self.switch_to_main))
        self.add_widget(layout)

    def switch_to_main(self, *args):
        self.manager.current = 'main'

class BackScreen(Screen):
    def __init__(self, **kwargs):
        super(BackScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(ScrButton(text='Back', on_release=self.switch_to_main))
        self.add_widget(layout)

    def switch_to_main(self, *args):
        self.manager.current = 'main'

class CryptoPriceChart(Screen):
    def __init__(self, symbol, **kwargs):
        super(CryptoPriceChart, self).__init__(**kwargs)

        self.symbol = symbol
        self.crypto_data = [(0, 0)]  # Данные для графика криптовалют

        graph = Graph(xlabel='Time', ylabel='Price', x_ticks_major=5, y_ticks_major=100, x_grid_label=True, y_grid_label=True, padding=5)
        plot = MeshLinePlot(color=[0, 1, 0, 1])
        plot.points = self.crypto_data
        graph.add_plot(plot)

        self.add_widget(graph)

    def fetch_crypto_price(self):
        try:
            binance_api_url = "https://api.binance.com/api/v3/ticker/price"
            params = {
                "symbol": self.symbol,
            }
            response = requests.get(binance_api_url, params=params)
            data = response.json()
            crypto_price = data["price"]
            
            # Обновляем данные графика
            graph = self.children[0]  # Получаем виджет графика
            plot = graph.plots[0]
            self.crypto_data.append((self.crypto_data[-1][0] + 1, float(crypto_price)))  # Добавляем новую точку
            plot.points = self.crypto_data[-100:]  # Ограничиваем количество отображаемых точек
            
            return crypto_price
        except Exception as e:
            print(f"Error fetching {self.symbol} price: {str(e)}")
            return "Error"

class MyApp(MDApp):
    def build(self):
        screen_manager = ScreenManager()

        main_screen = MainScreen(name='main')
        screen_manager.add_widget(main_screen)

        bitcoin_chart = CryptoPriceChart(name='bitcoin_chart', symbol='BTCUSDT')
        screen_manager.add_widget(bitcoin_chart)

        ethereum_chart = CryptoPriceChart(name='ethereum_chart', symbol='ETHUSDT')
        screen_manager.add_widget(ethereum_chart)

        ltc_chart = CryptoPriceChart(name='ltc_chart', symbol='LTCUSDT')
        screen_manager.add_widget(ltc_chart)

        return screen_manager

if __name__ == '__main__':
    MyApp().run()