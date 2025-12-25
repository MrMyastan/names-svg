import sys
from typing import Dict

from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QSpinBox,
    QDialog,
    QTreeWidget,
    QTreeWidgetItem,
    QPushButton,
    QFileDialog,
    QFontComboBox,
    QColorDialog,
    QComboBox,
    QMessageBox,
    QSizePolicy,
)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtCore import Qt, QTimer, QSize, QXmlStreamReader
from PySide6.QtGui import QCloseEvent, QPainter, QFont, QColor, QAction, QKeySequence


from data import (
    Content,
    FullStyling,
    LayoutConfig,
    TextStyling,
    process_names,
)
from gen import render_svg

content = Content([], [], False)
styling = FullStyling()
layout_config = LayoutConfig()
svg_content = ""
svg_widget = None
changes_since_render = False
changes_since_save = False

rerender_count = 0

# TODO: Only rerender if changes?
def update_svg():
    global svg_content
    global svg_widget
    global rerender_count
    global changes_since_render

    if changes_since_render:
        svg_document = render_svg(content, layout_config, styling)
        svg_content = str(svg_document)
        rerender_count += 1
        print(f"Rerendered {rerender_count}")
        if svg_widget:
            svg_widget.update_content(QXmlStreamReader(svg_content))
            svg_widget.update()
        changes_since_render = False

def mark_changes():
    global changes_since_render
    global changes_since_save
    changes_since_render = True
    changes_since_save = True

# def perform_batch_update(update_function):
#     global batch_update_lock
#     batch_update_lock = True
#     update_function()
#     batch_update_lock = False
#     #update_svg()

class SpacingEntry(QWidget):
    def __init__(self, setting: str, value: int, parent = None):
        super().__init__(parent)
        layout = QHBoxLayout()

        self.setting = setting

        self.setting_label = QLabel(setting.replace("_", " ").title())

        self.value_edit = QSpinBox(self)

        self.value_edit.setMinimum(-1000)
        self.value_edit.setMaximum(1000)
        self.value_edit.setValue(value)

        self.value_edit.valueChanged.connect(self.update_value)

        layout.addWidget(self.setting_label)
        layout.addWidget(self.value_edit)

        current_margins = layout.contentsMargins()
        layout.setContentsMargins(current_margins.left(),7,current_margins.right(),7)

        self.setLayout(layout)

    def update_value(self, new_value: int):
        layout_config.set_value(self.setting, new_value)
        mark_changes()

class SpacingSettings(QWidget):
    """a widget representing a spacing entry
    """
    def __init__(self, parent = None):
        super().__init__(parent)
        
        self.settings = layout_config.get_all_keys_and_values()

        self.spacing_entries: Dict[str, SpacingEntry] = {}

        layout = QVBoxLayout()
        layout.setSpacing(0)
        for setting, value in self.settings.items():
            entry = SpacingEntry(setting, value, self)
            self.spacing_entries[setting] = entry
            layout.addWidget(entry)

        self.reset_button = QPushButton("Reset", parent=self)
        self.reset_button.pressed.connect(self.reset_to_defaults)
        layout.addWidget(self.reset_button)
        layout.addStretch()
        self.setLayout(layout)

    def reset_to_defaults(self):
        defaults = layout_config.get_all_defaults()
        for setting,entry in self.spacing_entries.items():
            default = defaults[setting]
            layout_config.set_value(setting, default)
            entry.value_edit.setValue(default)
        mark_changes()

# # \TODO: Wire-up
# class ParticipantEntry(QWidget):
#     """a widget representing one participant entry with name and role
#     """
#     def __init__(self, name = "", role = "", parent = None, roles_enabled = True):
#         super().__init__(parent)
#         layout = QHBoxLayout()
#         self.name_edit = QLineEdit(name)
#         self.role_edit = QLineEdit(role)
#         self.role_edit.setDisabled(not roles_enabled)
#         layout.addWidget(self.name_edit)
#         layout.addWidget(self.role_edit)
#         self.setLayout(layout)

# # \TODO: Wire-up
# class SectionEntry(QWidget):
#     """a widget representing a section of participant entries
#     """
#     def __init__(self, title = "", parent = None, roles_enabled = True):
#         super().__init__(parent)
        
