import json
import os
import sys

from PySide6.QtCore import Qt, QTimer, Signal, QPoint, QTime, QDate
from PySide6.QtGui import QIcon, QPixmap, QDrag, QMouseEvent, QAction
from PySide6.QtWidgets import (QApplication, QMainWindow, QSplitter,
                               QListWidget, QWidget, QVBoxLayout, QPushButton,
                               QListWidgetItem, QStatusBar, QDialog, QFormLayout,
                               QLineEdit, QSpinBox, QHBoxLayout, QFileDialog, QLabel,
                               QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QTimeEdit, QAbstractItemView, QSystemTrayIcon, QMenu, QCheckBox)


class DeleteConfirmationDialog(QMessageBox):
    def __init__(self, program_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("删除确认")
        self.setText(f"确定要删除程序 '{program_name}' 吗？")
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        self.button(QMessageBox.Yes).setText("确定")
        self.button(QMessageBox.No).setText("取消")
        self.setDefaultButton(QMessageBox.No)
        self.setIcon(QMessageBox.Question)

class AddProgramDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加程序")
        
        # 设置无边框窗口
        self.setWindowFlag(Qt.FramelessWindowHint)
        
        # 创建自定义标题栏
        self.create_custom_title_bar()
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 添加自定义标题栏
        main_layout.addWidget(self.title_bar)
        
        # 表单布局容器
        form_container = QWidget()
        self.layout = QFormLayout()
        self.layout.setContentsMargins(30, 30, 30, 30)  # 增加内边距
        self.layout.setSpacing(20)  # 增加控件间距
        
        # 程序名称输入
        self.name_edit = QLineEdit()
        self.layout.addRow("程序名称:", self.name_edit)

        # 程序路径输入
        self.path_edit = QLineEdit()
        self.browse_btn = QPushButton("浏览")
        self.browse_btn.setFixedWidth(80)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.browse_btn)
        
        self.layout.addRow("程序路径:", path_layout)

        # 延迟时间输入
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(0, 3600)
        self.delay_spin.setValue(0)
        self.layout.addRow("延迟时间(秒):", self.delay_spin)

        # 错误提示
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: red;")
        self.layout.addRow(self.error_label)

        # 按钮
        self.button_box = QHBoxLayout()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        
        ok_btn.clicked.connect(self.validate_and_accept)
        cancel_btn.clicked.connect(self.reject)
        
        self.button_box.addStretch()
        self.button_box.addWidget(ok_btn)
        self.button_box.addWidget(cancel_btn)
        self.layout.addRow(self.button_box)

        # 将表单布局添加到主布局
        form_container.setLayout(self.layout)
        main_layout.addWidget(form_container)

        # 事件连接
        self.browse_btn.clicked.connect(self.browse_path)
        
        # 设置对话框尺寸
        self.resize(400, 300)  # 设置固定尺寸

    def create_custom_title_bar(self):
        # 创建自定义标题栏
        self.title_bar = QWidget()
        self.title_bar.setObjectName("dialogTitleBar")
        self.title_bar.setFixedHeight(36)
        
        # 标题栏布局
        title_layout = QHBoxLayout()
        title_layout.setSpacing(0)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题标签
        self.title_label = QLabel("添加程序")
        self.title_label.setObjectName("dialogTitle")
        self.title_label.setAlignment(Qt.AlignCenter)
        
        # 标题栏按钮容器
        button_container = QWidget()
        button_container.setFixedWidth(40)
        
        # 标题栏按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(0)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # 关闭按钮
        close_btn = QPushButton("×")
        close_btn.setObjectName("dialogCloseButton")
        close_btn.setFixedSize(36, 36)
        close_btn.clicked.connect(self.reject)
        
        # 添加到布局
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        
        button_layout.addWidget(close_btn)
        button_container.setLayout(button_layout)
        
        title_layout.addWidget(button_container)
        
        self.title_bar.setLayout(title_layout)
        
        # 用于拖动窗口
        self.drag_position = QPoint()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def browse_path(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择程序")
        if path:
            self.path_edit.setText(path)

    def validate_and_accept(self):
        path = self.path_edit.text()
        if not path or not os.path.exists(path):
            self.error_label.setText("程序路径不存在，请重新选择")
            return
            
        if not self.name_edit.text().strip():
            self.error_label.setText("程序名称不能为空")
            return

        self.error_label.setText("")
        self.accept()

    def get_data(self):
        return (
            self.name_edit.text(),
            self.path_edit.text(),
            str(self.delay_spin.value())
        )

class EditProgramDialog(QDialog):
    def __init__(self, name, path, delay, parent=None):
        super().__init__(parent)
        self.setWindowTitle("编辑程序")
        
        # 设置无边框窗口
        self.setWindowFlag(Qt.FramelessWindowHint)
        
        # 创建自定义标题栏
        self.create_custom_title_bar()
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 添加自定义标题栏
        main_layout.addWidget(self.title_bar)
        
        # 表单布局容器
        form_container = QWidget()
        self.layout = QFormLayout()
        self.layout.setContentsMargins(30, 30, 30, 30)  # 增加内边距
        self.layout.setSpacing(20)  # 增加控件间距
        
        # 程序名称输入
        self.name_edit = QLineEdit(name)
        self.layout.addRow("程序名称:", self.name_edit)

        # 程序路径输入
        self.path_edit = QLineEdit(path)
        self.browse_btn = QPushButton("浏览")
        self.browse_btn.setFixedWidth(80)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.browse_btn)
        
        self.layout.addRow("程序路径:", path_layout)

        # 延迟时间输入
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(0, 3600)
        self.delay_spin.setValue(int(delay))
        self.layout.addRow("延迟时间(秒):", self.delay_spin)

        # 按钮
        self.button_box = QHBoxLayout()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        self.button_box.addStretch()
        self.button_box.addWidget(ok_btn)
        self.button_box.addWidget(cancel_btn)
        self.layout.addRow(self.button_box)

        # 将表单布局添加到主布局
        form_container.setLayout(self.layout)
        main_layout.addWidget(form_container)

        # 事件连接
        self.browse_btn.clicked.connect(self.browse_path)
        
        # 设置对话框尺寸
        self.resize(400, 300)  # 设置固定尺寸

    def create_custom_title_bar(self):
        # 创建自定义标题栏
        self.title_bar = QWidget()
        self.title_bar.setObjectName("dialogTitleBar")
        self.title_bar.setFixedHeight(36)
        
        # 标题栏布局
        title_layout = QHBoxLayout()
        title_layout.setSpacing(0)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题标签
        self.title_label = QLabel("编辑程序")
        self.title_label.setObjectName("dialogTitle")
        self.title_label.setAlignment(Qt.AlignCenter)
        
        # 标题栏按钮容器
        button_container = QWidget()
        button_container.setFixedWidth(40)
        
        # 标题栏按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(0)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # 关闭按钮
        close_btn = QPushButton("×")
        close_btn.setObjectName("dialogCloseButton")
        close_btn.setFixedSize(36, 36)
        close_btn.clicked.connect(self.reject)
        
        # 添加到布局
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        
        button_layout.addWidget(close_btn)
        button_container.setLayout(button_layout)
        
        title_layout.addWidget(button_container)
        
        self.title_bar.setLayout(title_layout)
        
        # 用于拖动窗口
        self.drag_position = QPoint()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def browse_path(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择程序")
        if path:
            self.path_edit.setText(path)

    def get_data(self):
        return (
            self.name_edit.text(),
            self.path_edit.text(),
            str(self.delay_spin.value())
        )

class ProgramTableWidget(QTableWidget):
    itemDropped = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QTableWidget.InternalMove)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setDropIndicatorShown(True)
        
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(["程序名称", "延迟 (秒)"])
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.verticalHeader().setVisible(False) # 隐藏行号
        
        # 允许行拖放
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropOverwriteMode(False)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setEditTriggers(QTableWidget.NoEditTriggers) # 禁止编辑


    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if os.path.isfile(file_path) and file_path.endswith('.exe'):
                    name = os.path.basename(file_path)
                    self.add_program_item(name, file_path, "0")
            event.acceptProposedAction()
            self.itemDropped.emit()
            return

        if not (isinstance(event.source(), ProgramTableWidget) and event.source() is self):
            return

        source_row = self.currentRow()
        target_index = self.indexAt(event.position().toPoint())
        target_row = target_index.row()

        indicator = self.dropIndicatorPosition()
        if target_row == -1:
            if indicator == QAbstractItemView.DropIndicatorPosition.OnViewport:
                target_row = self.rowCount()
        elif indicator == QAbstractItemView.DropIndicatorPosition.BelowItem:
            target_row += 1

        if source_row == target_row or source_row + 1 == target_row:
            return

        self.blockSignals(True)
        
        taken_items = []
        for i in range(self.columnCount()):
            taken_items.append(self.takeItem(source_row, i))

        self.removeRow(source_row)
        
        if source_row < target_row:
            target_row -= 1
            
        self.insertRow(target_row)
        for i, item in enumerate(taken_items):
            self.setItem(target_row, i, item)
            
        self.blockSignals(False)
        self.setCurrentCell(target_row, 0)
        self.itemDropped.emit()

    def add_program_item(self, name, path, delay):
        row_position = self.rowCount()
        self.insertRow(row_position)
        
        name_item = QTableWidgetItem(name)
        name_item.setData(Qt.UserRole, path) # 将路径存在第一个单元格的 UserRole 中
        
        delay_item = QTableWidgetItem(str(delay))
        delay_item.setTextAlignment(Qt.AlignCenter)

        self.setItem(row_position, 0, name_item)
        self.setItem(row_position, 1, delay_item)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FastStart")
        
        # 设置应用程序图标
        self.setWindowIcon(QIcon('assets/images/app.png'))
        
        # 创建自定义标题栏
        self.create_title_bar()
        
        # 获取屏幕尺寸
        screen = QApplication.primaryScreen().geometry()
        window_width = 800
        window_height = 600
        x = (screen.width() - window_width) // 2
        y = (screen.height() - window_height) // 2
        self.setGeometry(x, y, window_width, window_height)
        
        # 加载样式表
        self.load_stylesheet()
        
        # 创建主窗口容器
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 创建水平分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧面板（支持拖放）
        self.left_panel = ProgramTableWidget()
        # self.left_panel.itemChanged.connect(self.save_programs) # QTableWidget 没有 itemChanged 信号，拖放后由 itemDropped 触发保存
        # 绑定双击事件
        self.left_panel.itemDoubleClicked.connect(self.edit_selected_program)
        # 绑定拖放完成信号
        self.left_panel.itemDropped.connect(self.save_programs)
        
        # 右侧按钮面板
        right_button_panel = QWidget()
        right_layout = QVBoxLayout()
        
        # 新增：顶部启动按钮
        launch_btn = QPushButton("启动程序")
        launch_btn.setFixedHeight(40)
        launch_btn.clicked.connect(self.launch_all_programs)
        
        add_btn = QPushButton("添加程序")
        edit_btn = QPushButton("编辑程序")
        delete_btn = QPushButton("删除程序")
        
        # 设置按钮固定高度
        add_btn.setFixedHeight(40)
        edit_btn.setFixedHeight(40)
        delete_btn.setFixedHeight(40)
        
        # 添加按钮到布局（按垂直顺序）
        right_layout.addWidget(launch_btn)
        right_layout.addWidget(add_btn)
        right_layout.addWidget(edit_btn)
        right_layout.addWidget(delete_btn)
        
        # 添加定时启动控件
        right_layout.addStretch() # 添加一个伸缩项
        
        # 添加“启动后退出”复选框
        self.exit_after_launch_checkbox = QCheckBox("启动完成后退出")
        right_layout.addWidget(self.exit_after_launch_checkbox)

        self.schedule_time_edit = QTimeEdit(QTime.currentTime())
        self.schedule_time_edit.setDisplayFormat("HH:mm")
        self.schedule_time_edit.setFixedHeight(40)
        right_layout.addWidget(self.schedule_time_edit)
        
        self.schedule_btn = QPushButton("启用定时启动")
        self.schedule_btn.setFixedHeight(40)
        right_layout.addWidget(self.schedule_btn)
        
        
        # 设置间距和边距
        right_layout.setSpacing(20)
        right_layout.setContentsMargins(20, 20, 20, 20)
        
        right_button_panel.setLayout(right_layout)
        
        # 添加到分割器
        splitter.addWidget(self.left_panel)
        splitter.addWidget(right_button_panel)
        
        # 设置默认分割比例
        splitter.setSizes([600, 200])
        
        # 主布局
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加自定义标题栏
        layout.addWidget(self.title_bar)
        
        # 添加分割器
        layout.addWidget(splitter)
        
        # 添加状态栏
        self.statusBar = QStatusBar()
        self.statusBar.setFixedHeight(35)  # 从默认高度调整为32px
        self.setStatusBar(self.statusBar)

        # 在状态栏右侧添加定时启动状态标签
        self.status_schedule_label = QLabel("定时启动: 禁用")
        self.statusBar.addPermanentWidget(self.status_schedule_label)

        # 绑定按钮和复选框的点击事件
        add_btn.clicked.connect(self.add_program)
        edit_btn.clicked.connect(self.edit_selected_program)
        delete_btn.clicked.connect(self.delete_selected_program)
        self.schedule_btn.clicked.connect(self.toggle_schedule)
        self.exit_after_launch_checkbox.stateChanged.connect(self.save_programs)
        
        # 设置窗口标志
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        
        # 初始化置顶状态
        self.is_pinned = False
        
        # 初始化定时启动状态
        self.is_schedule_enabled = False
        self.scheduled_launch_triggered_today = False
        self.last_check_date = QDate.currentDate()
        
        # 创建用于检查计划的定时器
        self.schedule_timer = QTimer(self)
        self.schedule_timer.timeout.connect(self.check_schedule)
        self.schedule_timer.start(5000) # 每5秒检查一次
        
        self.load_programs()
        
        # 初始化系统托盘图标
        self.create_tray_icon()

    def create_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon('assets/images/app.png'))
        
        show_action = QAction("显示", self)
        quit_action = QAction("退出", self)
        
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(QApplication.quit)
        
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # 连接双击事件
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.showNormal()

    def create_title_bar(self):
        # 创建自定义标题栏
        self.title_bar = QWidget()
        self.title_bar.setObjectName("customTitleBar")
        self.title_bar.setFixedHeight(36)
        
        # 标题栏布局
        title_layout = QHBoxLayout()
        title_layout.setSpacing(0)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        # 应用程序图标
        self.title_icon = QLabel()
        self.title_icon.setObjectName("titleIcon")
        
        # 加载图标
        try:
            from PySide6.QtGui import QPixmap
            icon = QPixmap('assets/images/app.png')
            self.title_icon.setPixmap(icon.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except Exception as e:
            print(f"加载图标失败: {str(e)}")
            self.title_icon.setText("F")
            self.title_icon.setStyleSheet("color: #ffffff; font-size: 18px; font-weight: bold;")
        
        self.title_icon.setFixedWidth(36)
        self.title_icon.setFixedHeight(36)
        self.title_icon.setAlignment(Qt.AlignCenter)
        
        # 应用名称标签
        self.title_label = QLabel("FastStart")
        self.title_label.setStyleSheet("color: #ffffff; font-size: 16px; font-weight: bold;")
        self.title_label.setFixedHeight(36)
        self.title_label.setAlignment(Qt.AlignCenter)
        
        # 创建窗口置顶按钮
        self.pin_button = QPushButton()
        self.pin_button.setObjectName("pinButton")
        self.pin_button.setFixedSize(36, 36)
        self.pin_button.setCheckable(True)
        self.pin_button.setChecked(False)
        self.pin_button.clicked.connect(self.toggle_pin)
        
        # 加载置顶图标
        try:
            from PySide6.QtGui import QPixmap
            pin_icon = QPixmap('assets/images/pin.png')
            if pin_icon.isNull():
                raise Exception("图片加载失败或为空")
            self.pin_button.setIcon(QIcon(pin_icon))
            self.pin_button.setIconSize(pin_icon.size())
        except Exception as e:
            print(f"加载置顶图标失败: {str(e)}")
            # 优雅降级：使用文字图标
            self.pin_button.setText("📌")
            self.pin_button.setStyleSheet("font-size: 18px; font-weight: bold;")
            # 显示友好提示
            self.statusBar.showMessage("置顶图标加载失败，请检查assets/images/pin.png是否存在", 5000)
        
        # 创建最小化按钮
        self.minimize_button = QPushButton("—")
        self.minimize_button.setObjectName("minimizeButton")
        self.minimize_button.setFixedSize(36, 36)
        self.minimize_button.clicked.connect(self.hide) # 点击时隐藏窗口

        # 创建关闭按钮容器
        close_button_container = QWidget()
        close_button_container.setFixedWidth(36)
        
        # 关闭按钮布局
        close_button_layout = QHBoxLayout()
        close_button_layout.setContentsMargins(0, 0, 0, 0)
        close_button_layout.setSpacing(0)
        
        # 创建关闭按钮
        close_btn = QPushButton("×")
        close_btn.setObjectName("titleBarButtons")
        close_btn.setFixedSize(36, 36)
        close_btn.setStyleSheet("font-size: 18px; font-weight: bold;")
        close_btn.clicked.connect(QApplication.quit)
        
        # 添加到关闭按钮布局
        close_button_layout.addWidget(close_btn, alignment=Qt.AlignCenter)
        close_button_container.setLayout(close_button_layout)
        
        # 添加到标题栏布局（保持正确顺序）
        title_layout.addWidget(self.title_icon)  # 图标在最左边
        title_layout.addWidget(self.title_label)  # 标题在中间
        title_layout.addStretch()  # 伸展空间推到右边
        title_layout.addWidget(self.pin_button)  # 置顶按钮
        title_layout.addWidget(self.minimize_button) # 最小化按钮
        title_layout.addWidget(close_button_container)  # 关闭按钮容器在最右边
        
        self.title_bar.setLayout(title_layout)
        
        # 用于拖动窗口
        self.drag_position = QPoint()

    def toggle_pin(self):
        # 切换窗口置顶状态
        self.is_pinned = not self.is_pinned
        
        # 获取当前窗口标志
        flags = self.windowFlags()
        
        # 切换置顶标志
        if self.is_pinned:
            self.setWindowFlags(flags | Qt.WindowStaysOnTopHint)
            self.pin_button.setChecked(True)  # 使用按钮的checked状态代替直接样式设置
        else:
            self.setWindowFlags(flags & ~Qt.WindowStaysOnTopHint)
            self.pin_button.setChecked(False)  # 使用按钮的checked状态代替直接样式设置
        
        # 重新设置窗口
        self.show()  # 必须调用show()使窗口标志生效
        
        # 更新状态栏提示
        self.statusBar.showMessage("窗口置顶: " + ("开启" if self.is_pinned else "关闭"), 2000)
        
        # 保持原有的拖动窗口功能
        self.create_title_bar()  # 重新创建标题栏以保持原有功能正常

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def load_stylesheet(self):
        try:
            with open('assets/styles/faststart.qss', 'r', encoding='utf-8') as f:
                stylesheet = f.read()
                self.setStyleSheet(stylesheet)
        except FileNotFoundError:
            print("样式表文件未找到，使用默认样式")
        except Exception as e:
            print(f"加载样式表失败: {str(e)}")

    def load_programs(self):
        try:
            with open('start.json', 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                self.left_panel.setRowCount(0) # 清空表格

                programs = []
                # 兼容旧格式 (list) 和新格式 (dict)
                if isinstance(config_data, dict):
                    programs = config_data.get('programs', [])
                    # 加载“启动后退出”设置
                    self.exit_after_launch_checkbox.setChecked(config_data.get('exit_after_launch', False))
                    
                    schedule_data = config_data.get('schedule', {})
                    self.is_schedule_enabled = schedule_data.get('enabled', False)
                    if self.is_schedule_enabled:
                        time_str = schedule_data.get('time', '00:00:00')
                        self.schedule_time_edit.setTime(QTime.fromString(time_str, 'HH:mm:ss'))
                    self.update_schedule_ui()
                elif isinstance(config_data, list):
                    programs = config_data

                for item_data in programs:
                    name = item_data['name']
                    path = item_data['path']
                    delay = str(item_data.get('deply', 0))
                    self.left_panel.add_program_item(name, path, delay)
        except FileNotFoundError:
            pass

    def save_programs(self):
        programs = []
        for i in range(self.left_panel.rowCount()):
            name_item = self.left_panel.item(i, 0)
            delay_item = self.left_panel.item(i, 1)

            # 添加健壮性检查，防止在拖动过程中出现空项
            if not name_item or not delay_item:
                continue
            
            name = name_item.text()
            path = name_item.data(Qt.UserRole)
            delay = delay_item.text() or "0"
            
            try:
                delay_int = int(delay)
            except (ValueError, TypeError):
                delay_int = 0
            
            programs.append({
                "name": name,
                "path": path,
                "deply": delay_int
            })
        
        config_data = {
            "programs": programs,
            "exit_after_launch": self.exit_after_launch_checkbox.isChecked(),
            "schedule": {
                "enabled": self.is_schedule_enabled,
                "time": self.schedule_time_edit.time().toString('HH:mm:ss')
            }
        }
        with open('start.json', 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)
        # 显示保存状态
        self.statusBar.showMessage("配置已保存", 2000)

    def add_program(self):
        dialog = AddProgramDialog(self)
        if dialog.exec() == QDialog.Accepted:
            # 获取输入数据
            name, path, delay = dialog.get_data()
            
            self.left_panel.add_program_item(name, path, delay)
            self.save_programs()
            self.statusBar.showMessage(f"已添加程序: {name}", 3000)

    def edit_selected_program(self, item=None):
        current_row = self.left_panel.currentRow()
        if current_row < 0:
            self.statusBar.showMessage("请先选择要编辑的程序", 3000)
            return

        # 获取当前程序信息
        name_item = self.left_panel.item(current_row, 0)
        delay_item = self.left_panel.item(current_row, 1)

        name = name_item.text()
        path = name_item.data(Qt.UserRole)
        delay = delay_item.text() or "0"
        
        # 创建编辑对话框
        dialog = EditProgramDialog(name, path, delay, self)
        if dialog.exec() == QDialog.Accepted:
            # 获取更新后的数据
            new_name, new_path, new_delay = dialog.get_data()
            
            # 验证路径是否存在
            if not os.path.exists(new_path):
                self.statusBar.showMessage("程序路径不存在，请重新选择", 5000)
                return

            # 更新列表项
            name_item.setText(new_name)
            name_item.setData(Qt.UserRole, new_path)
            delay_item.setText(new_delay)
            
            # 保存更新
            self.save_programs()
            self.statusBar.showMessage("程序信息已更新", 3000)

    def delete_selected_program(self):
        current_row = self.left_panel.currentRow()
        if current_row < 0:
            self.statusBar.showMessage("请先选择要删除的程序", 3000)
            return

        # 显示删除确认对话框
        program_name = self.left_panel.item(current_row, 0).text()
        dialog = DeleteConfirmationDialog(program_name, self)
        if dialog.exec() == QMessageBox.Yes:
            # 从列表中移除
            self.left_panel.removeRow(current_row)
            # 保存更新
            self.save_programs()
            self.statusBar.showMessage("程序已删除", 3000)

    def launch_selected_program(self, item):
        current_row = self.left_panel.currentRow()
        if current_row >= 0:
            program_path = self.left_panel.item(current_row, 0).data(Qt.UserRole)
            if os.path.exists(program_path):
                os.startfile(program_path)  # Windows系统
            else:
                self.statusBar.showMessage(f"程序路径不存在: {program_path}", 5000)

    def launch_all_programs(self):
        self.current_index = 0
        self.statusBar.showMessage("启动中... 准备开始")
        QTimer.singleShot(1000, self.launch_next_program)  # 初始延迟1秒

    def launch_next_program(self):
        if self.current_index >= self.left_panel.rowCount():
            self.current_index = 0
            self.statusBar.showMessage("全部启动完成", 3000)
            if self.exit_after_launch_checkbox.isChecked():
                QTimer.singleShot(1000, QApplication.quit) # 延迟1秒退出，让用户看到状态信息
            return

        name_item = self.left_panel.item(self.current_index, 0)
        delay_item = self.left_panel.item(self.current_index, 1)

        program_path = name_item.data(Qt.UserRole)
        program_name = name_item.text()
        delay = delay_item.text() or "0"
        
        try:
            deply_int = int(delay)
        except (ValueError, TypeError):
            deply_int = 0
        
        if deply_int < 0:
            deply_int = 0

        if os.path.exists(program_path):
            self.statusBar.showMessage(f"正在启动: {program_name} (延迟{deply_int}秒)")
            QTimer.singleShot(deply_int * 1000, lambda p=program_path: (
                os.startfile(p),
                setattr(self, 'current_index', self.current_index + 1),
                self.launch_next_program()
            ))
        else:
            self.statusBar.showMessage(f"程序路径不存在: {program_path}", 5000)
            self.current_index += 1
            self.launch_next_program()

    def toggle_schedule(self):
        self.is_schedule_enabled = not self.is_schedule_enabled
        self.update_schedule_ui()
        self.save_programs()

    def update_schedule_ui(self):
        if self.is_schedule_enabled:
            self.schedule_btn.setText("禁用定时启动")
            self.status_schedule_label.setText(f"定时启动: {self.schedule_time_edit.time().toString('HH:mm')}")
        else:
            self.schedule_btn.setText("启用定时启动")
            self.status_schedule_label.setText("定时启动: 禁用")

    def check_schedule(self):
        current_date = QDate.currentDate()
        if self.last_check_date != current_date:
            self.scheduled_launch_triggered_today = False
            self.last_check_date = current_date

        if not self.is_schedule_enabled or self.scheduled_launch_triggered_today:
            return

        current_time = QTime.currentTime()
        scheduled_time = self.schedule_time_edit.time()

        if current_time.hour() == scheduled_time.hour() and current_time.minute() == scheduled_time.minute():
            self.launch_all_programs()
            self.scheduled_launch_triggered_today = True
            # 定时启动完成后，禁用并更新UI
            self.is_schedule_enabled = False
            self.update_schedule_ui()
            self.save_programs()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())