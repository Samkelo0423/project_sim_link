import sys
from PyQt5.QtWidgets import QApplication
from UI_Interface.main_window import ProcessFlowEditor

def main():
    """
    Entry point for the application.
    - Initializes the QApplication.
    - Creates and shows the main window.
    - Starts the event loop.

    How:
        - QApplication is required for any PyQt5 application; it manages application-wide resources and settings.
        - ProcessFlowEditor is your custom main window class (imported from UI_Interface.main_window).
        - window.show() makes the main window visible on the screen.
        - sys.exit(app.exec_()) starts the Qt event loop and ensures a clean exit when the window is closed.
    """
    app = QApplication(sys.argv)
    window = ProcessFlowEditor()  # Main application window
    window.show()
    sys.exit(app.exec_())  # Start the Qt event loop

if __name__ == "__main__":
    # Run the main function if this script is executed directly
    main()