#         layout = QVBoxLayout()
        
#         self.title_label = QLineEdit(title)
#         layout.addWidget(self.title_label)
        
#         self.participant_entries = []
#         self.roles_enabled = roles_enabled
#         self.setLayout(layout)

#     def add_participant(self, name = "", role = ""):
#         """adds a participant entry to this section
#         """
#         entry = ParticipantEntry(name, role, self, self.roles_enabled)
#         self.participant_entries.append(entry)
#         self.layout().addWidget(entry) # type: ignore

# class FileSelector(QWidget):
#     def __init__(self, name, parent = None, save = False, svg=False, txt=False):
#         super().__init__(parent)

#         self.save = save

#         self.selected_file = None

#         self.filetypes = []
#         if svg:
#             self.filetypes.append("SVG Files (*.svg)")
#         if txt:
#             self.filetypes.append("Text Files (*.txt)")
#         if not self.filetypes:  
#             self.filetypes.append("All Files (*.*)")
#         self.filetypes_str = ";;".join(self.filetypes)

#         layout = QVBoxLayout()

#         self.label = QLabel(name)
#         layout.addWidget(self.label)

#         self.open_button = QPushButton("Open File")
#         self.open_button.clicked.connect(self.open_file_dialog)
#         layout.addWidget(self.open_button)

#         self.selected_file_label = QLabel(f"No file selected.")
#         layout.addWidget(self.selected_file_label)

#         self.setLayout(layout)

#     def open_file_dialog(self):
#         # Open a file dialog to select a single existing file
#         if not self.save:
#             file_name, _ = QFileDialog.getOpenFileName(
#                 self,
#                 "Open File",
#                 "",  # Initial directory (empty for default)
#                 self.filetypes_str # File filters
#             )
#         else:
#             file_name, _ = QFileDialog.getSaveFileName(
#                 self,
#                 "Save File",
#                 "",  # Initial directory (empty for default)
#                 self.filetypes_str # File filters
#             )

#         if file_name:
#             self.selected_file_label.setText(f"Selected file: {file_name}")
#             self.selected_file = file_name
#         else:
#             self.selected_file_label.setText("No file selected.")
#             self.selected_file = None


# # \? Simple labelled buttons? instead of multiple labels and button?
# class FileSettings(QWidget):
#     def __init__(self, parent = None):
#         super().__init__(parent)
        
#         layout = QVBoxLayout()
        
#         self.svg_selector = FileSelector("Select SVG Output File", self, save=True, svg=True)
#         layout.addWidget(self.svg_selector)

#         self.import_button = QPushButton("Export SVG", self)
#         self.import_button.clicked.connect(self.export_svg)
#         layout.addWidget(self.import_button)
        
#         self.txt_selector = FileSelector("Select Names Input File", self, txt=True)
#         layout.addWidget(self.txt_selector)

#         self.import_button = QPushButton("Import Names", self)
#         self.import_button.clicked.connect(self.import_names)
#         layout.addWidget(self.import_button)

#         # TODO: Wire-up
#         self.text_export_button = QPushButton("Export Names", self)
#         layout.addWidget(self.text_export_button)
        
#         self.setLayout(layout)

#     # TODO: If no file selected selected, or if svg invalid
#     # TODO: cmd s to save
#     def export_svg(self):
#         if self.svg_selector.selected_file:
#             with open(self.svg_selector.selected_file, "w") as f:
#                 f.write(svg_content)

#     # TODO: If not selected, or invalid input
#     def import_names(self):
#         if self.txt_selector.selected_file:
#             with open(self.txt_selector.selected_file, "r") as f:
#                 file_content = f.read()
#             try:
#                 global content
#                 tmp_content = process_names(file_content)
#                 content = tmp_content
#             except ValueError as e:
#                 print(e.args[0])
#             #update_svg()

