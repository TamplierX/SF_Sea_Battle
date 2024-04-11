from random import randint
from random import choice as ch
from time import sleep


#  -----------------------------------------------------------------------------------------------
#  GameException родительский класс для всех пользовательских исключений, где Exception это внутренний класс
#  исключений Python(отлавливаем все не предвиденные исключения).
class GameException(Exception):
    pass


#  Пользовательский класс исключений, если игрок вводит координаты вне поля боя.
class PointOutFieldException(GameException):
    def __str__(self):
        return ("""Адмирал, разведка докладывает что в районе куда вы хотите нанести удар, не может быть 
вражеских кораблей, совершите выстрел пользуясь данными радара!""")


#  Пользовательский класс исключений, если игрок вводит координаты клетки куда уже производился выстрел.
class PointUsedException(GameException):
    def __str__(self):
        return """Адмирал, вы уже стреляли в точку с этими координатами! Ваш приказ не был выполнен!
Попробуйте ещё раз."""


#  Класс исключений когда не правильно размещаются корабли на поле боя.
class WrongShipException(GameException):
    pass
#  -----------------------------------------------------------------------------------------------


#  -----------------------------------------------------------------------------------------------
#  Класс Точка с двумя параметрами х и у(которые передаются в конструкторе).
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    #  Метод для сравнения двух точек.
    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y

    #  Метод который отвечает за отображения точек (что бы у нас не печаталось
    # <__main__.Point object at 0x0000015033DB9400> а печаталась точка пример (1, 1).
    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"
#  -----------------------------------------------------------------------------------------------


#  -----------------------------------------------------------------------------------------------
#  Класс корабля с параметрами в конструкторе (rotation - в какую сторону будет смотреть корма корабля(0 - вверх,
#  1 - вниз, 2 - влево, 3- вправо)), length - длинна корабля, start_point - это нос корабля(туда передаются координаты
#  точки например Point(1, 1)).
class Ship:
    def __init__(self, start_pos, length, rotation):
        self.start_pos = start_pos
        self.length = length
        self.rotation = rotation
        self.hit_points = length

    #  Метод создает список ship_points в котором будут точки корабля, используем декоратор property
    #  потому что этот метод задает свойства корабля.
    @property
    def points(self) -> list:
        ship_points = []
        # Тут мы проходимся в цикле по значениям от 0 до длинны корабля.
        for i in range(self.length):
            #  Разделяем начальную точку на x и y, что бы была возможность продлевать корабль вертикально
            #  или горизонтально.
            coordinate_x = self.start_pos.x
            coordinate_y = self.start_pos.y

            if self.rotation == 0:
                coordinate_x -= i
            elif self.rotation == 1:
                coordinate_x += i
            elif self.rotation == 2:
                coordinate_y -= i
            elif self.rotation == 3:
                coordinate_y += i
            ship_points.append(Point(coordinate_x, coordinate_y))
        #  В конце возвращает объект корабля в виде списка со всеми его точками.
        return ship_points

    #  Метод, который проверяет попадание по кораблю.
    def falling_into_ship(self, shot) -> bool:
        return shot in self.points
#  -----------------------------------------------------------------------------------------------


