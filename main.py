import random as r
import tkinter as tk

REMAINED_MINES = 0
REMAINED_CELLS = 0
ROWS, COLUMNS = 0, 0
MINES_FIELD = []
REM_MINES_STRING = 'Осталось мин: {}'
REM_CELLS_STRING = 'Осталось клеток: {}'
END_GAME = False


class Cell:
    def __init__(self, frame, opened=False, value=''):
        self.opened = opened
        self.value = value
        self.button = tk.Button(
            frame, text='', font='sans 12 bold', height=1, width=2
        )


def count_neighbor_mines(row, column, radius=1):
    global MINES_FIELD, ROWS, COLUMNS
    return sum(
        [
            sum(
                [
                    MINES_FIELD[i][j].value == "*"
                    if 0 <= i < ROWS and 0 <= j < COLUMNS
                    else 0 for j in range(column - radius, column + radius + 1)  # 2
                ]
            ) for i in range(row - radius, row + radius + 1)  # 1
        ]
    )


def reveal_clear_neighbors(row, column, radius=1):
    global MINES_FIELD, ROWS, COLUMNS
    [
        [
            change(i, j) for j in range(column - radius, column + radius + 1)  # 2
            if 0 <= i < ROWS and 0 <= j < COLUMNS
            and MINES_FIELD[i][j].opened is False
        ] for i in range(row - radius, row + radius + 1)  # 1
    ]


def change(i, j):
    global MINES_FIELD, REMAINED_CELLS, END_GAME
    if END_GAME:
        return -1

    if not MINES_FIELD[i][j].opened:  # Чтобы нельзя было уже клацать по открытой клетке (при выключенной кнопке все равно засчитываются нажатия)
        REMAINED_CELLS -= 1
    MINES_FIELD[i][j].opened = True
    MINES_FIELD[i][j].button['state'] = tk.DISABLED  # Выключаем уже открытую клетку

    if MINES_FIELD[i][j].value != '*':  # Если клетка - не мина
        count = count_neighbor_mines(row=i, column=j)
        MINES_FIELD[i][j].button['bg'] = 'white'
        if count == 0:  # Если мин вокруг нет
            MINES_FIELD[i][j].button['text'] = ''
            reveal_clear_neighbors(i, j)
        else:  # Если мины вокруг есть
            MINES_FIELD[i][j].button['text'] = count
    else:  # Если клетка - мина
        END_GAME = True
        MINES_FIELD[i][j].button['text'] = '*'
        MINES_FIELD[i][j].button['bg'] = 'red'
        MINES_FIELD[i][j].button['fg'] = 'black'
        newWindow = tk.Toplevel(window)
        newWindow.geometry("200x200")
        tk.Label(newWindow, text="Game over").pack()
        newWindow.grab_set()
    update_mines_left()


def check_entries(rows, columns, mines):
    return (
        rows.isdigit() and columns.isdigit() and mines.isdigit()  # Все введенные значения - числа
        and 0 <= int(rows) <= 15 and 0 <= int(columns) <= 15  # столбцы и строки в определенных границах
        and int(mines) <= int(rows) * int(columns) * 0.3  # мин не слишком много
    )


def place_mine(i, j):
    global MINES_FIELD, REMAINED_MINES
    if END_GAME:
        return -1
    if not MINES_FIELD[i][j].opened:
        if MINES_FIELD[i][j].button['text'] == '⚑':
            MINES_FIELD[i][j].button['text'] = ''
            MINES_FIELD[i][j].button['bg'] = 'cyan'
            REMAINED_MINES += 1
        elif REMAINED_MINES:  # Если еще есть свободные флажки
            MINES_FIELD[i][j].button['bg'] = 'light cyan'
            MINES_FIELD[i][j].button['text'] = '⚑'
            REMAINED_MINES -= 1
    update_mines_left()  # Обновление информации об оставшихся минах


