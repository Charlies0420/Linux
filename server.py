import socket
import threading
import queue
import json  # json.dumps(some)pack   json.loads(some)unpack
import time
import tkinter as tk
import tkinter.messagebox
import sys
import os
import pyautogui
import tkinter.scrolledtext as tkscrolled

from PIL import Image, ImageTk


# 获取局域网 IP 地址
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print(f"获取 IP 地址失败: {e}")
        return None


IP = get_local_ip()
PORT = 8888
print(f"服务器 IP 地址: {IP}:{PORT}")

que = queue.Queue()  # A queue for storing information sent by the client
users = []  # It is used to store online user information  [conn, user, addr]
lock = threading.Lock()  # Create locks that prevent the order in which multiple threads write data from being scrambled
ii = 0  # Used to determine whether to open or close a list box
threads = []  # Used to store thread ids


# 消息格式
# 普通用户字符串消息格式 = ' ' + users[j][1] + '：' + message[1] #message[1] = user:;【Message sending object】users[j][1]Is the name of the sender

# 服务器通信的准备工作
# 1.初始化套接字
# 2.bind绑定地址和端口号到套接字
# 3.listen监听客户端请求


def onlines():  # 将在线用户存进online列表中
    online = []
    for i in range(len(users)):
        online.append(users[i][1])
    return online