#  -----------------------------------------------------------------------------------------------
#  Класс для создания игрового поля (hid_ships отвечает за то будут ли отображаться корабли на этом поле,
#  size - это размер поля).
class BattleField:
    def __init__(self, hid_ships=False, size=6):
        self.size = size
        self.hid_ships = hid_ships
        #  Генератор для создания игровой сетки.
        self.field = [["O"] * size for _ in range(size)]
        #  used_points - будет хранить в себе "занятые" точки.
        self.used_points = []
        #  ships - список всех кораблей.
        self.ships = []
        # count - количество живых кораблей.
        self.count = 7

    #  Метод оформляет визуальное отображения поля в функции print.
    def __str__(self):
        design = ""
        design += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, j in enumerate(self.field):
            design += f"\n{i + 1} | " + " | ".join(j) + " |"

        #  Если hid_ships = True, все клетки кораблей "■" будут заменены на пустые "O".
        if self.hid_ships:
            design = design.replace("■", "O")
        return design

    #  Метод проверяющий находится ли точка за пределами игрового поля.
    #  Он нужен, что б мы могли отлавливать исключения.
    def out(self, point) -> bool:
        return not ((0 <= point.x < self.size) and (0 <= point.y < self.size))

    #  Метод для добавления корабля на поле боя.
    def add_ship(self, ship):
        # В цикле проверяем: не выходит ли каждая точка корабля за границы и не занята ли точка другим кораблем или
        # точками окружности корабля.
        for point in ship.points:
            if self.out(point) or point in self.used_points:
                raise WrongShipException()
        # Цикл для визуального отображения каждой точки корабля и заполнение занятых кораблем координат.
        for point in ship.points:
            self.field[point.x][point.y] = "■"
            self.used_points.append(point)

        # Добавляем корабль в список кораблей.
        self.ships.append(ship)
        # Создает точки окружности корабля.
        self.around_ship(ship)

    #  Метод around_ship будет добавлять все точки вокруг корабля в список занятых точек, это поможет нам правильно
    #  поставить корабли на игровое поле и для удобства буде закрашивать все точки вокруг корабля при его уничтожении.
    def around_ship(self, ship, hid_points=False):
        #  Список всех возможных точек вокруг конкретной точки.
        around_points = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        #  Цикл пробегается по всем точкам корабля.
        for point in ship.points:
            #  Вложенный цикл пробегается по всем возможным точкам вокруг каждой точки корабля.
            for dx, dy in around_points:
                coordinate = Point(point.x + dx, point.y + dy)
                #  Проверяем не выходит ли точка за границу поля и не является ли точка уже использованной.
                if not (self.out(coordinate)) and coordinate not in self.used_points:
                    #  Если корабль уничтожен все точки вокруг корабля закрашиваются знаком промаха "T".
                    if hid_points:
                        self.field[coordinate.x][coordinate.y] = "T"
                    #  После всех проверок точки вокруг корабля добавляются в список "занятых" точек.
                    self.used_points.append(coordinate)

    #  Метод проверки выстрела на попадание/промах.
    def shot(self, point) -> bool:
        #  Проверяем что б координаты выстрела были в границе поля.
        if self.out(point):
            #  Исключение будет работать только для реального игрока, бот мимо поля стрелять не сможет.
            raise PointOutFieldException()
        #  Проверяем что б координаты выстрела были в "свободной" точке.
        if point in self.used_points:
            #  Исключение будет работать только для реального игрока, бот не сможет стрелять в "занятые" точки.
            raise PointUsedException()
        #  Когда проходит все проверки - добавляем точку в список "использованных" точек.
        self.used_points.append(point)
        #  Проходимся по списку кораблей и проверяем является ли точка выстрела точкой корабля.
        for ship in self.ships:
            if ship.falling_into_ship(point):
                #  Если да - уменьшаем количество жизней корабля.
                ship.hit_points -= 1
                #  Ставим "Х" в точке попадания.
                self.field[point.x][point.y] = "X"
                #  Если у корабля не осталось жизней - уменьшаем количество живых кораблей на 1 и отображаем точки
                #  вокруг корабля меняя hid_points на True.
                if ship.hit_points == 0:
                    self.count -= 1
                    self.around_ship(ship, hid_points=True)
                    print("Корабль уничтожен!")
                    #  возвращаем True что бы получить дополнительный ход.
                    return True
                else:
                    #  Если корабль ранен - получаем дополнительный ход.
                    print("Корабль ранен!")
                    return True
        #  Если корабля там нет указываем промах и ход переходит к противнику.
        self.field[point.x][point.y] = "T"
        print("Промах!")
        return False

    #  Метод нужен, что б в начале игры очистить список занятых точек.
    def preparation(self):
        self.used_points = []

    #  Проверяем условие для победи одного из игроков
    def victory(self):
        return self.count == 0
#  -----------------------------------------------------------------------------------------------


#  -----------------------------------------------------------------------------------------------
#  Класс игроков. В качестве аргументов передаются свое поле и поле с кораблями противника.
class Player:
    def __init__(self, field, radar):
        self.field = field
        self.radar = radar

    #  Определяем метод для наследования в дочерние классы.
    def request(self):
        pass

    #  Определяем метод для наследования в дочерние классы.
    def ship_rotation(self):
        pass

    #  Определяем метод для наследования в дочерние классы.
    def choice_auto_field(self):
        pass

    #  В этом методе просим игрока/бота сделать свой ход.
    def make_move(self) -> bool:
        # Делаем через бесконечный цикл, что бы в случае получения исключения ход не прерывался и заканчивался
        # результатом выстрела.
        while True:
            #  Используем try-except потому что здесь есть большая вероятность получить исключение на стадии
            #  ввода координат.
            try:
                #  Здесь мы просим ввести координаты выстрела.
                make_shot = self.request()
                #  Выполняем выстрел.
                result = self.radar.shot(make_shot)
                #  И возвращаем результат выстрела.
                return result
            #  Если получаем исключение - печатаем его.
            except GameException as exc:
                print(exc)


