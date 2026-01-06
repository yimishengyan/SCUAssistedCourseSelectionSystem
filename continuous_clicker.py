# continuous_clicker.py
import pyautogui
import time
import threading
import keyboard
import sys


class ContinuousClicker:
    """
    连续点击工具
    功能：在指定位置按固定时间间隔连续点击
    快捷键：Ctrl+Alt+C 开始/停止点击，Ctrl+Alt+Q 退出
    """

    def __init__(self, config=None):
        """
        初始化点击器

        参数:
        config: 配置字典，包含点击参数
        """
        self.is_clicking = False
        self.click_thread = None

        # 默认配置
        default_config = {
            'click_position': None,  # 点击位置 (x, y)
            'click_interval': 2.0,  # 点击间隔(秒)
            'click_duration': 0.1,  # 点击持续时间(秒)
            'click_count': None,  # 总点击次数(None表示无限)
            'click_button': 'left',  # 点击按钮: 'left', 'right', 'middle'
            'verbose': True,  # 是否显示详细输出
            'show_mouse_position': True,  # 是否显示鼠标位置
        }

        # 合并配置
        self.config = default_config.copy()
        if config:
            self.config.update(config)

        # 当前位置显示相关
        self.show_position = self.config['show_mouse_position']
        self.position_thread = None

        self.print_welcome()

    def print_welcome(self):
        """打印欢迎信息"""
        if self.config['verbose']:
            print("\n" + "=" * 60)
            print("连续点击工具 v1.0")
            print("=" * 60)
            print("快捷键说明:")
            print("  Ctrl+Alt+C = 设置点击位置并开始/停止点击")
            print("  Ctrl+Alt+Q = 退出程序")
            print("  Ctrl+Alt+P = 显示/隐藏鼠标位置")
            print("-" * 60)
            print("使用步骤:")
            print("1. 按 Ctrl+Alt+C 开始设置")
            print("2. 将鼠标移动到要点击的位置")
            print("3. 按 Enter 键确认位置")
            print("4. 程序开始自动连续点击")
            print("5. 再次按 Ctrl+Alt+C 停止点击")
            print("=" * 60 + "\n")

    def get_click_position(self):
        """获取点击位置"""
        if self.config['verbose']:
            print("\n" + "=" * 60)
            print("步骤1: 设置点击位置")
            print("=" * 60)
            print("请将鼠标移动到要点击的位置")
            print("移动到位后，按 【Enter】 键确认")
            print("提示: 可以移动鼠标到按钮、链接或其他需要点击的位置")

        try:
            input("等待确认..." if self.config['verbose'] else "")
            x, y = pyautogui.position()

            if self.config['verbose']:
                print(f"✅ 点击位置已记录: ({x}, {y})")
                print(f"点击间隔: {self.config['click_interval']}秒")
                print(f"点击按钮: {self.config['click_button']}")

            self.config['click_position'] = (x, y)
            return (x, y)

        except Exception as e:
            if self.config['verbose']:
                print(f"设置位置时出错: {e}")
            return None

    def show_mouse_position_loop(self):
        """持续显示鼠标位置（在新线程中运行）"""
        while self.show_position:
            try:
                x, y = pyautogui.position()
                # 使用回车符覆盖上一行输出
                print(f"\r鼠标位置: ({x}, {y}) - 按Ctrl+Alt+P停止显示", end='', flush=True)
                time.sleep(0.1)
            except:
                break
        print()  # 换行

    def toggle_mouse_position(self):
        """切换鼠标位置显示"""
        self.show_position = not self.show_position

        if self.show_position:
            # 启动显示线程
            self.position_thread = threading.Thread(target=self.show_mouse_position_loop)
            self.position_thread.daemon = True
            self.position_thread.start()
            if self.config['verbose']:
                print("✓ 已启用鼠标位置显示")
        else:
            if self.config['verbose']:
                print("✓ 已禁用鼠标位置显示")

    def click_loop(self):
        """点击循环"""
        pos = self.config['click_position']
        interval = self.config['click_interval']
        duration = self.config['click_duration']
        button = self.config['click_button']
        max_clicks = self.config['click_count']
        verbose = self.config['verbose']

        if verbose:
            print("\n" + "=" * 60)
            print("步骤2: 开始连续点击")
            print("=" * 60)
            print(f"点击位置: {pos}")
            print(f"点击间隔: {interval}秒")
            print(f"点击次数: {'无限' if max_clicks is None else max_clicks}")
            print(f"点击按钮: {button}")
            print("-" * 60)
            print("连续点击已启动！")
            print("按 Ctrl+Alt+C 停止点击")
            print("=" * 60 + "\n")

        click_count = 0

        while self.is_clicking:
            try:
                click_count += 1

                # 执行点击
                pyautogui.click(x=pos[0], y=pos[1],
                                duration=duration,
                                button=button)

                if verbose:
                    current_time = time.strftime("%H:%M:%S")
                    status = f"[{current_time}] 第{click_count}次点击"
                    if max_clicks:
                        status += f" (剩余{max_clicks - click_count}次)"
                    print(status)

                # 检查是否达到最大点击次数
                if max_clicks and click_count >= max_clicks:
                    if verbose:
                        print(f"\n✓ 已完成 {max_clicks} 次点击，自动停止")
                    self.is_clicking = False
                    break

                # 等待下一次点击
                time.sleep(interval)

            except KeyboardInterrupt:
                if verbose:
                    print("\n点击被中断")
                break
            except Exception as e:
                if verbose:
                    print(f"[错误] 点击异常: {e}")
                time.sleep(1)

        if verbose and not self.is_clicking:
            print(f"\n⏹️  点击已停止，共点击 {click_count} 次")

    def start_clicking(self):
        """开始点击流程"""
        if not self.is_clicking:
            # 获取点击位置
            position = self.get_click_position()
            if position is None:
                if self.config['verbose']:
                    print("✗ 无法获取点击位置")
                return

            self.is_clicking = True

            # 在新线程中启动点击循环
            self.click_thread = threading.Thread(target=self.click_loop)
            self.click_thread.daemon = True
            self.click_thread.start()

            if self.config['verbose']:
                print("\n✅ 连续点击已启动！")
        else:
            self.stop_clicking()

    def stop_clicking(self):
        """停止点击"""
        if self.is_clicking:
            if self.config['verbose']:
                print("\n正在停止连续点击...")
            self.is_clicking = False

            # 等待点击线程结束
            if self.click_thread and self.click_thread.is_alive():
                self.click_thread.join(timeout=2.0)

            if self.config['verbose']:
                print("连续点击已停止")

    def toggle_clicking(self):
        """切换点击状态"""
        if self.is_clicking:
            self.stop_clicking()
        else:
            self.start_clicking()

    def run(self):
        """运行主程序循环"""
        # 设置快捷键
        keyboard.add_hotkey('ctrl+alt+c', self.toggle_clicking)
        keyboard.add_hotkey('ctrl+alt+q', self.quit_program)
        keyboard.add_hotkey('ctrl+alt+p', self.toggle_mouse_position)

        if self.config['verbose']:
            print("程序已就绪，等待快捷键命令...")
            print("提示: 按 Ctrl+Alt+C 开始设置点击位置")
            print("      按 Ctrl+Alt+P 显示鼠标位置")
            print("      按 Ctrl+Alt+Q 退出程序\n")

        try:
            keyboard.wait()
        except KeyboardInterrupt:
            self.quit_program()

    def quit_program(self):
        """安全退出程序"""
        if self.config['verbose']:
            print("\n" + "=" * 60)
            print("正在退出连续点击工具...")

        self.stop_clicking()
        self.show_position = False  # 停止位置显示

        time.sleep(0.5)

        if self.config['verbose']:
            print("感谢使用！")
            print("=" * 60)

        sys.exit(0)


def check_dependencies():
    """检查必要的Python库是否已安装"""
    print("检查运行环境...")

    required_modules = [
        ('pyautogui', 'pyautogui'),
        ('keyboard', 'keyboard'),
    ]

    all_ok = True
    for import_name, package_name in required_modules:
        try:
            __import__(import_name)
            print(f"  ✓ {package_name}")
        except ImportError:
            print(f"  ✗ {package_name} 未安装")
            all_ok = False

    return all_ok