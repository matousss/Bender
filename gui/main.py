import os

import PySimpleGUI
from dotenv import load_dotenv

load_dotenv()

PySimpleGUI.theme('DarkAmber')

testbutton = PySimpleGUI.Button('Ok', key="troll")
layout = [[PySimpleGUI.Text('Some text on Row 1')],
          [PySimpleGUI.Text('Enter something on Row 2'), PySimpleGUI.InputText()],
          [testbutton, PySimpleGUI.Button('Cancel')]]

window = PySimpleGUI.Window('Bender ' + os.environ.get("VERSION"), layout, enable_close_attempted_event=True)




#def confirm():
    # confirm_window = PySimpleGUI.Window('', [[PySimpleGUI.Text("Are you sure you want exit?")],
    #                                          [PySimpleGUI.Button("Exit", key="CLOSE_APP"),
    #                                           PySimpleGUI.Button("Cancel")]], )
    # while True:
    #     event, values = confirm_window.read()
    #     if event == "CLOSE_APP":
    #         confirm_window.close()
    #         return True
    #
    #     if event == "Cancel":
    #         confirm_window.close()
    #         return False
    #     if event == PySimpleGUI.WIN_CLOSED:
    #         break


while True:
    event, values = window.read()
    print(str(event))
    if event == PySimpleGUI.WIN_CLOSED:
        break
    if event == PySimpleGUI.WINDOW_CLOSE_ATTEMPTED_EVENT and PySimpleGUI.popup_ok_cancel("Are you sure you want to exit?",
                                                                                         keep_on_top=True, title="") == "OK":
        break


window.close()