#  Класс бота.
class Bot(Player):
    #  В этом методе бот передает координаты своего выстрела.
    def request(self):
        #  Генерируем список со всеми возможными точками.
        points_list = [Point(i, j) for i in range(self.field.size) for j in range(self.field.size)]
        #  Перебираем список использованных точек и удаляем их из общего списка.
        for i in self.radar.used_points:
            if i in points_list:
                points_list.remove(i)
        #  Из общего списка случайно выбирается один элемент.
        shot_point = ch(points_list)
        print(f"Враг выстрелил в точку: {shot_point.x + 1}, {shot_point.y + 1}")
        return shot_point


#  Класс пользователя
class User(Player):
    #  Просим игрока ввести координаты
    def request(self):
        #  Делаем через бесконечный цикл, что бы в случае ошибки ход не прерывался.
        while True:
            point_x = input("Введите координату х: ")
            point_y = input("Введите координату y: ")
            #  Если введенные данные не являются числами - начинаем цикл заново
            if not (point_x.isdigit()) or not (point_y.isdigit()):
                print("Введите корректные координаты!")
                continue
            x, y = int(point_x), int(point_y)
            #  Возвращаем координаты точки с -1, потому что индексация поля начинается с нуля, а визуально с единицы.
            return Point(x - 1, y - 1)

    #  Просим игрока ввести направление корабля, метод возвращает число от 0 до 3
    def ship_rotation(self):
        #  Делаем через бесконечный цикл, что бы в случае ошибки программа не закрывалась.
        while True:
            pos = input("Введите направление корабля: ")
            if not (pos.isdigit()):
                print("Введены некорректные данные! ")
                continue
            ship_rotation = int(pos)
            if (ship_rotation < 0) and (ship_rotation > 3):
                print("Введены некорректные данные!")
                continue
            return ship_rotation

#  Даем игроку выбор: расставить корабли самому или сделать это автоматически. Возвращаем число 1 или 2.
    def choice_auto_field(self):
        #  Делаем через бесконечный цикл, что бы в случае ошибки программа не закрывалась.
        while True:
            user_auto_field = input('''Если вы желаете сами расставить корабли - введите 1,
а если хотите что бы флот сделал это сам - введите 2:\n''')
            if not (user_auto_field.isdigit()):
                print('Вы ввели некорректные данные')
                continue
            else:
                user_auto_field = int(user_auto_field)
            if user_auto_field > 2 or user_auto_field < 1:
                print('Вы ввели некорректные данные')
                continue
            return user_auto_field
#  -----------------------------------------------------------------------------------------------