class FileMenu():
    """a menu to handle file operations
    """
    def __init__(self, main: QMainWindow, file_menu):
        self.save_destination: str|None = None
        self.main: QMainWindow = main

        save_action = QAction("&Save", main)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save &As", main)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        open_names_action = QAction("&Open Names", main)
        open_names_action.setShortcut(QKeySequence.StandardKey.Open)
        open_names_action.triggered.connect(self.open_names_file)
        file_menu.addAction(open_names_action)

    def get_file_selection(self, save: bool = False, svg = False, txt = False):
        self.filetypes = []
        if svg:
            self.filetypes.append("SVG Files (*.svg)")
        if txt:
            self.filetypes.append("Text Files (*.txt)")
        if not self.filetypes:  
            self.filetypes.append("All Files (*.*)")
        self.filetypes_str = ";;".join(self.filetypes)

        if not save:
            file_name, _ = QFileDialog.getOpenFileName(
                self.main,
                "Open File",
                "",  # Initial directory (empty for default)
                self.filetypes_str # File filters
            )
        else:
            file_name, _ = QFileDialog.getSaveFileName(
                self.main,
                "Save File",
                "",  # Initial directory (empty for default)
                self.filetypes_str # File filters
            )

        return file_name

    def export_svg(self, destination):
            with open(destination, "w") as f:
                f.write(svg_content)
            global changes_since_save
            changes_since_save = False

    def save_file(self):
        if self.save_destination:
            self.export_svg(self.save_destination)
        else:
            self.save_file_as()

    def save_file_as(self):
        self.save_destination = self.get_file_selection(save=True, svg=True)
        if self.save_destination:
            self.export_svg(self.save_destination)

    def open_names_file(self):
        selected_file = self.get_file_selection(txt=True)
        if selected_file:
            with open(selected_file, "r") as f:
                file_content = f.read()
                try:
                    global content
                    tmp_content = process_names(file_content)
                    content = tmp_content
                except ValueError as e:
                    print(e.args[0])
        mark_changes()

class LabelledComboBox(QWidget):
    """a widget representing one labelled combo box
    """
    def __init__(self, label: str, items: list[str], parent = None):
        super().__init__(parent)
        layout = QHBoxLayout()
        
        self.label_widget = QLabel(label, self)
        layout.addWidget(self.label_widget)

        self.combo_box = QComboBox(self)
        self.combo_box.addItems(items)
        layout.addWidget(self.combo_box)

        self.setLayout(layout)

# TODO: Display color on control?
class LabelledColorEntry(QWidget):
    """a widget representing one labelled color entry
    """
    def __init__(self, label: str, parent = None):
        super().__init__(parent)
        layout = QHBoxLayout()
        
        self.label_widget = QLabel(label, self)
        layout.addWidget(self.label_widget)

        self.color_button = QColorDialog(self)
        layout.addWidget(self.color_button)

        self.open_dialog_button = QPushButton("Select Color", self)
        self.open_dialog_button.clicked.connect(self.color_button.open)
        layout.addWidget(self.open_dialog_button)

        self.setLayout(layout)

class TextStyleEntry(QWidget):
    """a widget representing one text style entry
    """
    def __init__(self, style_model: TextStyling, parent = None):
        super().__init__(parent)
        """
        font-family
        font-size
        font-weight
        font-style
        fill
        """
        layout = QVBoxLayout()

        self.style_model = style_model
        
        self.font_family_edit = QFontComboBox(self)
        self.font_family_edit.currentFontChanged.connect(self.font_updated)
        layout.addWidget(self.font_family_edit)

        self.font_size_edit = QSpinBox(self)
        self.font_size_edit.setSuffix("px")
        self.font_size_edit.textChanged.connect(self.font_size_updated)
        layout.addWidget(self.font_size_edit)

        self.font_weight_edit = LabelledComboBox("Font Weight:", ["Normal", "Bold"], self)
        self.font_weight_edit.combo_box.currentTextChanged.connect(self.font_weight_updated)
        layout.addWidget(self.font_weight_edit)

        self.font_style_edit = LabelledComboBox("Font Style:", ["Normal", "Italic"], self)
        self.font_style_edit.combo_box.currentTextChanged.connect(self.font_style_updated)
        layout.addWidget(self.font_style_edit)

        self.color_button = LabelledColorEntry("Fill:", self)
        self.color_button.color_button.currentColorChanged.connect(self.color_updated)
        layout.addWidget(self.color_button)

        self.setLayout(layout)

        self.set_values()

        #perform_batch_update(self.set_values)

    def set_values(self):
        self.font_family_edit.setCurrentFont(QFont(self.style_model.font_family))
        self.font_size_edit.setValue(int(self.style_model.font_size.replace("px", "")))
        self.font_weight_edit.combo_box.setCurrentText(self.style_model.font_weight.capitalize())
        self.font_style_edit.combo_box.setCurrentText(self.style_model.font_style.capitalize())
        self.color_button.color_button.setCurrentColor(QColor(self.style_model.fill))
        mark_changes()

    def font_updated(self, font: QFont):
        self.style_model.font_family = font.family()
        #update_svg()
        mark_changes()

    def font_size_updated(self, size: str):
        self.style_model.font_size = size
        #update_svg()
        mark_changes()

    def font_weight_updated(self, weight: str):
        self.style_model.font_weight = weight.lower()
        #update_svg()
        mark_changes()

    def font_style_updated(self, style: str):
        self.style_model.font_style = style.lower()
        #update_svg()
        mark_changes()

    def color_updated(self, color: QColor):
        self.style_model.fill = color.name()
        #update_svg()
        mark_changes()

