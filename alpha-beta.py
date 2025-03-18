import tkinter as tk
import time

class TicTacToe:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Tic-Tac-Toe")
        self.board = [' '] * 9
        self.current_player = None  # 玩家可以选择先手/后手
        self.total_time = 0  # 总时间
        self.step_start_time = None  # 当前步开始时间
        self.buttons = []  # 保存棋盘按钮
        self.create_board()
        self.create_labels()
        self.choose_first_player()

    def create_board(self):
        """创建棋盘按钮"""
        for i in range(9):
            btn = tk.Button(self.window, text=' ', font='Arial 20', width=5, height=2,
                            command=lambda i=i: self.player_move(i))
            btn.grid(row=i // 3, column=i % 3)
            self.buttons.append(btn)

    def create_labels(self):
        """创建时间显示标签"""
        self.step_time_label = tk.Label(self.window, text="当前步时: 0.00秒", font='Arial 12')
        self.step_time_label.grid(row=3, column=0, columnspan=3)

        self.total_time_label = tk.Label(self.window, text="总时间: 0.00秒", font='Arial 12')
        self.total_time_label.grid(row=4, column=0, columnspan=3)

    def choose_first_player(self):
        """选择先手玩家"""
        choice_window = tk.Toplevel(self.window)
        choice_window.title("选择先手")

        tk.Label(choice_window, text="选择谁先手：", font='Arial 14').pack()

        tk.Button(choice_window, text="玩家 (X)", font='Arial 12',
                  command=lambda: self.start_game('X', choice_window)).pack()

        tk.Button(choice_window, text="计算机 (O)", font='Arial 12',
                  command=lambda: self.start_game('O', choice_window)).pack()

    def start_game(self, first_player, choice_window):
        """开始游戏并初始化时间"""
        self.current_player = first_player
        self.step_start_time = time.time()  # 初始化步时
        choice_window.destroy()
        self.update_step_time()

        if self.current_player == 'O':
            self.computer_move()

    def update_step_time(self):
        """实时更新当前步时间"""
        if self.step_start_time:
            elapsed = time.time() - self.step_start_time
            self.step_time_label.config(text=f"当前步时: {elapsed:.2f}秒")
        self.window.after(100, self.update_step_time)

    def update_total_time(self):
        """更新总时间"""
        elapsed = time.time() - self.step_start_time
        self.total_time += elapsed
        self.total_time_label.config(text=f"总时间: {self.total_time:.2f}秒")

    def player_move(self, index):
        """处理玩家的落子操作"""
        if self.board[index] == ' ' and self.current_player == 'X':
            self.make_move(index, 'X')
            if not self.check_game_over('X'):
                self.update_total_time()
                self.current_player = 'O'
                self.step_start_time = time.time()  # 重置步时间
                self.computer_move()

    def computer_move(self):
        """计算机的落子操作"""
        move = self.alpha_beta(0, True, -1000, 1000)[1]
        self.make_move(move, 'O')
        if not self.check_game_over('O'):
            self.update_total_time()
            self.current_player = 'X'
            self.step_start_time = time.time()  # 重置步时间

    def make_move(self, index, player):
        """在棋盘上进行标记"""
        self.board[index] = player
        self.buttons[index].config(text=player)

    def alpha_beta(self, depth, is_max, alpha, beta):
        """Alpha-Beta 剪枝算法"""
        winner = self.get_winner()
        if winner:
            return (1 if winner == 'O' else -1, None)
        elif ' ' not in self.board:
            return (0, None)  # 平局

        best_score = -1000 if is_max else 1000
        best_move = None

        for i in range(9):
            if self.board[i] == ' ':
                self.board[i] = 'O' if is_max else 'X'
                score = self.alpha_beta(depth + 1, not is_max, alpha, beta)[0]
                self.board[i] = ' '  # 撤销落子
                if is_max:
                    if score > best_score:
                        best_score = score
                        best_move = i
                    alpha = max(alpha, score)
                else:
                    if score < best_score:
                        best_score = score
                        best_move = i
                    beta = min(beta, score)
                if beta <= alpha:
                    break

        return best_score, best_move

    def get_winner(self):
        """判断是否有赢家"""
        win_conditions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # 横向
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # 纵向
            [0, 4, 8], [2, 4, 6]  # 对角线
        ]
        for a, b, c in win_conditions:
            if self.board[a] == self.board[b] == self.board[c] != ' ':
                return self.board[a]
        return None

    def check_game_over(self, player):
        """检查游戏是否结束"""
        winner = self.get_winner()
        if winner:
            self.end_game(f"{winner} 获胜!")
            return True
        elif ' ' not in self.board:
            self.end_game("平局!")
            return True
        return False

    def end_game(self, message):
        """结束游戏并禁用所有按钮"""
        for btn in self.buttons:
            btn.config(state='disabled')
        print(message)  # 打印结果

    def run(self):
        """启动游戏主循环"""
        self.window.mainloop()

# 运行游戏
game = TicTacToe()
game.run()
