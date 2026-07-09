from customtkinter import CTkLabel, CTkTextbox, CTkFrame, CTkSwitch
from tkinter import END
import re

from widgets.frames import CustomFrame
from widgets.dropdown import CustomDropdown
from widgets.buttons import CustomButton, ImageButton
from constants import COLOR, SIZE, POS, OFFSET, FONT_SIZE, WINDOW_MARGIN, SETTINGS_WINDOW_MARGIN, WINDOW_HEIGHT, WINDOW_WIDTH, ENTRY_HEIGHT, Pos, Size
from strings import STRINGS, get_default_language_code
from fonts import FONT
from helpers import open_github_issue, resource_path, open_path
from settings_manager import Settings

INVALID_TEXTBOX_ARGS = [ "cluster", "shard", "monitor_parent_process", "token", "ownerdir", "persistent_storage_root", "ugc_directory" ]

class SettingsTooltip(CTkFrame):
    def __init__(self, master, parent, title, description):
        self._master = master
        self.parent = parent

        max_width = self.parent.winfo_reqwidth() / self.parent._apply_widget_scaling(1) - 30

        super().__init__(
            master=master,
            fg_color=COLOR.DARK_GRAY,
            border_width=0,
            corner_radius=10,
            width=max_width,
            height=0,
        )

        self.title = CTkLabel(
            master=self,
            height=0,
            text=title,
            text_color=COLOR.WHITE,
            fg_color="transparent",
            font=FONT.SETTING_TITLE,
            wraplength = max_width,
            justify="left"
        )

        self.description = CTkLabel(
            master=self,
            height=0,
            text=description,
            text_color=COLOR.WHITE_HOVER,
            fg_color="transparent",
            font=FONT.SETTING_DESC,
            wraplength = max_width,
            justify="left"
        )

        self.title.grid(
            row = 0,
            column = 0,
            padx = 10,
            sticky="nw",
        )

        self.description.grid(
            row = 1,
            column = 0,
            padx = 10,
            pady = (5, 0),
            sticky="nw",
        )

    def get_height(self):
        self.update_idletasks()

        return self.winfo_reqheight() / self.parent._apply_widget_scaling(1) + 12

    def set_position(self):
        self.parent.update_idletasks()

        self.place(
            x=self.parent.winfo_x() / self.parent._apply_widget_scaling(1),
            y=(self.parent.winfo_y() - self.winfo_reqheight()) / self.parent._apply_widget_scaling(1) - 12,
        )

