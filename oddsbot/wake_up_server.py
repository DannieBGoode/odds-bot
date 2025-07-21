from flask import Flask


def run_flask():
    app = Flask(__name__)

    @app.route("/wake-up", methods=["GET"])
    def wake_up():
        return (
            "<html><body><h1>OK</h1></body></html>",
            200,
            {"Content-Type": "text/html"},
        )

    app.run(host="0.0.0.0", port=8080)


if __name__ == "__main__":
    run_flask()
