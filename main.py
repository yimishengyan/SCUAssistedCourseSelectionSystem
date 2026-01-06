#!/usr/bin/env python3
# main.py
# 整合版主程序 - 课程检测 + 鼠标连点
# 使用说明: 直接运行此文件即可启动

import sys
import os
import time
import threading
import keyboard

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入核心模块
from course_monitor import CourseMonitor, check_dependencies as check_monitor_deps
from continuous_clicker import ContinuousClicker, check_dependencies as check_clicker_deps
import config


class IntegratedApp:
    """
    整合版应用程序
    功能：管理课程检测和鼠标连点两个功能
    """

    def __init__(self):
        self.course_monitor = None
        self.clicker = None
        self.is_running = False
        self.stop_event = threading.Event()
        self.has_shown_stop_message = False  # 新增：标记是否已经显示过停止消息

        # 从配置文件加载设置
        self.course_config = config.COURSE_MONITOR_CONFIG.copy()
        self.clicker_config = config.CLICKER_CONFIG.copy()
        self.feature_switches = config.FEATURE_SWITCHES.copy()

    def check_all_dependencies(self):
        """检查所有必要的Python库"""
        print("检查运行环境...")

        # 检查课程检测依赖
        print("\n[课程检测模块依赖]")
        monitor_ok = check_monitor_deps()

        # 检查鼠标连点依赖
        print("\n[鼠标连点模块依赖]")
        clicker_ok = check_clicker_deps()

        return monitor_ok and clicker_ok

    def print_clicker_exit_instructions(self):
        """打印鼠标连点退出说明"""
        print("\n" + "=" * 60)
        print("❗ 鼠标连点功能 - 重要控制提示 ❗")
        print("=" * 60)
        print("启动后如何控制鼠标连点：")
        print("1. 停止连点：按 【Ctrl+Alt+C】")
        print("2. 退出程序：按 【Ctrl+Alt+Q】")
        print("3. 紧急停止：也可以按 【Ctrl+C】 强制中断")
        print("=" * 60)

    def ask_feature_enable(self):
        """询问用户启用哪些功能"""
        print("\n" + "=" * 60)
        print("功能选择")
        print("=" * 60)

        # 询问是否启用鼠标连点
        print("\n1. 鼠标连点功能")
        print("   功能：在指定位置按固定间隔连续点击")
        print("   用途：自动点击刷新按钮、提交按钮等")

        # 先告诉用户如何停止鼠标连点
        self.print_clicker_exit_instructions()

        enable_clicker = input("是否启用鼠标连点功能？(y/n, 默认n): ").strip().lower()
        if enable_clicker == 'y':
            self.feature_switches['enable_clicker'] = True
            print("   ✓ 已启用鼠标连点功能")
        else:
            self.feature_switches['enable_clicker'] = False
            print("   ✗ 不启用鼠标连点功能")

        # 询问是否启用课程检测
        print("\n2. 课程检测功能")
        print("   功能：监控指定区域，发现目标课程时发出提醒")
        print("   用途：选课时自动检测课程是否出现")

        enable_monitor = input("是否启用课程检测功能？(y/n, 默认n): ").strip().lower()
        if enable_monitor == 'y':
            self.feature_switches['enable_course_monitor'] = True
            print("   ✓ 已启用课程检测功能")

            # 如果两个功能都启用，设置课程检测回调
            if self.feature_switches['enable_clicker']:
                print("   ⚠  注意：课程检测到目标时会自动停止鼠标连点")
        else:
            self.feature_switches['enable_course_monitor'] = False
            print("   ✗ 不启用课程检测功能")

        print("\n" + "=" * 60)

        # 如果没有启用任何功能，退出
        if not (self.feature_switches['enable_clicker'] or
                self.feature_switches['enable_course_monitor']):
            print("未启用任何功能，程序退出")
            return False

        return True

    def setup_clicker(self):
        """设置鼠标连点功能 - 只设置位置，不启动"""
        print("\n" + "=" * 60)
        print("鼠标连点功能设置")
        print("=" * 60)

        print(f"当前点击间隔: {self.clicker_config['click_interval']}秒")
        print("提示：如需修改点击间隔，请在 config.py 中调整 CLICKER_CONFIG['click_interval']")
        print("-" * 40)

        # 创建点击器实例
        self.clicker = ContinuousClicker(self.clicker_config)

        # 设置点击位置（不启动）
        print("\n请设置点击位置：")
        position = self.clicker.get_click_position()
        if position:
            print(f"   点击位置已设置: {position}")
            print("   注意：连点将在功能启动后开始")
            return True
        else:
            print("   点击位置设置失败")
            return False

    def setup_course_monitor(self):
        """设置课程检测功能"""
        print("\n" + "=" * 60)
        print("课程检测功能设置")
        print("=" * 60)

        # 显示当前关键词（用户应直接修改config.py文件）
        keywords_str = ", ".join(self.course_config['keywords'])
        print(f"监控关键词: {keywords_str}")
        print("提示：如需修改关键词，请直接编辑 config.py 文件中的 COURSE_MONITOR_CONFIG['keywords']")
        print("-" * 40)

        # 创建课程检测器实例 - 这里的关键是正确传递回调函数
        if self.feature_switches['enable_clicker']:
            # 如果启用了点击器，设置回调函数
            self.course_config['on_target_detected'] = self.on_course_detected
        else:
            self.course_config['on_target_detected'] = None

        self.course_monitor = CourseMonitor(self.course_config)
        return True

    def on_course_detected(self):
        """课程检测到目标时的回调函数"""
        # 停止鼠标连点
        if self.clicker and self.clicker.is_clicking:
            # 只显示一次停止消息
            if not self.has_shown_stop_message:
                print("\n" + "=" * 60)
                print("⚠️  检测到目标课程，正在停止鼠标连点...")
                print("=" * 60)
                self.has_shown_stop_message = True

            self.clicker.stop_clicking()

    def run_features(self):
        """运行启用的功能"""
        print("\n" + "=" * 60)
        print("启动功能")
        print("=" * 60)

        # 重置停止消息标记
        self.has_shown_stop_message = False

        # 如果启用了课程检测，先启动课程检测
        if self.feature_switches['enable_course_monitor'] and self.course_monitor:
            print("启动课程检测功能...")
            self.course_monitor.start_monitoring()
            print("✓ 课程检测已启动")

            # 如果同时启用了鼠标连点，在课程检测启动后启动它
            if self.feature_switches['enable_clicker'] and self.clicker:
                print("\n正在启动鼠标连点功能...")
                # 注意：这里直接调用点击器的内部方法，而不是start_clicking（避免重复设置位置）
                if not self.clicker.is_clicking:
                    self.clicker.is_clicking = True
                    # 在新线程中启动点击循环
                    self.clicker.click_thread = threading.Thread(target=self.clicker.click_loop)
                    self.clicker.click_thread.daemon = True
                    self.clicker.click_thread.start()
                    print("✓ 鼠标连点已启动")

        # 如果只启用了鼠标连点，没有启用课程检测
        elif self.feature_switches['enable_clicker'] and self.clicker:
            print("启动鼠标连点功能...")
            self.clicker.start_clicking()
            print("✓ 鼠标连点已启动")

        print("\n✅ 所有启用的功能已启动！")
        print("=" * 60)
        print("控制提示:")

        if self.feature_switches['enable_clicker']:
            print("  - 鼠标连点: 按 Ctrl+Alt+C 停止")

        if self.feature_switches['enable_course_monitor']:
            print("  - 课程检测: 按 Ctrl+S 停止")

        print("  - 退出程序: 按 Ctrl+Alt+Q")
        print("=" * 60 + "\n")

    def start(self):
        """启动应用程序"""
        print("=" * 60)
        print("整合版选课助手 - 课程检测 + 鼠标连点")
        print("=" * 60)

        # 检查依赖
        if not self.check_all_dependencies():
            print("\n缺少必要组件，请运行以下命令安装:")
            print("pip install pyautogui keyboard easyocr opencv-python pillow numpy")
            sys.exit(1)

        # 询问用户启用哪些功能
        if not self.ask_feature_enable():
            return

        # 设置鼠标连点功能
        if self.feature_switches['enable_clicker']:
            if not self.setup_clicker():
                print("鼠标连点功能设置失败")
                return

        # 设置课程检测功能
        if self.feature_switches['enable_course_monitor']:
            if not self.setup_course_monitor():
                print("课程检测功能设置失败")
                return

        # 运行启用的功能
        self.run_features()

        # 设置全局退出快捷键
        keyboard.add_hotkey('ctrl+alt+q', self.quit)

        # 保持程序运行
        try:
            keyboard.wait()
        except KeyboardInterrupt:
            self.quit()

    def quit(self):
        """安全退出程序"""
        print("\n" + "=" * 60)
        print("正在退出整合版选课助手...")

        # 停止鼠标连点
        if self.clicker and self.clicker.is_clicking:
            self.clicker.stop_clicking()
            print("✓ 鼠标连点已停止")

        # 停止课程检测
        if self.course_monitor and self.course_monitor.is_monitoring:
            self.course_monitor.stop_monitoring()
            print("✓ 课程检测已停止")

        time.sleep(1)
        print("\n感谢使用！")
        print("=" * 60)
        sys.exit(0)


def main():
    """主函数 - 程序入口"""
    app = IntegratedApp()
    app.start()


if __name__ == "__main__":
    main()