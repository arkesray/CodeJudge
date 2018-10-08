from CodeJudge import app
from waitress import serve


if __name__ == '__main__':
    app.run( host = '0.0.0.0')
    #serve(app)