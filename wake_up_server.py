from flask import Flask

def run_flask():
    app = Flask(__name__)

    @app.route('/wake-up', methods=['GET'])
    def wake_up():
        return 'OK', 200

    app.run(host='0.0.0.0', port=8080) 