def create_field():
    global MINES_FIELD, REMAINED_MINES, REMAINED_CELLS, mines_field_frame, rows_entry, columns_entry, mines_entry, ROWS, COLUMNS, END_GAME

    if not check_entries(rows_entry.get(), columns_entry.get(), mines_entry.get()):  # Проверяем корректность ввода
        newWindow = tk.Toplevel(window)
        newWindow.geometry("200x200")
        tk.Label(newWindow, text="Ошибка создания поля").pack()
        newWindow.grab_set()
        return -1

    # Переводим все значения полей ввода в числа
    ROWS = int(rows_entry.get())
    COLUMNS = int(columns_entry.get())
    REMAINED_MINES = int(mines_entry.get())

    # удаление старого поля
    for widget in mines_field_frame.winfo_children():
        widget.destroy()

    # Создаем массив с минами (array)
    REMAINED_CELLS = ROWS * COLUMNS - REMAINED_MINES
    array = ['*'] * REMAINED_MINES + [''] * (ROWS * COLUMNS - REMAINED_MINES)
    r.shuffle(array)

    # Создаем матрицу из значений массива мин (array)
    buttons = []
    for i in range(ROWS):
        temp = []
        for j in range(COLUMNS):
            cell = Cell(mines_field_frame, False, array[i * COLUMNS + j])
            cell.button.grid(row=i, column=j)
            cell.button['bg'] = 'cyan'
            cell.button.bind(
                '<Button-1>', lambda event, i=i, j=j: change(i, j)
            )  # ЛКМ
            cell.button.bind(
                '<Button-3>', lambda event, i=i, j=j: place_mine(i, j)
            )  # ПКМ
            temp.append(cell)
        buttons.append(temp)
    MINES_FIELD = buttons
    END_GAME = False


def update_mines_left():
    global mines_left_label, mines_right_label, END_GAME
    mines_left_label['text'] = REM_MINES_STRING.format(REMAINED_MINES)
    mines_right_label['text'] = REM_CELLS_STRING.format(REMAINED_CELLS)
    if REMAINED_CELLS == REMAINED_MINES == 0:
        END_GAME = True
        newWindow = tk.Toplevel(window)
        newWindow.geometry("200x200")
        tk.Label(newWindow, text="Ура победа").pack()

        # захват фокуса на маленькое окно, чтобы большое было неактивным
        newWindow.grab_set()


# Создание главного окна
window = tk.Tk()
window.title('minesweeper')
window.geometry('800x600')

mines_count_frame = tk.Frame(window)
mines_count_frame.pack()

mines_field_frame = tk.Frame(window)
mines_field_frame.pack()

entries_frame = tk.Frame(window)
entries_frame.pack()

rows_label = tk.Label(entries_frame, text='Количество строк (макс. 20)')
rows_label.grid(row=1, column=1)
rows_entry = tk.Entry(entries_frame)
rows_entry.insert(0, '10')
rows_entry.grid(row=2, column=1)

columns_label = tk.Label(entries_frame, text='Количество столбцов (макс. 20)')
columns_label.grid(row=1, column=2)
columns_entry = tk.Entry(entries_frame)
columns_entry.insert(0, '10')
columns_entry.grid(row=2, column=2)

mines_label = tk.Label(entries_frame, text='Количество мин (макс. 30% поля)')
mines_label.grid(row=1, column=3)
mines_entry = tk.Entry(entries_frame)
mines_entry.insert(0, '10')
mines_entry.grid(row=2, column=3)

new_game_button = tk.Button(entries_frame, text='Новая игра')
new_game_button.grid(row=3, column=2)
new_game_button.config(command=create_field)

create_field()

mines_left_label = tk.Label(
    mines_count_frame, text=REM_MINES_STRING.format(REMAINED_MINES)
)
mines_left_label.grid(row=1, column=1)
mines_right_label = tk.Label(
    mines_count_frame, text=REM_CELLS_STRING.format(REMAINED_CELLS)
)
mines_right_label.grid(row=2, column=1)

window.mainloop()
