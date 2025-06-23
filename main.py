import sys
from PyQt5.QtWidgets import QApplication
from UI_Interface.main_window import ProcessFlowEditor

def main():
    """
    Entry point for the application.
    - Initializes the QApplication.
    - Creates and shows the main window.
    - Starts the event loop.
    """
    app = QApplication(sys.argv)
    window = ProcessFlowEditor()  # Main application window
    window.show()
    sys.exit(app.exec_())  # Start the Qt event loop

if __name__ == "__main__":
    # Run the main function if this script is executed directly
    main()