class SettingsScreen():
    def __init__(self, master) -> None:
        self.corner_radius = 10
        self.master = master
        self.bind = None

        self.root = CustomFrame(
            master=master,
            color=COLOR.DARK_GRAY,
            size=SIZE.SETTINGS_PANEL,
            corner_radius=self.corner_radius,
        )

        lang_code = self.master.settings.get(Settings.LANGUAGE)

        self.language_dropdown = CustomDropdown(
            master=self.root,
            options=[(code, name) for code, name in STRINGS.LANGUAGES.to_dict().items()],
            default=STRINGS.LANGUAGES[lang_code] is not None and lang_code or get_default_language_code(),
            on_selected_option=lambda code, name: self.master.settings.set(Settings.LANGUAGE, code)
        )

        self.language_dropdown._tooltip = SettingsTooltip(
            master=self.root,
            parent=self.language_dropdown.button,
            title=STRINGS.SETTINGS_SCREEN.LANGUAGE.TITLE,
            description=STRINGS.SETTINGS_SCREEN.LANGUAGE.DESC,
        )

        self.language_dropdown.button.place(
            x = SETTINGS_WINDOW_MARGIN,
            y = SETTINGS_WINDOW_MARGIN + self.language_dropdown._tooltip.get_height(),
        )

        self.language_dropdown._tooltip.set_position()

        # # -------------------------- #

        # self.tray_switch = CTkSwitch(
        #     master=self.root,
        #     text="",
        #     command=self._on_tray_toggle,
        #     onvalue=True,
        #     offvalue=False,
        #     fg_color=COLOR.GRAY_HOVER,
        #     progress_color=COLOR.GREEN,
        #     button_color=COLOR.WHITE,
        #     button_hover_color=COLOR.WHITE,
        #     text_color=COLOR.WHITE,
        #     font=FONT.SETTING_LONG_BUTTON,
        #     width=SIZE.LOGS_AUTO_SCROLL_SWITCH.w + 20,
        #     height=SIZE.LOGS_AUTO_SCROLL_SWITCH.h,
        # )

        # if self.master.settings.get(Settings.MINIMIZE_TO_TRAY):
        #     self.tray_switch.select()
        # else:
        #     self.tray_switch.deselect()

        # # Title label left-aligned
        # self.tray_title = CTkLabel(
        #     master=self.root,
        #     height=0,
        #     text_color=COLOR.WHITE,
        #     fg_color="transparent",
        #     font=FONT.SETTING_TITLE,
        #     anchor="w",
        # )

        # self.tray_title._tooltip = SettingsTooltip(
        #     master=self.root,
        #     parent=self.tray_title,
        #     title=STRINGS.SETTINGS_SCREEN.MINIMIZE_TO_TRAY.TITLE,
        #     description=STRINGS.SETTINGS_SCREEN.MINIMIZE_TO_TRAY.DESC,
        # )

        # self.tray_title.place(
        #     x = SETTINGS_WINDOW_MARGIN + 10,
        #     y = SETTINGS_WINDOW_MARGIN + self.language_dropdown._tooltip.get_height() + ENTRY_HEIGHT + 35,
        # )

        # # Switch placed accurately to the right of the rendered text bounds
        # self.tray_switch.place(
        #     x = SETTINGS_WINDOW_MARGIN + 10 + self.tray_title._tooltip.get_width() + 15,
        #     y = SETTINGS_WINDOW_MARGIN + self.language_dropdown._tooltip.get_height() + ENTRY_HEIGHT + 35,
        # )

        # # Description tooltip block
        # self.tray_switch._tooltip = SettingsTooltip(
        #     master=self.root,
        #     parent=self.root,
        #     title="",
        #     description="",
        # )

        # # -------------------------- #
        # -------------------------- #

        # 1. Base Y position cleanly below the Language section
        tray_y = SETTINGS_WINDOW_MARGIN + self.language_dropdown._tooltip.get_height() + ENTRY_HEIGHT + 35

        # 2. Title Label (Plain text, no hidden background frames)
        self.tray_title = CTkLabel(
            master=self.root,
            height=0,
            text=STRINGS.SETTINGS_SCREEN.MINIMIZE_TO_TRAY.TITLE,
            text_color=COLOR.WHITE,
            fg_color="transparent",
            font=FONT.SETTING_TITLE,
            anchor="w",
        )
        self.tray_title.place(
            x = SETTINGS_WINDOW_MARGIN + 10,
            y = tray_y,
        )

        # Force rendering update to get the absolute text width safely
        self.tray_title.update_idletasks()
        title_width = self.tray_title.winfo_reqwidth() / self.root._apply_widget_scaling(1)

        # 3. Toggle Switch placed inline right after the title text
        self.tray_switch = CTkSwitch(
            master=self.root,
            text="",
            command=self._on_tray_toggle,
            onvalue=True,
            offvalue=False,
            fg_color=COLOR.GRAY_HOVER,
            progress_color=COLOR.GREEN,
            button_color=COLOR.WHITE,
            button_hover_color=COLOR.WHITE,
            text_color=COLOR.WHITE,
            font=FONT.SETTING_LONG_BUTTON,
            width=SIZE.LOGS_AUTO_SCROLL_SWITCH.w + 20,
            height=SIZE.LOGS_AUTO_SCROLL_SWITCH.h,
        )

        if self.master.settings.get(Settings.MINIMIZE_TO_TRAY):
            self.tray_switch.select()
        else:
            self.tray_switch.deselect()

        self.tray_switch.place(
            x = SETTINGS_WINDOW_MARGIN + 10 + title_width + 15,
            y = tray_y - 9,
        )

        # 4. Standalone Description Text Block placed safely underneath
        tooltip_width = WINDOW_WIDTH / 2.5
        self.tray_desc = CTkLabel(
            master=self.root,
            height=0,
            text=STRINGS.SETTINGS_SCREEN.MINIMIZE_TO_TRAY.DESC,
            text_color=COLOR.WHITE_HOVER,
            fg_color="transparent",
            font=FONT.SETTING_DESC,
            wraplength=tooltip_width - 20,
            justify="left",
            anchor="nw"
        )
        self.tray_desc.place(
            x = SETTINGS_WINDOW_MARGIN + 10,
            y = tray_y + 24, # Explicit font-line height gap to match the grid look perfectly
        )

        # -------------------------- #

        # Auto Launch toggle
        auto_launch_y = tray_y + 70

        self.auto_launch_title = CTkLabel(
            master=self.root,
            height=0,
            text=STRINGS.SETTINGS_SCREEN.AUTO_LAUNCH.TITLE,
            text_color=COLOR.WHITE,
            fg_color="transparent",
            font=FONT.SETTING_TITLE,
            anchor="w",
        )
        self.auto_launch_title.place(
            x = SETTINGS_WINDOW_MARGIN + 10,
            y = auto_launch_y,
        )

        self.auto_launch_title.update_idletasks()
        auto_launch_title_width = self.auto_launch_title.winfo_reqwidth() / self.root._apply_widget_scaling(1)

        self.auto_launch_switch = CTkSwitch(
            master=self.root,
            text="",
            command=self._on_auto_launch_toggle,
            onvalue=True,
            offvalue=False,
            fg_color=COLOR.GRAY_HOVER,
            progress_color=COLOR.GREEN,
            button_color=COLOR.WHITE,
            button_hover_color=COLOR.WHITE,
            text_color=COLOR.WHITE,
            font=FONT.SETTING_LONG_BUTTON,
            width=SIZE.LOGS_AUTO_SCROLL_SWITCH.w + 20,
            height=SIZE.LOGS_AUTO_SCROLL_SWITCH.h,
        )

        if self.master.settings.get(Settings.AUTO_LAUNCH):
            self.auto_launch_switch.select()
        else:
            self.auto_launch_switch.deselect()

        self.auto_launch_switch.place(
            x = SETTINGS_WINDOW_MARGIN + 10 + auto_launch_title_width + 15,
            y = auto_launch_y - 9,
        )

        self.auto_launch_desc = CTkLabel(
            master=self.root,
            height=0,
            text=STRINGS.SETTINGS_SCREEN.AUTO_LAUNCH.DESC,
            text_color=COLOR.WHITE_HOVER,
            fg_color="transparent",
            font=FONT.SETTING_DESC,
            wraplength=tooltip_width - 20,
            justify="left",
            anchor="nw"
        )
        self.auto_launch_desc.place(
            x = SETTINGS_WINDOW_MARGIN + 10,
            y = auto_launch_y + 24,
        )

        # -------------------------- #

        self.arguments_entry = CTkTextbox(
            master = self.root,
            corner_radius=15,
            border_color=COLOR.GRAY,
            text_color=COLOR.WHITE_HOVER,
            fg_color=COLOR.GRAY,
            font=FONT.ENTRY_ARIAL,
            border_width=0,
            height=90,
            width=350,
        )

        self.arguments_entry._textbox.configure(selectbackground=COLOR.DARK_GRAY)
        self.arguments_entry.tag_config("goodoption", foreground=COLOR.LIGHT_BLUE)
        self.arguments_entry.tag_config("badoption", foreground=COLOR.LIGHT_RED)
        self.arguments_entry.highlight_pattern = re.compile(r"([-+]\w+)")

        self.arguments_entry.bind("<KeyRelease>", self.on_arguments_textbox_key)

        self.arguments_entry.insert(END, self.master.settings.get(Settings.LAUNCH_OPTIONS))
        self.on_arguments_textbox_key() # Highlight inserted text.

        self.arguments_entry._tooltip = SettingsTooltip(
            master=self.root,
            parent=self.arguments_entry,
            title=STRINGS.SETTINGS_SCREEN.LAUNCH_OPTIONS.TITLE,
            description=STRINGS.SETTINGS_SCREEN.LAUNCH_OPTIONS.DESC,
        )

        self.arguments_entry.place(
            x = WINDOW_WIDTH - SETTINGS_WINDOW_MARGIN - 350,
            y = SETTINGS_WINDOW_MARGIN + self.arguments_entry._tooltip.get_height(),
        )

        self.arguments_entry._tooltip.set_position()

        # -------------------------- #

        self.button_menu = CustomFrame(
            master=self.root,
            color=COLOR.DARK_GRAY,
            size=Size(0, 0),
            corner_radius=self.corner_radius,
        )

        buttons = [
            ("APP_LOG",      "assets/file.png",      lambda: open_path(resource_path("logs"))    ),
            ("LOCAL_FILES",  "assets/directory.png", lambda: open_path(resource_path("savedata"))),
            ("REPORT_ISSUE", "assets/bug.png",       lambda: open_github_issue(include_applog=True)),
        ]

        for text, img, cmd in buttons:
            btn = ImageButton(
                master=self.button_menu,
                text=STRINGS.SETTINGS_SCREEN.BUTTONS[text],
                image=img,
                image_size=(SIZE.SMALL_BUTTON_LONG.h - 15, SIZE.SMALL_BUTTON_LONG.h - 15),
                command=cmd,
                font=FONT.SETTING_LONG_BUTTON,
                width=SIZE.SMALL_BUTTON_LONG.w,
                height=SIZE.SMALL_BUTTON_LONG.h,
                pos=Pos(0, 0),
                corner_radius=self.corner_radius,
            )

            btn.pack(fill="both", expand=True, pady=5, ipadx=15)

        self.button_menu.update()

        menu_width = self.button_menu.winfo_reqwidth() / self.root._apply_widget_scaling(1)

        self.button_menu.place(
            x = WINDOW_WIDTH - SETTINGS_WINDOW_MARGIN - menu_width * 1.25,
            y = SETTINGS_WINDOW_MARGIN + 250,
        )

        # -------------------------- #

        self.cancel_button = CustomButton(
            master=self.root,
            text=STRINGS.SETTINGS_SCREEN.CLOSE,
            command=self.hide,
            font=FONT.LAUNCH_BUTTON,
            size=SIZE.LOGS_CLOSE,
            corner_radius=10,
            pos=Pos(WINDOW_MARGIN, WINDOW_HEIGHT - WINDOW_MARGIN - SIZE.LOGS_CLOSE.h),
        )

        self.cancel_button.show()

        # -------------------------- #

        self.version_label = CTkLabel(
            master=self.root,
            height=0,
            anchor="se",
            text=STRINGS.VERSION_LABEL,
            text_color=COLOR.WHITE,
            font=FONT.VERSION,
        )

        self.version_label.update()

        self.version_label.place(
            x = WINDOW_WIDTH  - WINDOW_MARGIN - self.version_label.winfo_reqwidth() / self.version_label._apply_widget_scaling(1),
            y = WINDOW_HEIGHT - WINDOW_MARGIN - self.version_label.winfo_reqheight() / self.version_label._apply_widget_scaling(1),
        )

        # -------------------------- #

        self.hide()

    def show(self, *args, **kwargs):
        self._visible = True

        self.root.place(
            x=OFFSET.SETTINGS_PANEL.x,
            y=OFFSET.SETTINGS_PANEL.y,
        )

        self.root.lift()

        self.bind = self.master.bind("<Escape>", self.hide)

    def hide(self, *args, **kwargs):
        if self.master.grab_current() is not None:
            return # Not in focus...

        if self.language_dropdown.selected_code != STRINGS.current_language_code:
            restarting, _ = self.master.restart_popup.create(STRINGS.SETTINGS_SCREEN.RESTART_REQUIRED)
            
            if restarting:
                return # Don't do anything...

        self._visible = False
        self.root.place_forget()

        if self.bind:
            self.master.unbind("<Escape>", self.bind)
            self.bind = None

    def on_arguments_textbox_key(self, *args, **kwargs):
        text = self.arguments_entry.get("1.0", END)

        self.master.settings.set_delayed(Settings.LAUNCH_OPTIONS, text.strip())

        # Remove existing tags
        self.arguments_entry.tag_remove("goodoption", "1.0", END)
        self.arguments_entry.tag_remove("badoption", "1.0", END)

        matches = self.arguments_entry.highlight_pattern.finditer(text)

        for match in matches:
            start, end = match.span()
            matched_word = match.group(1)[1:] # No prefix symbol.
            tag = matched_word in INVALID_TEXTBOX_ARGS and "badoption" or "goodoption"

            self.arguments_entry.tag_add(tag, f"1.0+{start}c", f"1.0+{end}c")

    def _on_tray_toggle(self):
        enabled = self.tray_switch.get()
        self.master.settings.set(Settings.MINIMIZE_TO_TRAY, enabled)
        self.master._update_tray()

    def _on_auto_launch_toggle(self):
        enabled = self.auto_launch_switch.get()
        self.master.settings.set(Settings.AUTO_LAUNCH, enabled)