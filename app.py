# app.py
from shiny import App
from app_controller import AppController

def create_app():
    controller = AppController()
    app = App(ui=controller.ui, server=controller.server)
    return app

app = create_app()

if __name__ == "__main__":
    app.run()
