# course_monitor.py
import pyautogui
import time
import threading
import keyboard
import sys
import cv2
import numpy as np
from PIL import ImageGrab
import easyocr


class CourseMonitor:
    """
    选课监控核心类
    功能：仅监控指定屏幕区域，识别指定文字关键词并声音提醒
    """

    def __init__(self, config):
        """
        初始化监控器

        参数:
        config: 配置字典，包含所有监控参数
        """
        self.is_monitoring = False
        self.config = config
        self.reader = None

        # 从配置中获取参数
        self.keywords = config.get('keywords', ["模式识别", "机器学习", "Python", "深度学习"])
        self.image_scale = config.get('image_scale', 0.7)
        self.check_interval = config.get('check_interval', 0.2)
        self.status_interval = config.get('status_interval', 30)
        self.alert_cooldown = config.get('alert_cooldown', 1)
        self.use_gpu = config.get('use_gpu', False)
        self.verbose = config.get('verbose', True)

        # 关键修复：保存回调函数
        self.callback_function = config.get('on_target_detected', None)

        self.init_ocr_simple()
        if self.verbose:
            self.print_config()

    def print_config(self):
        """打印配置信息"""
        print("\n" + "=" * 60)
        print("选课监控助手 - 区域文字检测版")
        print("=" * 60)
        print(f"监控关键词: {', '.join(self.keywords)}")
        print(f"优化设置: 图像缩放{self.image_scale * 100}%, 检查间隔{self.check_interval}秒")
        print(f"提醒冷却: {self.alert_cooldown}秒, GPU加速: {'是' if self.use_gpu else '否'}")
        print("快捷键说明:")
        print("  Ctrl+S = 开始/停止监控")
        print("  Ctrl+Q = 退出程序")
        print("-" * 60)
        print("提示：程序启动后，按 Ctrl+S 开始设置监控区域")
        print("=" * 60 + "\n")

    def init_ocr_simple(self):
        """初始化OCR识别器 - 极简兼容版"""
        if self.verbose:
            print("正在初始化OCR识别器...")
        try:
            self.reader = easyocr.Reader(
                lang_list=['ch_sim', 'en'],
                gpu=self.use_gpu,
            )
            if self.verbose:
                print("✓ OCR识别器初始化成功")
            return True
        except Exception as e:
            print(f"✗ OCR初始化失败: {e}")
            self.handle_ocr_error(e)
            return False

    def handle_ocr_error(self, error):
        """处理OCR初始化错误"""
        print("\n" + "=" * 50)
        print("OCR初始化问题解决方案：")
        print("1. 确保easyocr正确安装: pip install easyocr")
        print("2. 如果仍有问题，尝试安装稳定版本:")
        print("   pip install easyocr==1.7.0  # 稳定版本")
        print("3. 或者完全卸载重装:")
        print("   pip uninstall easyocr -y")
        print("   pip install easyocr")
        print("=" * 50)
        self.reader = None  # 修复：这行必须在方法内部

    def play_beep_sound(self):
        """发出声音提醒 (Windows系统)"""
        try:
            import winsound
            frequencies = [1000, 1500]
            for freq in frequencies:
                winsound.Beep(freq, 150)
                time.sleep(0.03)
            return True
        except:
            if self.verbose:
                print("\a\a")
            return False

    def capture_region(self, region):
        """截取指定屏幕区域 - 优化版"""
        try:
            left, top, right, bottom = region

            if right <= left or bottom <= top:
                if self.verbose:
                    print(f"无效区域: {region}")
                return None

            screenshot = ImageGrab.grab(bbox=region)
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            # 图像预处理优化
            if self.image_scale < 1.0:
                height, width = screenshot_cv.shape[:2]
                new_width = int(width * self.image_scale)
                new_height = int(height * self.image_scale)
                screenshot_cv = cv2.resize(screenshot_cv, (new_width, new_height),
                                           interpolation=cv2.INTER_AREA)

            screenshot_cv = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)

            if self.image_scale < 0.9:
                kernel = np.array([[0, -0.25, 0],
                                   [-0.25, 2.0, -0.25],
                                   [0, -0.25, 0]])
                screenshot_cv = cv2.filter2D(screenshot_cv, -1, kernel)

            return screenshot_cv
        except Exception as e:
            if self.verbose:
                print(f"[错误] 截屏失败: {e}")
            return None

    def recognize_text_safe(self, image):
        """安全地识别图像中的文字"""
        if self.reader is None:
            if self.verbose:
                print("OCR识别器未初始化")
            return []

        try:
            results = self.reader.readtext(image)
            texts = []
            for result in results:
                if len(result) >= 2:
                    text = result[1]
                    texts.append(text)
            return texts
        except Exception as e:
            if self.verbose:
                print(f"[错误] 文字识别失败: {e}")
            return []

    def check_keywords(self, texts):
        """检查是否包含监控关键词"""
        found = []
        for text in texts:
            for keyword in self.keywords:
                if keyword in text:
                    found.append(keyword)
        return list(set(found))

    def setup_monitoring_region(self):
        """引导用户设置监控区域"""
        if self.verbose:
            print("\n" + "=" * 60)
            print("步骤1: 设置监控区域")
            print("=" * 60)

        try:
            if self.verbose:
                print("请将鼠标移动到监控区域的【左上角】")
                print("移动到位后，请按 【Enter】 键确认")
            input("等待确认..." if self.verbose else "")
            x1, y1 = pyautogui.position()
            if self.verbose:
                print(f"✅ 左上角坐标已记录: ({x1}, {y1})\n")

            if self.verbose:
                print("请将鼠标移动到监控区域的【右下角】")
                print("移动到位后，请按 【Enter】 键确认")
            input("等待确认..." if self.verbose else "")
            x2, y2 = pyautogui.position()
            if self.verbose:
                print(f"✅ 右下角坐标已记录: ({x2}, {y2})\n")

            left = min(x1, x2)
            top = min(y1, y2)
            right = max(x1, x2)
            bottom = max(y1, y2)

            region = (left, top, right, bottom)
            width = right - left
            height = bottom - top

            if self.verbose:
                print(f"📐 监控区域: {region}")
                print(f"📏 区域尺寸: {width} × {height} 像素\n")

            if width < 50 or height < 20:
                if self.verbose:
                    print("⚠️  警告: 区域过小，可能影响识别效果")
                    choice = input("是否重新设置? (y/n): ")
                    if choice.lower() == 'y':
                        return self.setup_monitoring_region()

            return region

        except Exception as e:
            if self.verbose:
                print(f"设置区域时出错: {e}")
            return None

    def monitor_region(self, region):
        """监控指定区域 - 修复版（解决状态打印频繁和提醒间隔不准确问题）"""
        if self.verbose:
            print("\n" + "=" * 60)
            print("步骤2: 开始监控")
            print("=" * 60)
            print(f"监控区域: {region}")
            print(f"监控关键词: {', '.join(self.keywords)}")
            print(f"优化设置: 图像缩放{self.image_scale * 100}%, 检查间隔{self.check_interval}秒")
            print("-" * 60)
            print("监控已启动！发现关键词时将发出声音提醒。")
            print("按 Ctrl+S 停止监控\n")

        alert_count = 0
        check_count = 0
        last_alert_time = 0
        last_status_time = time.time()

        while self.is_monitoring:
            try:
                check_count += 1
                # 在循环开始时获取准确的时间戳
                loop_start_time = time.time()

                # 状态打印（每30秒一次）
                if loop_start_time - last_status_time > self.status_interval:
                    if self.verbose:
                        time_str = time.strftime("%H:%M:%S")
                        print(f"[{time_str}] 监控中... 检查{check_count}次, 提醒{alert_count}次")
                    last_status_time = loop_start_time

                # 1. 截取指定区域
                screenshot = self.capture_region(region)
                if screenshot is None:
                    time.sleep(self.check_interval)
                    continue

                # 2. 识别文字 (OCR)
                texts = self.recognize_text_safe(screenshot)

                # 3. 检查关键词
                if texts:
                    found_keywords = self.check_keywords(texts)

                    if found_keywords:
                        # 防重复提醒（使用循环开始时的时间戳）
                        if loop_start_time - last_alert_time > self.alert_cooldown:
                            alert_count += 1
                            last_alert_time = loop_start_time

                            self.play_beep_sound()

                            if self.verbose:
                                time_str = time.strftime("%H:%M:%S")
                                print(f"[{time_str}] 提醒{alert_count}: 发现「{', '.join(found_keywords)}」")

                            # 关键修复：调用回调函数
                            if self.callback_function:
                                print("检测到目标课程，正在调用回调函数...")
                                self.callback_function()
                                # 回调函数可能会停止监控，所以检查一下
                                if not self.is_monitoring:
                                    print("回调函数停止了监控，退出监控循环")
                                    break

                # 4. 计算实际耗时，动态调整等待时间
                processing_time = time.time() - loop_start_time
                if processing_time < self.check_interval:
                    time.sleep(self.check_interval - processing_time)
                else:
                    # 如果处理时间超过检查间隔，立即开始下一次检查
                    if self.verbose and processing_time > self.check_interval * 2:
                        print(f"[注意] OCR处理耗时较长: {processing_time:.2f}秒")

            except KeyboardInterrupt:
                if self.verbose:
                    print("\n监控被中断")
                break
            except Exception as e:
                if self.verbose:
                    print(f"[错误] 监控异常: {e}")
                time.sleep(self.check_interval * 2)

    def start_monitoring(self):
        """开始监控流程"""
        if not self.is_monitoring:
            if self.reader is None:
                if self.verbose:
                    print("✗ 无法启动: OCR识别器未初始化")
                return

            if self.verbose:
                print("\n启动区域监控...")
            self.is_monitoring = True

            region = self.setup_monitoring_region()
            if region is None:
                if self.verbose:
                    print("区域设置失败，监控已取消")
                self.is_monitoring = False
                return

            monitor_thread = threading.Thread(
                target=self.monitor_region,
                args=(region,)
            )
            monitor_thread.daemon = True
            monitor_thread.start()

            if self.verbose:
                print("\n✅ 区域监控已启动！")

    def stop_monitoring(self):
        """停止监控"""
        if self.is_monitoring:
            if self.verbose:
                print("\n正在停止监控...")
            self.is_monitoring = False
            time.sleep(1.5)
            if self.verbose:
                print("监控已停止")

    def toggle_monitoring(self):
        """切换监控状态"""
        if self.is_monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()

    def run(self):
        """运行主程序循环"""
        keyboard.add_hotkey('ctrl+s', self.toggle_monitoring)
        keyboard.add_hotkey('ctrl+q', self.quit_program)

        if self.verbose:
            print("程序已就绪，等待快捷键命令...")
            print("提示: 按 Ctrl+S 开始设置监控区域，按 Ctrl+Q 退出程序\n")

        try:
            keyboard.wait()
        except KeyboardInterrupt:
            self.quit_program()

    def quit_program(self):
        """安全退出程序"""
        if self.verbose:
            print("\n" + "=" * 60)
            print("正在退出选课监控助手...")
        self.stop_monitoring()
        time.sleep(0.5)
        if self.verbose:
            print("感谢使用！")
            print("=" * 60)
        sys.exit(0)


def check_dependencies():
    """检查必要的Python库是否已安装"""
    print("检查运行环境...")

    required_modules = [
        ('pyautogui', 'pyautogui'),
        ('keyboard', 'keyboard'),
        ('easyocr', 'easyocr'),
        ('cv2', 'opencv-python'),
        ('PIL', 'Pillow'),
        ('numpy', 'numpy')
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