class server_deal:  # 服务器管理页面类
    global ban
    global users

    def __init__(self, window):
        self.window = window
        # 窗口标题
        self.window.title("管理员窗口")
        # 窗口大小设置，放大1.5倍
        width = int(450 * 1.5)
        height = int(360 * 1.5)
        self.window.geometry(f"{width}x{height}+500+220")
        self.window.resizable(0, 0)  # 窗口大小设置不可调整

        # 加载背景图片
        try:
            self.background_image = Image.open('xiaohui.png')
            # 调整图片大小以适应窗口
            self.background_image = self.background_image.resize((width, height))
            self.background_photo = ImageTk.PhotoImage(self.background_image)
            self.background_label = tk.Label(self.window, image=self.background_photo)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        except FileNotFoundError:
            print("未找到背景图片文件 'xiaohui.png'")

        # 在线用户用户名
        self.User = tk.StringVar()
        self.User.set('')
        # 创建一个多行文本框以显示在线用户
        self.listbox1 = tkinter.Listbox(root)
        # 调整列表框的位置和大小
        self.listbox1.place(x=int(310 * 1.5), y=0, width=int(130 * 1.5), height=int(320 * 1.5))
        # 增大列表框字体大小
        self.listbox1.config(font=("微软雅黑", 16))
        # 查看在线用户的摁扭
        self.button1 = tkinter.Button(root, text='用户列表', command=self.show_users)
        # 调整按钮的位置和大小
        self.button1.place(x=int(330 * 1.5), y=int(325 * 1.5), width=int(90 * 1.5), height=int(30 * 1.5))
        # 增大按钮字体大小
        self.button1.config(font=("微软雅黑", 16))
        # 用户名标签以及输入框
        self.labelUser = tk.Label(window, text='用户名')
        # 调整标签的位置和大小
        self.labelUser.place(x=int(20 * 1.5), y=int(100 * 1.5), width=int(100 * 1.5), height=int(20 * 1.5))
        # 增大标签字体大小
        self.labelUser.config(font=("微软雅黑", 16))
        self.entryUser = tk.Entry(window, width=80, textvariable=self.User)
        # 调整输入框的位置和大小
        self.entryUser.place(x=int(120 * 1.5), y=int(100 * 1.5), width=int(130 * 1.5), height=int(20 * 1.5))
        # 增大输入框字体大小
        self.entryUser.config(font=("微软雅黑", 16))
        # 禁言摁扭
        self.button = tk.Button(self.window, text="禁言", command=self.deal_ban)
        # 调整禁言按钮的位置和大小
        self.button.place(x=int(60 * 1.5), y=int(210 * 1.5), width=int(70 * 1.5), height=int(30 * 1.5))
        # 增大禁言按钮字体大小
        self.button.config(font=("微软雅黑", 16))
        # 解除禁言的摁扭
        self.button = tk.Button(self.window, text="解禁", command=self.deal_unban)
        # 调整解禁按钮的位置和大小
        self.button.place(x=int(120 * 1.5), y=int(210 * 1.5), width=int(70 * 1.5), height=int(30 * 1.5))
        # 增大解禁按钮字体大小
        self.button.config(font=("微软雅黑", 16))

        # 添加查询按钮
        self.buttonQuery = tk.Button(self.window, text="查询",
                                     command=self.query_user,
                                     font=("微软雅黑", 16),
                                     width=7, height=1)
        self.buttonQuery.place(x=int(180 * 1.5), y=int(210 * 1.5),
                               width=int(70 * 1.5), height=int(30 * 1.5))

        # 创建“不会使用？”按钮
        self.help_button = tk.Button(self.window, text="不会使用？", command=self.show_readme)
        # 调整按钮的位置和大小，放在左下角
        button_width = 80
        button_height = 30
        self.help_button.place(x=10, y=height - button_height - 10, width=button_width * 1.5,
                               height=button_height * 1.5)
        # 增大按钮字体大小
        self.help_button.config(font=("微软雅黑", 16))
        # 关闭窗口时调用end结束程序
        self.window.protocol("WM_DELETE_WINDOW", self.end)
        # 显示在线用户列表
        self.show_users()


    def show_readme(self):
        try:
            # 获取当前脚本所在目录
            script_dir = os.path.dirname(os.path.abspath(__file__))
            readme_path = os.path.join(script_dir, 'server_readme.txt')
            with open(readme_path, 'r', encoding='utf-8') as file:
                readme_content = file.read()
            # 创建一个新窗口来显示说明文档
            readme_window = tk.Toplevel(self.window)
            readme_window.title("使用说明")
            # 设置窗口大小
            readme_window.geometry("600x400")

            # 创建滚动文本框来显示内容
            text_widget = tkscrolled.ScrolledText(readme_window, wrap=tk.WORD, width=70, height=20)
            text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
            text_widget.insert(tk.INSERT, readme_content)
            text_widget.config(state=tk.DISABLED)  # 让文本框只读
        except FileNotFoundError:
            tk.messagebox.showerror("错误", "未找到 server_readme.txt 文件。")
        except Exception as e:
            tk.messagebox.showerror("错误", f"读取文件时出错: {e}")

    def deal_ban(self):
        ban_name = self.entryUser.get()  # 获取要禁言的用户名
        data = "【禁言警告】" + ":;" + "server" + ":;" + ban_name
        que.put(("!", data))
        tk.messagebox.showinfo('温馨提示', message='禁言成功！')  # 管理页反馈

    def deal_unban(self):
        unban_name = self.entryUser.get()
        data = "【解禁提示】" + ":;" + "server" + ":;" + unban_name
        que.put(("@", data))
        tk.messagebox.showinfo('温馨提示', message='解禁成功！')

    def query_user(self):
        username = self.entryUser.get().strip()
        if not username:
            tk.messagebox.showwarning("提示", "请输入要查询的用户名")
            return

        try:
            with open("data/user.txt", 'r', encoding="utf-8") as f:
                while True:
                    line_user = f.readline().strip()
                    line_pwd = f.readline().strip()
                    line_phone = f.readline().strip()
                    if not line_user:
                        break
                    if line_user == username:
                        self.show_user_info(username, line_pwd, line_phone)
                        return
                tk.messagebox.showwarning("提示", "用户不存在")
        except FileNotFoundError:
            tk.messagebox.showerror("错误", "用户数据文件不存在")
        except Exception as e:
            tk.messagebox.showerror("错误", f"查询失败: {str(e)}")

    def show_user_info(self, username, password, phone):
        info_window = tk.Toplevel(self.window)
        info_window.title(f"{username} 的信息")
        info_window.geometry("300x150")

        tk.Label(info_window, text="用户名:", font=("微软雅黑", 14)).place(x=30, y=20)
        tk.Label(info_window, text=username, font=("微软雅黑", 14)).place(x=100, y=20)

        tk.Label(info_window, text="密码:", font=("微软雅黑", 14)).place(x=30, y=60)
        tk.Label(info_window, text=password, font=("微软雅黑", 14)).place(x=100, y=60)

        tk.Label(info_window, text="手机号:", font=("微软雅黑", 14)).place(x=30, y=100)
        tk.Label(info_window, text=phone, font=("微软雅黑", 14)).place(x=100, y=100)

    def end(self):
        # 销毁窗口
        self.window.destroy()
        try:
            os._exit(0)
        except:
            print("failed to close")

    def show_users(self):
        global ii
        if ii == 1:
            self.listbox1.place_forget()  # 隐藏列表框
            ii = 0
        else:
            # 调整列表框的位置和大小
            self.listbox1.place(x=int(310 * 1.5), y=0, width=int(130 * 1.5), height=int(320 * 1.5))  # 显示列表框
            ii = 1

        self.listbox1.delete(0, tkinter.END)  # 清除列表框内容
        # 显示在线人数
        number = ('   在线用户数: ' + str(len(users)))
        self.listbox1.insert(tkinter.END, number)
        # 设置文字和背景颜色
        self.listbox1.itemconfig(tkinter.END, fg='green', bg="#f0f0ff")
        # 插入群发选项
        self.listbox1.insert(tkinter.END, '【群发】')
        self.listbox1.itemconfig(tkinter.END, fg='green')
        for i in range(len(users)):
            # 插入每个用户的用户名，以绿色显示
            self.listbox1.insert(tkinter.END, (users[i][1]))
            self.listbox1.itemconfig(tkinter.END, fg='green')


