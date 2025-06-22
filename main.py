import sys
from PyQt5.QtWidgets import QApplication
from process_flow_editor import ProcessFlowEditor

def main():
    app = QApplication(sys.argv)
    window = ProcessFlowEditor()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
   main()