class SectionExpandButton(QPushButton):
    """a QPushbutton that can expand or collapse its section
    """
    def __init__(self, item, text = "", parent = None):
        super().__init__(text, parent)
        self.section = item
        self.clicked.connect(self.on_clicked)
        
    def on_clicked(self):
        """toggle expand/collapse of section by clicking
        """
        if self.section.isExpanded():
            self.section.setExpanded(False)
        else:
            self.section.setExpanded(True)
         
class CollapsibleDialog(QDialog):
    """a dialog to which collapsible sections can be added;
    reimplement define_sections() to define sections and
        add them as (title, widget) tuples to self.sections
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        layout = QVBoxLayout()
        layout.addWidget(self.tree)
        self.setLayout(layout)
        self.tree.setIndentation(0)
        
        self.sections = []
        self.define_sections()
        self.add_sections()

        self.setMinimumWidth(300)

    def add_sections(self):
        """adds a collapsible sections for every 
        (title, widget) tuple in self.sections
        """
        for (title, widget) in self.sections:
            button1 = self.add_button(title)
            section1 = self.add_widget(button1, widget)
            button1.addChild(section1)

    def define_sections(self):
        """reimplement this to define all your sections
        and add them as (title, widget) tuples to self.sections
        """
        pass

    def add_button(self, title):
        """creates a QTreeWidgetItem containing a button 
        to expand or collapse its section
        """
        item = QTreeWidgetItem()
        self.tree.addTopLevelItem(item)
        self.tree.setItemWidget(item, 0, SectionExpandButton(item, text = title))
        return item

    def add_widget(self, button, widget):
        """creates a QWidgetItem containing the widget,
        as child of the button-QWidgetItem
        """
        section = QTreeWidgetItem(button)
        section.setDisabled(True)
        self.tree.setItemWidget(section, 0, widget)
        return section

class StylesControls(QWidget):
    """a widget to control styles settings
    """
    def __init__(self, parent = None):
        super().__init__(parent)
        layout = QVBoxLayout()
        
        self.set_color_for_all_button = LabelledColorEntry("Set Color for All", self)
        layout.addWidget(self.set_color_for_all_button)

        self.restore_defaults_button = QPushButton("Restore Defaults", self)
        layout.addWidget(self.restore_defaults_button)

        self.setLayout(layout)

class CollapsibleStyleDialog(CollapsibleDialog):
    """a dialog to define text styles with collapsible sections
    """
    def define_sections(self):
        """define text style sections
        """

        self.controls = StylesControls(parent=self)

        self.sections.append(("Controls", self.controls))
        self.text_style_entries: Dict[str, TextStyleEntry] = {}

        self.styles: Dict[str, TextStyling] = {
            "Label": styling.label_style, 
            "Name": styling.name_style, 
            "Role": styling.role_style, 
            "Subtitle 1": styling.sub1_style, 
            "Subtitle 2": styling.sub2_style,
        }
        for kind, style in self.styles.items():
            text_style_entry = TextStyleEntry(style, parent=self)
            self.sections.append((f"{kind} Styles", text_style_entry))
            self.text_style_entries[kind] = (text_style_entry)

        # TODO: Live update as user is choosing a color without hanging the program
        self.controls.set_color_for_all_button.color_button.colorSelected.connect(self.set_color_for_all)
        self.controls.restore_defaults_button.clicked.connect(self.reset_to_defaults)
        

    def set_color_for_all(self, color: QColor):
        """set all styles to the given color
        """
        for style in self.styles.values():
            style.fill = color.name()
        for entry in self.text_style_entries.values():
            entry.color_button.color_button.setCurrentColor(color)
        mark_changes()

    def reset_to_defaults(self):
        # ? something better? maybe it should have a key to the global model?
        """reset all styles to their default values
        """
        self.text_style_entries["Label"].style_model.update_from_other(TextStyling.label_defaults())
        self.text_style_entries["Name"].style_model.update_from_other(TextStyling.name_defaults())
        self.text_style_entries["Role"].style_model.update_from_other(TextStyling.role_defaults())
        self.text_style_entries["Subtitle 1"].style_model.update_from_other(TextStyling.sub1_defaults())
        self.text_style_entries["Subtitle 2"].style_model.update_from_other(TextStyling.sub2_defaults())
        for entry in self.text_style_entries.values():
            entry.set_values()
        mark_changes()

# # \TODO: Wire-up
# class ListModificationControls(QWidget):
#     """a widget to control list modification
#     """
#     def __init__(self, parent = None):
#         super().__init__(parent)
#         layout = QHBoxLayout()
        
