import tkinter as tk
from random import shuffle
from tkinter.messagebox import showinfo, showerror
from colors import colors
from PIL import Image, ImageTk

class MyButton(tk.Button):

    def __init__(self, master, x, y, number=0, *args, **kwargs):
        super(MyButton, self).__init__(master, width=3, font='Calibri 15 bold', *args, **kwargs)
        self.x = x
        self.y = y
        self.number = number
        self.is_mine = False
        self.count_bomb = 0
        self.is_open = False

    def __repr__(self):
        return f'MyButton {self.x} {self.y} {self.number} {self.is_mine}'


class MineSweeper:
    window = tk.Tk()
    window.iconphoto(False, tk.PhotoImage(file='MineSweeper_icon.png'))
    ROW = 7
    COLUMNS = 10
    MINES = 10
    IS_GAME_OVER = False
    IS_FIRST_CLICK = True
    image_file_1 = Image.open('smilyhappy.png').resize((60, 60))
    image_file_2 = Image.open('smilysad.png').resize((60, 60))
    image_file_3 = Image.open('success_smile.png').resize((60, 60))
    vp_image_1 = ImageTk.PhotoImage(image_file_1)
    vp_image_2 = ImageTk.PhotoImage(image_file_2)
    vp_image_3 = ImageTk.PhotoImage(image_file_3)
    IS_HAPPY = True
    MINES_TO_FLAG = MINES
    safe_buttons_to_open = ROW * COLUMNS - MINES

    def __init__(self):
        self.buttons = []
        for i in range(MineSweeper.ROW + 2):
            temp = []
            for j in range(MineSweeper.COLUMNS + 2):
                btn = MyButton(self.window, x=i, y=j)
                btn.config(command=lambda button=btn: self.click(button))
                btn.bind("<Button-3>", self.right_click)
                temp.append(btn)
            self.buttons.append(temp)
        self.img_button = tk.Button(self.window, image=MineSweeper.vp_image_1)

    def right_click(self, event):
        cur_btn = event.widget
        if cur_btn['state'] == 'normal':
            if MineSweeper.MINES_TO_FLAG == 0:
                pass
            else:
                MineSweeper.MINES_TO_FLAG -= 1
                cur_btn['state'] = 'disabled'
                cur_btn['text'] = '🚩'
                cur_btn['disabledforeground'] = 'red'
        elif cur_btn['text'] == '🚩':
            cur_btn['state'] = 'normal'
            cur_btn['text'] = ''
            MineSweeper.MINES_TO_FLAG += 1
        self.mines_to_flag_label['text'] = str(MineSweeper.MINES_TO_FLAG)

    def click(self, clicked_button: MyButton):

        if MineSweeper.IS_GAME_OVER:
            return

        if MineSweeper.IS_FIRST_CLICK:
            self.insert_mines(clicked_button.number)
            self.count_mines_in_buttons()
            self.print_buttons()
            MineSweeper.IS_FIRST_CLICK = False

        if clicked_button.is_mine:
            clicked_button.config(text='*', background='red', activeforeground='black')
            clicked_button.is_open = True
            MineSweeper.IS_HAPPY = False
            self.smile_label.config(image=MineSweeper.vp_image_2)
            MineSweeper.IS_GAME_OVER = True
            showinfo('Game over!', 'Вы проиграли')
            for i in range(1, MineSweeper.ROW + 1):
                for j in range(1, MineSweeper.COLUMNS + 1):
                    btn = self.buttons[i][j]
                    if btn.is_mine:
                        btn['text'] = '*'

        else:
            print(f' we have {MineSweeper.safe_buttons_to_open} safe buttons to open')
            MineSweeper.safe_buttons_to_open -= 1
            color = colors.get(clicked_button.count_bomb, 'black')
            if clicked_button.count_bomb:
                clicked_button.config(text=clicked_button.count_bomb, disabledforeground=color)
                clicked_button.is_open = True
            else:
                self.breadth_first_search(clicked_button)
            if MineSweeper.safe_buttons_to_open == 0:
                self.smile_label.config(image=MineSweeper.vp_image_3)
        clicked_button.config(state='disabled')
        clicked_button.config(relief=tk.SUNKEN)

    def breadth_first_search(self, btn: MyButton):
        queue = [btn]
        while queue:

            cur_btn = queue.pop()
            color = colors.get(cur_btn.count_bomb, 'black')
            if cur_btn.count_bomb:
                cur_btn.config(text=cur_btn.count_bomb, disabledforeground=color)
            else:
                cur_btn.config(text='',disabledforeground=color)
            cur_btn.is_open = True
            cur_btn.config(state='disabled')
            cur_btn.config(relief=tk.SUNKEN)

            if cur_btn.count_bomb == 0:
                x, y = cur_btn.x, cur_btn.y
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        # if not abs(dx - dy) == 1:
                        #     continue

                        next_btn = self.buttons[x + dx][y + dy]
                        if not next_btn.is_open and 1 <= next_btn.x <= MineSweeper.ROW and \
                            1 <= next_btn.y <= MineSweeper.COLUMNS and next_btn not in queue:
                            queue.append(next_btn)

    def create_settings_win(self):
        win_settings = tk.Toplevel(self.window)
        win_settings.wm_title('Настройки')

        tk.Label(win_settings, text="Количество строк").grid(row=0, column=0)
        row_entry = tk.Entry(win_settings)
        row_entry.insert(0, MineSweeper.ROW)
        row_entry.grid(row=0, column=1, padx=20, pady=20)

        tk.Label(win_settings, text="Количество столбцов").grid(row=1, column=0)
        column_entry = tk.Entry(win_settings)
        column_entry.insert(0, MineSweeper.COLUMNS)
        column_entry.grid(row=1, column=1, padx=20, pady=20)

        tk.Label(win_settings, text="Количество мин").grid(row=2, column=0)
        mines_entry = tk.Entry(win_settings)
        mines_entry.insert(0, MineSweeper.MINES)
        mines_entry.grid(row=2, column=1)

        tk.Button(win_settings, text='Применить',
                 command=lambda :self.change_settings(row_entry, column_entry, mines_entry))\
                .grid(row=3,column=0, columnspan=2, padx=20, pady=20)

    def change_settings(self, row: tk.Entry, column: tk.Entry, mines: tk.Entry):
        try:
            int(row.get()), int(column.get()), int(mines.get())
        except ValueError:
            showerror("Ошибка", "Вы ввели неправильное значение")

        MineSweeper.ROW = int(row.get())
        MineSweeper.COLUMNS = int(column.get())
        MineSweeper.MINES = int(mines.get())
        self.reload()

    def reload(self):
        [child.destroy() for child in self.window.winfo_children()]
        self.__init__()
        self.create_widgets()
        MineSweeper.IS_FIRST_CLICK = True
        MineSweeper.IS_GAME_OVER = False
        MineSweeper.MINES_TO_FLAG = MineSweeper.MINES
        self.mines_to_flag_label['text'] = str(MineSweeper.MINES_TO_FLAG)
        MineSweeper.safe_buttons_to_open = MineSweeper.ROW * MineSweeper.COLUMNS - MineSweeper.MINES

    def open_all_buttons(self):
        for i in range(MineSweeper.ROW + 2):
            for j in range(MineSweeper.COLUMNS + 2):
                btn = self.buttons[i][j]
                if btn.is_mine:
                    btn.config(text='*', backcround='red', disabledforeground='black')
                elif btn.count_bomb in colors:
                    color = colors.get(btn.count_bomb, 'black')
                    btn.config(text=btn.count_bomb, fg=color)

    def print_buttons(self):
        for i in range(1, MineSweeper.ROW + 1):
            for j in range(1, MineSweeper.COLUMNS + 1):
                btn = self.buttons[i][j]
                if btn.is_mine:
                    print('B', end='')
                else:
                    print(btn.count_bomb, end='')
            print()

    def insert_mines(self, number: int):
        index_mines = self.get_mines_places(number)
        print(index_mines)
        for i in range(1, MineSweeper.ROW + 1):
            for j in range(1, MineSweeper.COLUMNS + 1):
                btn = self.buttons[i][j]
                if btn.number in index_mines:
                    btn.is_mine = True

    def count_mines_in_buttons(self):
        for i in range(1, MineSweeper.ROW + 1):
            for j in range(1, MineSweeper.COLUMNS + 1):
                btn = self.buttons[i][j]
                count_bomb = 0
                if not btn.is_mine:
                    for row_dx in [-1, 0, 1]:
                        for col_dx in [-1, 0, 1]:
                            neighbour = self.buttons[i  + row_dx][j+col_dx]
                            if neighbour.is_mine:
                                count_bomb +=1
                btn.count_bomb = count_bomb

    @staticmethod
    def get_mines_places(exclude_number: int):
        indexes = list(range(1, MineSweeper.COLUMNS * MineSweeper.ROW + 1))
        print(f'Исключаем кнопку номер {exclude_number}')
        indexes.remove(exclude_number)
        shuffle(indexes)
        return indexes[:MineSweeper.MINES]


    def create_widgets(self):

        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)

        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label='Играть', command=self.reload)
        settings_menu.add_command(label='Настройки', command=self.create_settings_win)
        settings_menu.add_command(label='Выход', command=self.window.destroy)
        menubar.add_cascade(label="Меню", menu=settings_menu)

        count = 1
        for i in range(1, MineSweeper.ROW + 1):
            for j in range(1, MineSweeper.COLUMNS + 1):
                btn = self.buttons[i][j]
                btn.number = count
                btn.grid(row=i, column=j, stick='NESW')
                count += 1

        for i in range(1, MineSweeper.ROW + 1):
                tk.Grid.rowconfigure(self.window, i, weight=1)

        for i in range(1, MineSweeper.COLUMNS + 1):
            tk.Grid.columnconfigure(self.window, i, weight=1)
        
        self.smile_label = tk.Label(self.window, image=MineSweeper.vp_image_1)
        self.smile_label.grid(row=MineSweeper.ROW+1, column=int((MineSweeper.COLUMNS + 1)/ 2), columnspan=2)
        
        self.mines_to_flag_label = tk.Label(self.window, font='Calibri 25 bold', foreground='red', text=MineSweeper.MINES_TO_FLAG)
        self.mines_to_flag_label.grid(row=MineSweeper.ROW + 2, column=int((MineSweeper.COLUMNS + 1) / 2), columnspan=2)
        # self.mines_to_flag_label.config()

    def start(self):
        self.create_widgets() # создаёт кнопку-меню, размещает уже созданные кнопки
        # self.open_all_buttons()
        self.window.mainloop()


game = MineSweeper()
game.start()