class ChatServer(threading.Thread):  # 继承threading.Thread
    global users, que, lock

    def __init__(self, port):  # 构造函数，用于创建套接字
        threading.Thread.__init__(self)  # 调用父类构造函数
        # 地址端口
        self.ADDR = ('', port)
        # 创建一个IPv4，TCP套接字，用于监听服务器请求
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 新增此行
        ss = self.s
        # 打印当前线程名称和ID
        print("thread name = {}, thread id = {}".format(threading.current_thread().name,
                                                        threading.current_thread().ident))

    # 接收所有客户端发来消息的函数
    def tcp_connect(self, conn, addr):
        # Add the user information to the users list after the connection
        print("thread name = {}, thread id = {}".format(threading.current_thread().name,
                                                        threading.current_thread().ident))
        user = conn.recv(1024)  # Receiving user name
        user = user.decode()
        for i in range(len(users)):
            if user == users[i][1]:
                print('User already exist')
                user = '' + user + '_2'
        if user == 'no':
            user = addr[0] + ':' + str(addr[1])
        users.append((conn, user, addr))
        print('新的连接:', addr, ':', user, end='')  # Print user name
        d = onlines()  # Refresh the online user display on the client when a new connection is available
        self.recv(d,
                  addr)  # The slef.recv function is used to broadcast the user list to all clients in a message queue after the initial connection
        self.show_users()
        try:
            while True:
                data = conn.recv(1024)
                if not data:  # Check if the data is empty, indicating the client has disconnected
                    break
                data = data.decode()
                try:
                    data = json.loads(data)
                    if isinstance(data, dict):
                        file_size = data.get('file_length')
                        file_path = data.get('file_name')
                        # 1. Obtain the directory where the os is stored
                        working_path = os.getcwd()
                        # 2. Read the file name when the file is sent
                        file_name = os.path.basename(file_path)
                        # 3. Overlay to get a new path (file saving path)
                        file_path = os.path.join(working_path, 'server_photos', file_name)
                        now_size = 0
                        with open(file_path, 'wb') as f:
                            while now_size < file_size:
                                tmp_data = conn.recv(1024)
                                now_size += len(tmp_data)
                                f.write(tmp_data)
                        with open(file_path, 'rb') as f:
                            tmp_data = f.read()
                            self.recv(data, addr)  # Save the message to the queue
                            que.put(("图片", tmp_data))
                        # que.put(("图片", new_data))
                except:
                    self.recv(data, addr)  # Save the message to the queue
        except:
            pass
        finally:
            print(user + ' 断开连接')
            self.delUsers(conn, addr)  # Move the disconnected user out of users
            conn.close()
            self.show_users()

    # 确定断开连接的用户在users列表中的位置，并将其从列表中删除，同时刷新客户端在线用户显示
    def delUsers(self, conn, addr):
        a = 0
        for i in users:
            if i[0] == conn:
                users.pop(a)
                print(' 在线用户: ', end='')  # 打印剩余在线用户
                # 重新获取在线用户列表
                d = onlines()
                # 广播在线用户列表给所有客户端
                self.recv(d, None)
                print(d)
                # 清理消息队列中该客户端的消息
                with lock:
                    que.queue = queue.deque([msg for msg in que.queue if msg[0] != addr])
                break
            a += 1

    def show_users(self):
        p1.listbox1.delete(0, tkinter.END)  # 清空服务器管理界面列表框
        # 重新获取在线用户数量并重复显示操作
        number = ('   在线用户数: ' + str(len(users)))
        p1.listbox1.insert(tkinter.END, number)
        p1.listbox1.itemconfig(tkinter.END, fg='green', bg="#f0f0ff")
        p1.listbox1.insert(tkinter.END, '【群发】')
        p1.listbox1.itemconfig(tkinter.END, fg='green')
        for i in range(len(users)):
            p1.listbox1.insert(tkinter.END, (users[i][1]))
            p1.listbox1.itemconfig(tkinter.END, fg='green')

    # 将接收到的消息（IP、端口和发送的信息）存储在队列 que 中
    def recv(self, data, addr):
        global users
        lock.acquire()
        # 获取锁，防止多线程冲突
        try:
            # 尝试将数据解析为 JSON 对象
            data = json.loads(data)
            que.put((addr, data))
        except:
            que.put((addr, data))
        finally:
            lock.release()

    # 将队列中的消息发送给所有在线用户
    def sendData(self):
        print("thread name = {}, thread id = {}".format(threading.current_thread().name,
                                                        threading.current_thread().ident))
        while True:
            if not que.empty():
                data = ''
                reply_text = ''
                message = que.get()  # Fetch the first element of the queue, message[0] = addr, message[1] = data
                print(message)
                if message[1] == '':  # Check if the data is empty
                    continue
                if isinstance(message[1], str):
                    for i in range(len(users)):
                        try:
                            # user[i][1] is user name, users[i][2] is addr, Change message[0] to the user name
                            source_user = 0
                            if message[0] == '!':
                                data = ' ' + 'server' + '：' + message[1]
                                print(' this: message is from server')  # Print the sending source of the message
                                print('The User {} has been banned'.format(list(message[1].split(":;"))[2]))
                            elif message[0] == '@':
                                data = ' ' + 'server' + '：' + message[1]
                                print(' this: message is from server')  # Print the sending source of the message
                                print('The User {} has been freed'.format(list(message[1].split(":;"))[2]))
                            else:
                                for j in range(len(users)):
                                    if message[0] == users[j][
                                        2]:  # message[0] = addr, message[1] = data Determine which user sent the message
                                        print(users[j][2])
                                        print(' this: message is from user[{}]'.format(
                                            j))  # Print the sending source of the message
                                        data = ' ' + users[j][1] + '：' + message[1]  # message[1] = user:;【消息发送对象】
                                    print(data)
                            users[i][0].send(
                                data.encode())  # Each message is sent to everyone and this statement encodes data and sends it to each user's socket
                        except BrokenPipeError:
                            print(f"Client {users[i][1]} disconnected. Removing from user list.")
                            self.delUsers(users[i][0], users[i][2])
                elif isinstance(message[1], list) or isinstance(message[1], dict):
                    data = json.dumps(message[1])
                    for i in range(len(users)):
                        try:
                            users[i][0].send(data.encode())
                        except BrokenPipeError:
                            print(f"Client {users[i][1]} disconnected. Removing from user list.")
                            self.delUsers(users[i][0], users[i][2])
                if isinstance(message[1], dict):
                    wait_times = 0
                    while que.empty():
                        print("The data hasn's already arrived")
                        time.sleep(0.5)
                        wait_times += 0.5
                        if wait_times >= 10:
                            print(
                                "服务器接收数据失败")  # If the receiving time is longer than 5 seconds, the message is lost
                            # trans_flag = 1
                            break
                    if not que.empty():
                        photo_message = que.get()
                        print(type(photo_message))
                        print("The message is from user" + message[1]['from_user'])
                        time.sleep(0.5)  # Ensure that the current dictionary message has been delivered
                        for i in range(len(users)):
                            try:
                                users[i][0].sendall(photo_message[1])
                                print("server sent photo message")
                            except BrokenPipeError:
                                print(f"Client {users[i][1]} disconnected. Removing from user list.")
                                self.delUsers(users[i][0], users[i][2])

    def run(self):
        try:
            self.s.bind(self.ADDR)
            self.s.listen(5)
            print('服务器已启动，正在监听端口...')
        except Exception as e:
            print(f"启动服务器失败: {e}")
            self.s.close()
            return

        try:
            q = threading.Thread(target=self.sendData)
            q.setDaemon(True)
            q.start()

            while True:
                conn, addr = self.s.accept()
                # 简单连接数限制
                if threading.active_count() > 100:  # 根据实际情况调整
                    conn.send("服务器达到最大负载".encode())
                    conn.close()
                    continue

                t = threading.Thread(target=self.tcp_connect, args=(conn, addr))
                t.setDaemon(True)
                t.start()
        except KeyboardInterrupt:
            print("\n服务器正在关闭...")
        finally:
            self.s.close()
            print("服务器套接字已关闭")


if __name__ == '__main__':
    cserver = ChatServer(PORT)
    cserver.start()  # Apply for the system thread, in this case the main thread
    root = tk.Tk()
    p1 = server_deal(root)  # These two sheets can be run separately
    root.mainloop()