#  -----------------------------------------------------------------------------------------------
#  Класс Игра, где из всех созданных ранее классов, мы будем создавать объекты и настраивать логику взаимодействия.
class Game:
    def __init__(self, size=6):
        self.size = size
        #  Список с длиной кораблей для расстановки на поле боя.
        self.ship_lens = [3, 2, 2, 1, 1, 1, 1]
        # Создавать игровые поля будем в процессе игры
        self.bot_field = None
        self.user_field = None
        self.user = User(self.user_field, self.bot_field)
        self.bot = Bot(self.bot_field, self.user_field)

    #  Метод "Приветствие" с игроком
    @staticmethod
    def greetings() -> None:
        print('-' * 80)
        sleep(1)
        print('Приветствую вас в игре "Морской бой"')
        print('-' * 80)
        sleep(1)
        print('''    Вы получили внеочередное звание Адмирала!
Также, вы получаете под личное командование собственный флот:
- Крейсер (трех палубный корабль) х 1;
- Эсминец (двух палубный корабль) х 2;
- Катер (Однопалубный корабль) х 4.''')
        print('-' * 80)
        sleep(1)
        print('''    Сейчас вы отправляетесь на очередное боевое задание.
Вам предстоит встретится с противником, у которого флот аналогичен вашему.
Ваша задача: потопить весь вражеский флот, сохранив хотя бы один свой корабль.
Все что вам нужно делать, это указывать координаты выстрела.''')
        print('-' * 80)
        sleep(1)
        print('Формат ввода: x и y , где х - номер строки, а у - номер столбца.')
        print('-' * 80)
        sleep(1)

    #  Печатаем поле игрока и противника(радар).
    def print_fields(self):
        print('-' * 80)
        print("Ваша карта:")
        print(self.user.field)
        print('-' * 80)
        print("Ваш радар:")
        print(self.bot.field)

    #  Метод который гарантированно создает поле боя.
    def creating_field(self, choice=2):
        field = choice
        #  Если игрок выбрал "самому создать поле" запустится метод ручной расстановки кораблей.
        while field == 1:
                field = self.input_creation()
        #  Если игрок выбрал "автоматически создать поле" запустится метод автоматической расстановки кораблей.
        #  Для бота этот метод идет по умолчанию.
        while field == 2:
                field = self.random_creation()

        return field

    #  Метод расстановки кораблей вручную.
    def input_creation(self):
        #  Создаем поле.
        field = BattleField(size=self.size)
        #  Для каждой длинны корабля, в бесконечном цикле будем пытаться его поставить.
        for ship_len in self.ship_lens:
            while True:
                print(field)
                #  Если нет возможности поставить корабль на поле, даем игроку выбор: попытаться снова или
                #  перейти на автоматический режим.
                if len(field.used_points) == 36:
                    print('-' * 80)
                    print('''Адмирал, у вас не осталось свободных координат что бы разместить корабль.
Прийдется все начать с начала.''')
                    print('-' * 80)
                    user_choice = self.user.choice_auto_field()
                    if user_choice == 1:
                        return 1
                    else:
                        return 2

                print('Введите начальную координату и направление(0 - вверх, 1 - вниз, 2 - влево, 3- вправо)')
                print(f'Длина корабля: {ship_len} палубы')
                #  Просим игрока ввести координаты начала корабля.
                ship_point = self.user.request()
                #  Если корабль длиннее одной палубы, просим игрока указать направление корабля.
                if ship_len > 1:
                    pos = self.user.ship_rotation()
                else:
                    pos = 0
                #  Создаем экземпляр корабля.
                ship = Ship(ship_point, ship_len, pos)
                # Пробуем поставить корабли, если все получается - цикл завершается.
                # Если получаем ошибку - переходим на новую итерацию цикла.
                try:
                    field.add_ship(ship)
                    break
                except WrongShipException:
                    print('-' * 80)
                    print("""Адмирал, капитан корабля сообщает что не может выплыть в заданную позицию и разместить 
корабль в заданном направлении, пожалуйста, обновите приказ с корректными данными""")
        #  Очищаем список занятых точек.
        field.preparation()
        return field

    #  Метод, который пытается случайно расставить корабли на поле боя.
    def random_creation(self):
        #  Создаем поле
        field = BattleField(size=self.size)
        # Счетчик итераций цикла.
        try_ = 0
        #  Для каждой длинны корабля, в бесконечном цикле будем пытаться его поставить.
        for ship_len in self.ship_lens:
            while True:
                try_ += 1
                #  Если счетчик перевалил за 500 итераций - возвращаем None и начинаем генерировать поле заново.
                if try_ > 500:
                    return 2
                ship = Ship(Point(randint(0, self.size), randint(0, self.size)), ship_len, randint(0, 1))
                # Пробуем поставить корабли, если все получается - цикл завершается.
                # Если получаем ошибку - переходим на новую итерацию цикла.
                try:
                    field.add_ship(ship)
                    break
                except WrongShipException:
                    pass
        #  Очищаем список занятых точек.
        field.preparation()
        return field

    #  Создаем поле боя для каждого игрока.
    def creating_players_fields(self):
        self.bot_field = self.creating_field()
        choice = self.user.choice_auto_field()
        self.user_field = self.creating_field(choice)
        self.user = User(self.user_field, self.bot_field)
        self.bot = Bot(self.bot_field, self.user_field)
        #  Скрываем отображение кораблей на доске противника.
        self.bot_field.hid_ships = True

#  Метод игровой логики
    def logic(self):
        #  Счетчик для определения очередности хода игрока/бота. Случайно определяем кто будет ходить первым.
        next_move = randint(0, 1)
        while True:
            self.print_fields()
            #  Если номер хода четный - ходит игрок, нечетный - бот.
            if next_move % 2 == 0:
                print('-' * 80)
                print("Адмирал, ваш ход!")
                #  result возвращает нам True или False, это значит либо дальше ходит противник, либо мы получаем
                #  дополнительный ход.
                result = self.user.make_move()
            else:
                print('-' * 80)
                print("Ход противника!")
                sleep(1)
                result = self.bot.make_move()
            #  Если result вернул True - мы получаем дополнительный ход.
            if result:
                next_move -= 1
            #  Если потоплены все корабли на доске Бота - игрок победил.
            if self.bot.field.victory():
                self.print_fields()
                print('-' * 80)
                print("""Поздравляем с победой, Адмирал!
Вы доказали, что достойны управлять флотом!""")
                break
            #  Если потоплены все корабли на доске игрока - Бот победил.
            if self.user.field.victory():
                self.print_fields()
                print('-' * 80)
                print('Ваш флот уничтожен! "Press F to pay respects((("')
                break
            #  Увеличиваем значение хода на 1, что бы ходил соперник.
            next_move += 1

    #  Метод старт игры запускает приветствие, создаем поля игрокам запускаем логику игры.
    def start(self):
        self.greetings()
        self.creating_players_fields()
        self.logic()


if __name__ == '__main__':
    g = Game()
    g.start()
