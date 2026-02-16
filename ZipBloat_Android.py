import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.uix.screenmanager import ScreenManager, Screen
import zipfile
import os
import threading
import shutil
import stat
import logging
from logging.handlers import RotatingFileHandler
import datetime
import sys

kivy.require('2.0.0')

try:
    from android.storage import primary_external_storage_path
    from android.permissions import request_permissions, Permission
    ANDROID = True
except ImportError:
    ANDROID = False


class ZipBloatLogic:
    def __init__(self):
        self.logger = self._init_log()
        self.is_running = False
        self.cancel_flag = False

    def _init_log(self):
        if ANDROID:
            log_dir = os.path.join(primary_external_storage_path(), "ZipBloat", "logs")
        else:
            log_dir = os.path.join(os.path.expanduser("~"), "ZipBloat", "logs")
        
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"zipbloat_{datetime.datetime.now().strftime('%Y%m%d')}.log")

        logger = logging.getLogger("ZipBloat")
        logger.setLevel(logging.INFO)
    
        handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        if not logger.handlers:
            logger.addHandler(handler)

        logger.info("=" * 50)
        logger.info("ZipBloat started")
        logger.info("=" * 50)
        
        return logger

    def check_disk_space(self, path, required_gb):
        try:
            if os.name == 'nt':
                free_bytes = shutil.disk_usage(path).free
            else:
                statvfs = os.statvfs(path)
                free_bytes = statvfs.f_frsize * statvfs.f_bavail
            
            required_bytes = required_gb * 1024 * 1024 * 1024
            return free_bytes >= required_bytes
        except:
            return True

    def generate_empty_block_zip(self, original_path, output_path, target_gb, progress_callback):
        target_size = target_gb * 1024 * 1024 * 1024
        
        try:
            with zipfile.ZipFile(original_path, 'r') as src_zip:
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as dest_zip:
                    for item in src_zip.infolist():
                        if self.cancel_flag:
                            return False
                        dest_zip.writestr(item, src_zip.read(item.filename))
                    
                    block_size = 1024 * 1024
                    empty_data = b'\x00' * block_size
                    current_size = dest_zip.fp.tell()
                    
                    while current_size < target_size:
                        if self.cancel_flag:
                            return False
                        
                        dest_zip.writestr(f'empty_block_{current_size}.bin', empty_data)
                        current_size = dest_zip.fp.tell()
                        
                        progress = min(100, int((current_size / target_size) * 100))
                        progress_callback(progress)
            
            return True
        except Exception as e:
            self.logger.error(f"Empty block method error: {str(e)}")
            return False

    def generate_nested_zip(self, original_path, output_path, target_gb, progress_callback):
        target_size = target_gb * 1024 * 1024 * 1024
        temp_dir = os.path.join(os.path.dirname(output_path), 'temp_nested')
        
        try:
            os.makedirs(temp_dir, exist_ok=True)
            
            with zipfile.ZipFile(original_path, 'r') as src_zip:
                src_zip.extractall(temp_dir)
            
            current_size = os.path.getsize(original_path)
            level = 1
            
            while current_size < target_size:
                if self.cancel_flag:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    return False
                
                temp_zip = os.path.join(temp_dir, f'level_{level}.zip')
                with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as z:
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            if file.endswith('.zip') and file != f'level_{level}.zip':
                                continue
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, temp_dir)
                            z.write(file_path, arcname)
                
                current_size = os.path.getsize(temp_zip)
                level += 1
                
                progress = min(100, int((current_size / target_size) * 100))
                progress_callback(progress)
            
            shutil.copy2(temp_zip, output_path)
            shutil.rmtree(temp_dir, ignore_errors=True)
            return True
        except Exception as e:
            self.logger.error(f"Nested ZIP method error: {str(e)}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False

    def generate_append_junk_zip(self, original_path, output_path, target_gb, progress_callback):
        target_size = target_gb * 1024 * 1024 * 1024
        
        try:
            shutil.copy2(original_path, output_path)
            current_size = os.path.getsize(output_path)
            
            if current_size >= target_size:
                progress_callback(100)
                return True
            
            with open(output_path, 'ab') as f:
                chunk_size = 1024 * 1024
                junk_data = b'\x00' * chunk_size
                
                while current_size < target_size:
                    if self.cancel_flag:
                        return False
                    
                    f.write(junk_data)
                    current_size = f.tell()
                    
                    progress = min(100, int((current_size / target_size) * 100))
                    progress_callback(progress)
            
            return True
        except Exception as e:
            self.logger.error(f"Append junk method error: {str(e)}")
            return False

    def generate_zip_bomb(self, original_path, output_path, target_gb, progress_callback):
        try:
            with zipfile.ZipFile(original_path, 'r') as src_zip:
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=0) as dest_zip:
                    for item in src_zip.infolist():
                        if self.cancel_flag:
                            return False
                        dest_zip.writestr(item, src_zip.read(item.filename))
                    
                    zero_kb = b'\x00' * 1024
                    for i in range(1000000):
                        if self.cancel_flag:
                            return False
                        dest_zip.writestr(f'bomb_{i}.txt', zero_kb)
                        
                        if i % 10000 == 0:
                            progress = min(100, int((i / 1000000) * 100))
                            progress_callback(progress)
            
            progress_callback(100)
            return True
        except Exception as e:
            self.logger.error(f"ZIP bomb method error: {str(e)}")
            return False