#         # Section reorder buttons
#         self.move_up_button = QPushButton("Move Up", self)
#         layout.addWidget(self.move_up_button)
#         self.move_down_button = QPushButton("Move Down", self)
#         layout.addWidget(self.move_down_button)

#         # add new item button
#         self.add_item_button = QPushButton("Add Item", self)
#         layout.addWidget(self.add_item_button)

#         # delete item button
#         self.delete_item_button = QPushButton("Delete Item", self)
#         layout.addWidget(self.delete_item_button)

#         self.setLayout(layout)

# # \TODO: Wire-up
# class NamesAndRolesControl(QWidget):
#     """a widget to control names and roles settings
#     """
#     def __init__(self, parent = None):
#         super().__init__(parent)
#         layout = QVBoxLayout()
        
#         # roles enabled check box
#         self.roles_enabled_button = QCheckBox("Enable Roles", self)
#         layout.addWidget(self.roles_enabled_button)

#         # section list view
#          # Create a QStandardItemModel
#         self.model = QStandardItemModel()

#         # Add some items to the model
#         items_data = ["Section 1", "Section 2", "Section 3"]
#         for item_text in items_data:
#             item = QStandardItem(item_text)
#             self.model.appendRow(item)

#         # Create a QListView
#         self.list_view = QListView(self)
#         self.list_view.setModel(self.model)
#         self.list_view.setSelectionMode(QListView.SelectionMode.SingleSelection)
#         layout.addWidget(self.list_view)

#         # Section reorder buttons
#         self.list_modification_controls = ListModificationControls(parent=self)
#         layout.addWidget(self.list_modification_controls)

#         self.setLayout(layout)

# # \TODO: Wire-up
# class CollapsibleNamesDialog(CollapsibleDialog):
#     """a dialog to define names and roles with collapsible sections
#     """
#     def define_sections(self):
        
#         self.sections.append(("Controls", NamesAndRolesControl(parent=self)))
        
#         """define name sections
#         """
#         sections = {
#             "Main Cast": [("Alice", "Protagonist"), ("Bob", "Antagonist")],
#             "Supporting Cast": [("Charlie", "Supporting Role"), ("Dave", "Cameo")],
#         }
#         for section, participants in sections.items():
#             widget = SectionEntry(section, roles_enabled = True, parent=self)
#             for name, role in participants:
#                 widget.add_participant(name, role)
#             self.sections.append((section, widget))

# class CollapsibleMainDialog(CollapsibleDialog):
#     """a dialog to define general settings with collapsible sections
#     """
#     def define_sections(self):
#         """define general settings sections
#         """
#         self.sections.append(("Spacing Settings", SpacingSettings(parent=self)))
#         self.sections.append(("File Settings", FileSettings(parent=self)))
#         self.sections.append(("Text Styles", CollapsibleStyleDialog(parent=self)))
#         self.sections.append(("Names and Roles", CollapsibleNamesDialog(parent=self)))

