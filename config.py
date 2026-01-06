# config.py
# 配置文件 - 统一管理课程检测和鼠标连点的配置参数

# ==================== 课程检测配置 ====================
COURSE_MONITOR_CONFIG = {
    # 监控关键词
    'keywords': [
        "多媒体技术",
        "机器学习",
        "Python",
        "代数式代码和AI框架"
    ],

    # 性能优化设置
    'image_scale': 0.8,  # 图像缩放比例: 0.5 = 50%
    'check_interval': 1.0,  # 检查间隔: 1.0秒
    'alert_cooldown': 2,  # 提醒冷却时间: 2秒

    # 其他设置
    'status_interval': 30,  # 状态显示间隔: 30秒
    'use_gpu': False,  # 是否使用GPU加速(需要NVIDIA显卡)
    'verbose': True,  # 是否显示详细输出信息
}

# ==================== 鼠标连点配置 ====================
CLICKER_CONFIG = {
    # 点击参数
    'click_interval': 2.0,  # 点击间隔: 2.0秒
    'click_duration': 0.1,  # 点击持续时间: 0.1秒
    'click_count': None,  # 点击次数: None=无限
    'click_button': 'left',  # 点击按钮: 'left'(左键), 'right'(右键), 'middle'(中键)

    # 显示设置
    'verbose': True,  # 显示详细输出
    'show_mouse_position': True,  # 启动时显示鼠标位置
}

# ==================== 功能开关 (默认值) ====================
FEATURE_SWITCHES = {
    'enable_course_monitor': False,  # 是否启用课程检测
    'enable_clicker': False,  # 是否启用鼠标连点
}