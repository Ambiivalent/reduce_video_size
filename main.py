import dearpygui.dearpygui as dpg
import os, subprocess, time

VIEW_WIDTH = 1280
VIEW_HEIGHT = 720
ffmpeg_command = "ffmpeg -i input.mp4 -vcodec libx265 -crf 28 output.mp4"
originalPath = os.getcwd()
filePath = None
totalVideos = 0

dpg.create_context()
dpg.create_viewport(title='Video Size Reducer', width=VIEW_WIDTH, height=VIEW_HEIGHT)

def centerItem(width, height, id):
    dpg.set_item_pos(id, [VIEW_WIDTH // 2 - width // 2, VIEW_HEIGHT // 2 - height // 2])

def grabFolderDataCallback(sender, app_data):
    global totalVideos, filePath
    print('OK was clicked.')
    print("Sender: ", sender)
    print("App Data: ", app_data)
    filePath = app_data['file_path_name']
    dpg.set_value("filePathTag", f"Current Filepath: {filePath}")

    specifyFileFormat = dpg.get_value("R1")
    selectAll = dpg.get_value("R2")
    extension = dpg.get_value("user_extension")

    os.chdir(filePath)

    if specifyFileFormat:
        for count, files in enumerate(os.listdir()):
            if files[-len(extension):] == extension:
                dpg.add_table_row(parent="videoTable", tag=f"videoItem{count}")
                dpg.add_selectable(label = files, parent=f"videoItem{count}")
                dpg.add_text(parent=f"videoItem{count}", tag=f"videoItemSelect", show=False)

    else:
        for count, files in enumerate(os.listdir()):
            dpg.add_table_row(parent="videoTable", tag=f"videoItem{count}")
            dpg.add_selectable(label = files, parent=f"videoItem{count}", callback=queueItem, user_data=count)
            dpg.add_text(files, parent=f"videoItem{count}", tag=f"videoItemSelect{count}", show=False)

    totalVideos = len(os.listdir())
    dpg.configure_item("executeBtn", show=True)
    

def cancel_callback(sender, app_data):
    print('Cancel was clicked.')

def save_callback(sender,app_data):
    ffmpeg_command = dpg.get_value("command_line")
    dpg.set_value("command_line", ffmpeg_command)

def selectAll(sender,app_data):
    for index in range(totalVideos):
        tag = f"videoItemSelect{index}"
        dpg.configure_item(tag, show=not dpg.get_item_configuration(tag)['show'])

def reduceVideo(sender, app_data):
    os.chdir(originalPath)
    for index in range(totalVideos):
        tag = f"videoItemSelect{index}"
        if dpg.get_item_configuration(tag)['show']:
            video = dpg.get_value(tag)
            command = ffmpeg_command.replace("input.mp4", "\""+ filePath + "\\" + video + "\"")
            command = command.replace("output.mp4", f"\"reduced{video}\"")
            dpg.configure_item("loadingScreen", show=True)
            subprocess.call(f"{command}", shell=True)
    dpg.configure_item("loadingScreen", show=False)
    time.sleep(0.5)
    dpg.configure_item("success_id", show=True)


def queueItem(sender, app_data, index):
    tag = f"videoItemSelect{index}"
    dpg.configure_item(tag, show=not dpg.get_item_configuration(tag)['show'])

dpg.add_file_dialog(
    directory_selector=True, show=False, callback=grabFolderDataCallback, tag="file_dialog_id",
    cancel_callback=cancel_callback, width=700 ,height=400)

with dpg.window(label="Help", modal=True, show=False, tag="help_window_id", width=640, height=360):
    dpg.add_text("""Open a file directory and choose settings to reduce file size\n\n
                File -> Open\n\nBuilt with Python, DearPyGUI and ffmpeg\nVersion 1.0\nBrian Hoang""")
    centerItem(dpg.get_item_width("help_window_id"), dpg.get_item_height("help_window_id"), "help_window_id")

with dpg.window(label="Edit Command", modal=True, show=False, tag="command_id", width=640, height=360):
    dpg.add_text("WARNING - DO NOT EDIT IF YOU ARE UNSURE ABOUT WHAT YOU ARE DOING", color=(255,0,0))
    dpg.add_text("Alter the FFMPEG Command that is ran on each file:")
    dpg.add_input_text(label="FFMPEG Command", default_value=f"{ffmpeg_command}", tag="command_line")
    dpg.add_button(label="Save", callback=save_callback)
    centerItem(dpg.get_item_width("command_id"), dpg.get_item_height("command_id"), "command_id")

with dpg.window(label="Success", modal=True, show=False, tag="success_id", width=640, height=360):
    dpg.add_text("Videos successfully reduced in filesize.")
    centerItem(dpg.get_item_width("success_id"), dpg.get_item_height("success_id"), "success_id")

with dpg.window(label="Loading...", modal=True, show=False, tag="loadingScreen", width=640, height=360):
    dpg.add_loading_indicator()
    centerItem(dpg.get_item_width("loadingScreen"), dpg.get_item_height("loadingScreen"), "loadingScreen")

with dpg.window(label="Select a file directory", tag="primaryWindow"):
    with dpg.menu_bar():
        with dpg.menu(label="File"):
            dpg.add_menu_item(label="Open", callback=lambda: dpg.show_item("file_dialog_id"))
            dpg.add_menu_item(label="Command", callback=lambda: dpg.show_item("command_id"))

        with dpg.menu(label="About"):
            dpg.add_menu_item(label="Help", callback=lambda: dpg.configure_item("help_window_id", show=True))
            dpg.add_menu_item(label="Version 1.0")
    dpg.add_text(f"Current Filepath: {filePath}", tag="filePathTag")
    
    dpg.add_separator()

    dpg.add_checkbox(label="Specify File Extension", tag="R1", callback=lambda: dpg.configure_item("user_extension", enabled = not(dpg.get_item_configuration("user_extension")["enabled"])))
    dpg.add_input_text(label="", default_value=".mp4", tag="user_extension", enabled=False)
    dpg.add_checkbox(label="Select All Files", tag="R2", callback=selectAll)
    dpg.add_text("")

    with dpg.table(tag="videoTable"):
        dpg.add_table_column(label="Videos")
        dpg.add_table_column(label="Converted Videos")
    
    dpg.add_button(label="Execute", callback=reduceVideo, show=False, tag="executeBtn")

dpg.setup_dearpygui()

with dpg.theme() as disabled_theme:
    with dpg.theme_component(dpg.mvInputText, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_Text, (60, 60, 60), category=dpg.mvThemeCat_Core)

dpg.bind_theme(disabled_theme)

dpg.show_viewport()
dpg.set_primary_window("primaryWindow", True)
dpg.start_dearpygui()
dpg.destroy_context()