class SvgWidget(QWidget):
    def __init__(self, svg_content: QXmlStreamReader, parent=None):
        super().__init__(parent)
        # Load the SVG file using QSvgRenderer
        self.renderer = QSvgRenderer()
        self.setMinimumSize(QSize(400, 200))
        self.renderer.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
        self.update_content(svg_content)

        self.timer = QTimer()
        self.timer.timeout.connect(update_svg)
        self.timer.setInterval(1000//24)
        self.timer.start()

    def update_content(self, svg_content: QXmlStreamReader):
        self.renderer.load(svg_content)
        if not self.renderer.isValid():
            print(f"Error: SvgRenderer failed to load SVG content.")
        self.renderer.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)

    def paintEvent(self, event):
        # A QPainter operates on the widget (self) within the paintEvent
        painter = QPainter(self)
        
        # Optional: Set a render hint for smoother output
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Render the SVG to the painter on the specified bounds (the whole widget)
        self.renderer.render(painter, self.rect())
        
        # The painter is closed automatically when exiting the paintEvent function scope
        # in Python bindings, though an explicit painter.end() can also be used.

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Names SVG Generator")

        layout = QGridLayout()

        global svg_widget
        svg_widget = SvgWidget(QXmlStreamReader(svg_content), parent=self)
        svg_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.spacing_settings = SpacingSettings(parent=self)
        self.spacing_settings.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.spacing_settings, 0, 0)
        
        self.style_settings = CollapsibleStyleDialog(parent=self)
        self.style_settings.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.style_settings, 0, 3)
        
        # layout.addWidget(CollapsibleNamesDialog(parent=self), 1, 3)
        
        layout.addWidget(svg_widget, 0, 1, 2, 2)

        # layout.setColumnStretch(1, 1)

        file_qmenu = self.menuBar().addMenu("&File")
        self.file_menu = FileMenu(self, file_qmenu)

        help_qmenu = self.menuBar().addMenu("&Help")
        help_action = QAction("Show info", self)
        help_action.triggered.connect(self.help_dialog)
        help_qmenu.addAction(help_action)

        self.central_widget = QWidget()
        self.central_widget.setLayout(layout)
        self.setCentralWidget(self.central_widget)

        global changes_since_save
        global changes_since_render
        changes_since_save = False
        changes_since_render = False
    
    def closeEvent(self, event: QCloseEvent) -> None:
        if not changes_since_save:
            event.accept()
            return
        
        button = QMessageBox.warning(
            self,
            "Quit Confirmation",
            "You may have unsaved changes. Do you want to save and quit, quit without saving, or cancel?",
            buttons=QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.Discard,
            defaultButton=QMessageBox.StandardButton.Discard,
        )

        if button == QMessageBox.StandardButton.Save:
            self.file_menu.save_file()
        elif button == QMessageBox.StandardButton.Cancel:
            event.ignore()
            return
        
        event.accept()

    def help_dialog(self):
        QMessageBox.information(
            self,
            "Help",
            """This program generates an SVG file containing the names of participants in and information about a production to be used for the back of a t-shirt.
    To use the program, adjust the spacing settings and text styles as desired using the controls on the left and right.
    You can save the generated design using the File menu or Ctrl/Cmd + S.
    To load a list of names, use the File menu or Ctrl/Cmd + O to open a text file containing the names. The file should be formatted as follows:
    
    Title of Section 1 (ex. Cast)
    Name 1: Role 1
    Name 2: Role 2
    
    Title of Section 2 (ex. Crew)
    Name 3: Role 3
    Name 4: Role 4

    Subs: Subtitle 1
    Subtitle 2

    The roles are optional, however all names should either include the semicolon or not include it. You can have as many sections or participant names as you would like. You can have no more than 2 subtitles, however they are optional and you can have 0, 1, or 2.
    You can open this information dialog again from the Help menu.""",
            buttons=QMessageBox.StandardButton.Ok,
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    window.help_dialog()

    sys.exit(app.exec())