class MainScreen(Screen):
    lang_texts = {
        "zh": {
            "title": "ZipBloat - ZIP文件体积放大工具",
            "original_file": "原ZIP文件:",
            "output_file": "输出ZIP文件:",
            "target_size": "目标放大体积 (GB):",
            "size_tip": "建议1-20GB",
            "zoom_method": "放大方式:",
            "empty_block": "添加空块",
            "nest_zip": "嵌套ZIP",
            "append_junk": "尾部追加垃圾数据",
            "zip_bomb": "ZIP炸弹模式",
            "start": "开始生成",
            "cancel": "取消",
            "status_ready": "状态: 就绪",
            "status_running": "状态: 正在生成...",
            "status_canceled": "状态: 已取消",
            "status_completed": "状态: 生成完成！",
            "status_failed": "状态: 生成失败",
            "select_file": "选择文件",
            "select_output": "选择输出路径",
            "err_num": "错误",
            "err_num_msg": "目标体积必须是数字！",
            "err_file_not_exist": "文件不存在！请选择有效的原ZIP文件。",
            "err_file_format": "格式错误！所选文件不是ZIP格式。",
            "err_output_path": "请选择输出文件路径！",
            "err_param": "参数错误！目标体积请设置为0-100GB之间。",
            "success_title": "成功",
            "success_msg": "ZIP文件已生成：",
            "fail_title": "错误",
            "fail_msg": "生成失败：",
            "help_title": "使用说明",
            "help_content": "ZipBloat 使用说明\n\n1. 选择原ZIP文件\n2. 设置输出路径\n3. 设置目标体积(GB)\n4. 选择放大方式\n5. 点击开始生成\n\n注意事项：\n- 目标体积建议1-20GB\n- 生成过程中可以取消\n- 确保输出路径有写入权限",
            "about_title": "关于",
            "about_content": "ZipBloat v1.0\n\n一个简单易用的ZIP文件体积放大工具\n\n作者: Geekline\n官网: geekline.pages.dev\n\n功能特性：\n• 4种放大方式\n• 多语言支持\n• 实时进度显示\n• 支持取消操作\n\n开源协议: MIT"
        },
        "en": {
            "title": "ZipBloat - ZIP File Size Enlarger",
            "original_file": "Original ZIP File:",
            "output_file": "Output ZIP File:",
            "target_size": "Target Size (GB):",
            "size_tip": "Recommended 1-20GB",
            "zoom_method": "Enlarge Method:",
            "empty_block": "Add Empty Blocks",
            "nest_zip": "Nested ZIP",
            "append_junk": "Append Junk Data",
            "zip_bomb": "ZIP Bomb Mode",
            "start": "Start Generating",
            "cancel": "Cancel",
            "status_ready": "Status: Ready",
            "status_running": "Status: Generating...",
            "status_canceled": "Status: Canceled",
            "status_completed": "Status: Generated!",
            "status_failed": "Status: Failed",
            "select_file": "Select File",
            "select_output": "Select Output",
            "err_num": "Error",
            "err_num_msg": "Target size must be a number!",
            "err_file_not_exist": "File not found! Please select a valid ZIP file.",
            "err_file_format": "Format error! Selected file is not a ZIP file.",
            "err_output_path": "Please select output file path!",
            "err_param": "Parameter error! Target size must be between 0-100GB.",
            "success_title": "Success",
            "success_msg": "ZIP file generated:",
            "fail_title": "Error",
            "fail_msg": "Generation failed:",
            "help_title": "Usage Instructions",
            "help_content": "ZipBloat Usage Instructions\n\n1. Select Original ZIP File\n2. Set Output Path\n3. Set Target Size (GB)\n4. Select Enlarge Method\n5. Click Start Generating\n\nNotes:\n- Recommended target size: 1-20GB\n- You can cancel during generation\n- Ensure write permission for output path",
            "about_title": "About",
            "about_content": "ZipBloat v1.0\n\nA simple and easy-to-use ZIP file size enlarger\n\nAuthor: Geekline\nWebsite: geekline.pages.dev\n\nFeatures:\n• 4 enlargement methods\n• Multi-language support\n• Real-time progress display\n• Cancel operation support\n\nLicense: MIT"
        }
    }

    language = StringProperty("zh")
    original_path = StringProperty("")
    output_path = StringProperty("")
    target_size = StringProperty("1.0")
    zoom_method = StringProperty("append_junk")
    status_text = StringProperty("状态: 就绪")
    progress_value = NumericProperty(0)
    is_running = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logic = ZipBloatLogic()
        self._setup_ui()
        self._request_permissions()

    def _request_permissions(self):
        if ANDROID:
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])

    def _setup_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        lang_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        self.btn_zh = ToggleButton(text='中文', size_hint_x=0.25)
        self.btn_en = ToggleButton(text='English', size_hint_x=0.25)
        self.btn_zh.bind(state=self._on_lang_change)
        self.btn_en.bind(state=self._on_lang_change)
        self.btn_zh.state = 'down'
        
        btn_about = Button(text='关于', size_hint_x=0.2)
        btn_about.bind(on_press=self._show_about)
        btn_help = Button(text='?', size_hint_x=0.1)
        btn_help.bind(on_press=self._show_help)
        
        lang_layout.add_widget(self.btn_zh)
        lang_layout.add_widget(self.btn_en)
        lang_layout.add_widget(btn_about)
        lang_layout.add_widget(btn_help)
        main_layout.add_widget(lang_layout)
        
        scroll = ScrollView()
        content_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10))
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        self.lbl_original = Label(text=self.lang_texts["zh"]["original_file"], size_hint_y=None, height=dp(30), halign='left')
        content_layout.add_widget(self.lbl_original)
        
        original_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        self.entry_original = TextInput(text='', multiline=False, readonly=True)
        self.btn_browse_original = Button(text=self.lang_texts["zh"]["select_file"], size_hint_x=0.3)
        self.btn_browse_original.bind(on_press=self._select_original_zip)
        original_layout.add_widget(self.entry_original)
        original_layout.add_widget(self.btn_browse_original)
        content_layout.add_widget(original_layout)
        
        self.lbl_output = Label(text=self.lang_texts["zh"]["output_file"], size_hint_y=None, height=dp(30), halign='left')
        content_layout.add_widget(self.lbl_output)
        
        output_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        self.entry_output = TextInput(text='', multiline=False, readonly=True)
        self.btn_browse_output = Button(text=self.lang_texts["zh"]["select_output"], size_hint_x=0.3)
        self.btn_browse_output.bind(on_press=self._select_output_zip)
        output_layout.add_widget(self.entry_output)
        output_layout.add_widget(self.btn_browse_output)
        content_layout.add_widget(output_layout)
        
        self.lbl_size = Label(text=self.lang_texts["zh"]["target_size"], size_hint_y=None, height=dp(30), halign='left')
        content_layout.add_widget(self.lbl_size)
        
        size_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        self.entry_size = TextInput(text='1.0', multiline=False, input_filter='float')
        self.lbl_size_tip = Label(text=self.lang_texts["zh"]["size_tip"], size_hint_x=0.4)
        size_layout.add_widget(self.entry_size)
        size_layout.add_widget(self.lbl_size_tip)
        content_layout.add_widget(size_layout)
        
        self.lbl_method = Label(text=self.lang_texts["zh"]["zoom_method"], size_hint_y=None, height=dp(30), halign='left')
        content_layout.add_widget(self.lbl_method)
        
        self.spinner_method = Spinner(
            text=self.lang_texts["zh"]["append_junk"],
            values=[
                self.lang_texts["zh"]["empty_block"],
                self.lang_texts["zh"]["nest_zip"],
                self.lang_texts["zh"]["append_junk"],
                self.lang_texts["zh"]["zip_bomb"]
            ],
            size_hint_y=None,
            height=dp(50)
        )
        self.spinner_method.bind(text=self._on_method_select)
        content_layout.add_widget(self.spinner_method)
        
        self.lbl_status = Label(text=self.lang_texts["zh"]["status_ready"], size_hint_y=None, height=dp(30), halign='left')
        content_layout.add_widget(self.lbl_status)
        
        self.progress = ProgressBar(max=100, value=0, size_hint_y=None, height=dp(30))
        content_layout.add_widget(self.progress)
        
        self.lbl_progress = Label(text='0%', size_hint_y=None, height=dp(30), halign='center')
        content_layout.add_widget(self.lbl_progress)
        
        button_layout = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        self.btn_start = Button(text=self.lang_texts["zh"]["start"])
        self.btn_start.bind(on_press=self._run_generator)
        self.btn_cancel = Button(text=self.lang_texts["zh"]["cancel"], disabled=True)
        self.btn_cancel.bind(on_press=self._cancel_task)
        button_layout.add_widget(self.btn_start)
        button_layout.add_widget(self.btn_cancel)
        content_layout.add_widget(button_layout)
        
        scroll.add_widget(content_layout)
        main_layout.add_widget(scroll)
        
        info_label = Label(
            text='ZipBloat © Geekline | geekline.pages.dev',
            size_hint_y=None,
            height=dp(30),
            font_size='12sp',
            color=(0.4, 0.4, 0.4, 1)
        )
        main_layout.add_widget(info_label)
        
        self.add_widget(main_layout)

    def _on_lang_change(self, instance, value):
        if value == 'down':
            if instance == self.btn_zh:
                self.btn_en.state = 'normal'
                self.language = 'zh'
            else:
                self.btn_zh.state = 'normal'
                self.language = 'en'
            self._update_language()

    def _update_language(self):
        lang = self.language
        texts = self.lang_texts[lang]
        
        self.lbl_original.text = texts["original_file"]
        self.lbl_output.text = texts["output_file"]
        self.btn_browse_original.text = texts["select_file"]
        self.btn_browse_output.text = texts["select_output"]
        self.lbl_size.text = texts["target_size"]
        self.lbl_size_tip.text = texts["size_tip"]
        self.lbl_method.text = texts["zoom_method"]
        self.spinner_method.values = [
            texts["empty_block"],
            texts["nest_zip"],
            texts["append_junk"],
            texts["zip_bomb"]
        ]
        self.spinner_method.text = texts[self.zoom_method]
        self.btn_start.text = texts["start"]
        self.btn_cancel.text = texts["cancel"]
        self.lbl_status.text = texts["status_ready"]

    def _on_method_select(self, spinner, text):
        lang = self.language
        texts = self.lang_texts[lang]
        method_mapping = {
            texts["empty_block"]: "empty_block",
            texts["nest_zip"]: "nest_zip",
            texts["append_junk"]: "append_junk",
            texts["zip_bomb"]: "zip_bomb"
        }
        self.zoom_method = method_mapping[text]

    def _select_original_zip(self, instance):
        if ANDROID:
            from android.storage import open_file_dialog
            path = open_file_dialog()
            if path:
                self.original_path = path
                self.entry_original.text = path
                dir_name = os.path.dirname(path)
                file_name = os.path.basename(path)
                name, ext = os.path.splitext(file_name)
                self.output_path = os.path.join(dir_name, f"{name}_big{ext}")
                self.entry_output.text = self.output_path
        else:
            from kivy.uix.filechooser import FileChooserListView
            content = BoxLayout(orientation='vertical')
            filechooser = FileChooserListView(filters=['*.zip'])
            btn_layout = BoxLayout(size_hint_y=None, height=dp(50))
            btn_select = Button(text='Select')
            btn_cancel = Button(text='Cancel')
            
            def on_select(instance):
                if filechooser.selection:
                    path = filechooser.selection[0]
                    self.original_path = path
                    self.entry_original.text = path
                    dir_name = os.path.dirname(path)
                    file_name = os.path.basename(path)
                    name, ext = os.path.splitext(file_name)
                    self.output_path = os.path.join(dir_name, f"{name}_big{ext}")
                    self.entry_output.text = self.output_path
                    popup.dismiss()
            
            def on_cancel(instance):
                popup.dismiss()
            
            btn_select.bind(on_press=on_select)
            btn_cancel.bind(on_press=on_cancel)
            btn_layout.add_widget(btn_select)
            btn_layout.add_widget(btn_cancel)
            content.add_widget(filechooser)
            content.add_widget(btn_layout)
            
            popup = Popup(title='Select ZIP File', content=content, size_hint=(0.9, 0.9))
            popup.open()

    def _select_output_zip(self, instance):
        if ANDROID:
            from android.storage import save_file_dialog
            path = save_file_dialog()
            if path:
                self.output_path = path
                self.entry_output.text = path
        else:
            from kivy.uix.filechooser import FileChooserListView
            content = BoxLayout(orientation='vertical')
            filechooser = FileChooserListView(filters=['*.zip'])
            btn_layout = BoxLayout(size_hint_y=None, height=dp(50))
            btn_select = Button(text='Select')
            btn_cancel = Button(text='Cancel')
            
            def on_select(instance):
                if filechooser.selection:
                    path = filechooser.selection[0]
                    self.output_path = path
                    self.entry_output.text = path
                    popup.dismiss()
            
            def on_cancel(instance):
                popup.dismiss()
            
            btn_select.bind(on_press=on_select)
            btn_cancel.bind(on_press=on_cancel)
            btn_layout.add_widget(btn_select)
            btn_layout.add_widget(btn_cancel)
            content.add_widget(filechooser)
            content.add_widget(btn_layout)
            
            popup = Popup(title='Select Output Path', content=content, size_hint=(0.9, 0.9))
            popup.open()

    def _run_generator(self, instance):
        if self.is_running:
            return
        
        original_path = self.entry_original.text
        output_path = self.entry_output.text
        target_size_str = self.entry_size.text
        
        if not original_path:
            self._show_error(self.lang_texts[self.language]["err_file_not_exist"])
            return
        
        if not os.path.exists(original_path):
            self._show_error(self.lang_texts[self.language]["err_file_not_exist"])
            return
        
        if not original_path.lower().endswith('.zip'):
            self._show_error(self.lang_texts[self.language]["err_file_format"])
            return
        
        if not output_path:
            self._show_error(self.lang_texts[self.language]["err_output_path"])
            return
        
        try:
            target_size = float(target_size_str)
            if target_size <= 0 or target_size > 100:
                self._show_error(self.lang_texts[self.language]["err_param"])
                return
        except ValueError:
            self._show_error(self.lang_texts[self.language]["err_num_msg"])
            return
        
        self.is_running = True
        self.btn_start.disabled = True
        self.btn_cancel.disabled = False
        self.lbl_status.text = self.lang_texts[self.language]["status_running"]
        self.progress.value = 0
        self.lbl_progress.text = '0%'
        
        self.logic.cancel_flag = False
        
        def progress_callback(progress):
            self.progress.value = progress
            self.lbl_progress.text = f'{progress}%'
        
        def generate_thread():
            try:
                success = False
                if self.zoom_method == "empty_block":
                    success = self.logic.generate_empty_block_zip(
                        original_path, output_path, target_size, progress_callback
                    )
                elif self.zoom_method == "nest_zip":
                    success = self.logic.generate_nested_zip(
                        original_path, output_path, target_size, progress_callback
                    )
                elif self.zoom_method == "append_junk":
                    success = self.logic.generate_append_junk_zip(
                        original_path, output_path, target_size, progress_callback
                    )
                elif self.zoom_method == "zip_bomb":
                    success = self.logic.generate_zip_bomb(
                        original_path, output_path, target_size, progress_callback
                    )
                
                Clock.schedule_once(lambda dt: self._on_generation_complete(success))
            except Exception as e:
                self.logic.logger.error(f"Generation error: {str(e)}")
                Clock.schedule_once(lambda dt: self._on_generation_complete(False))
        
        thread = threading.Thread(target=generate_thread)
        thread.start()

    def _on_generation_complete(self, success):
        self.is_running = False
        self.btn_start.disabled = False
        self.btn_cancel.disabled = True
        
        if self.logic.cancel_flag:
            self.lbl_status.text = self.lang_texts[self.language]["status_canceled"]
        elif success:
            self.lbl_status.text = self.lang_texts[self.language]["status_completed"]
            self._show_success(self.lang_texts[self.language]["success_msg"] + f"\n{self.output_path}")
        else:
            self.lbl_status.text = self.lang_texts[self.language]["status_failed"]
            self._show_error(self.lang_texts[self.language]["fail_msg"])

    def _cancel_task(self, instance):
        if self.is_running:
            self.logic.cancel_flag = True

    def _show_error(self, message):
        lang = self.language
        texts = self.lang_texts[lang]
        content = BoxLayout(orientation='vertical', padding=dp(10))
        lbl = Label(text=message, halign='center')
        content.add_widget(lbl)
        btn = Button(text='OK', size_hint_y=None, height=dp(50))
        
        def on_close(instance):
            popup.dismiss()
        
        btn.bind(on_press=on_close)
        content.add_widget(btn)
        popup = Popup(title=texts["err_num"], content=content, size_hint=(0.8, 0.4))
        popup.open()

    def _show_success(self, message):
        lang = self.language
        texts = self.lang_texts[lang]
        content = BoxLayout(orientation='vertical', padding=dp(10))
        lbl = Label(text=message, halign='center')
        content.add_widget(lbl)
        btn = Button(text='OK', size_hint_y=None, height=dp(50))
        
        def on_close(instance):
            popup.dismiss()
        
        btn.bind(on_press=on_close)
        content.add_widget(btn)
        popup = Popup(title=texts["success_title"], content=content, size_hint=(0.8, 0.4))
        popup.open()

    def _show_help(self, instance):
        lang = self.language
        texts = self.lang_texts[lang]
        content = BoxLayout(orientation='vertical', padding=dp(10))
        scroll = ScrollView()
        lbl = Label(text=texts["help_content"], halign='left', valign='top', text_size=(None, None))
        lbl.bind(texture_size=lbl.setter('size'))
        scroll.add_widget(lbl)
        content.add_widget(scroll)
        btn = Button(text='OK', size_hint_y=None, height=dp(50))
        
        def on_close(instance):
            popup.dismiss()
        
        btn.bind(on_press=on_close)
        content.add_widget(btn)
        popup = Popup(title=texts["help_title"], content=content, size_hint=(0.9, 0.8))
        popup.open()

    def _show_about(self, instance):
        lang = self.language
        texts = self.lang_texts[lang]
        content = BoxLayout(orientation='vertical', padding=dp(10))
        scroll = ScrollView()
        lbl = Label(text=texts["about_content"], halign='left', valign='top', text_size=(None, None))
        lbl.bind(texture_size=lbl.setter('size'))
        scroll.add_widget(lbl)
        content.add_widget(scroll)
        btn = Button(text='OK', size_hint_y=None, height=dp(50))
        
        def on_close(instance):
            popup.dismiss()
        
        btn.bind(on_press=on_close)
        content.add_widget(btn)
        popup = Popup(title=texts["about_title"], content=content, size_hint=(0.8, 0.7))
        popup.open()


class ZipBloatApp(App):
    def build(self):
        self.title = 'ZipBloat'
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        return sm


if __name__ == '__main__':
    ZipBloatApp().run()
