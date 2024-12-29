# from app import app

# if __name__ == "__main__":
#     app.run(debug=True)

from app import app, fleact

if __name__ == "__main__":
    fleact.socketio.run(app, debug=True)
