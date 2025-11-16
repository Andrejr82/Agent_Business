import logging
from functools import wraps
import os
from flask import Flask, redirect, render_template, request, session, url_for


class WebServer:
    def __init__(self, host="127.0.0.1", port=5000):
        # FLASK_AVAILABLE check is removed as Flask is directly imported here
        self.host = host
        self.port = port

        base_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        self.app = Flask(
            "server",
            template_folder=os.path.join(base_dir, "web", "templates"),
            static_folder=os.path.join(base_dir, "web", "static"),
        )
        self.app.config["DEBUG"] = True
        self.app.config["SECRET_KEY"] = os.getenv(
            "SECRET_KEY", "chave_secreta_component_factory"
        )
        self._running = False

        # Placeholder para usuários (similar ao servidor_integrado.py)
        self.USERS = {
            "admin": {"password": "admin123", "name": "Administrador CF"},
            "usuario": {"password": "senha123", "name": "Usuário Padrão CF"},
        }

        self._setup_routes()

    # Decorator para verificar se o usuário está logado
    def _login_required(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "username" not in session:
                return redirect(
                    url_for("login_route")
                )
            return f(*args, **kwargs)

        return decorated_function

    def _setup_routes(self):
        @self.app.route("/")
        @self._login_required
        def index():
            return render_template("index.html", username=session.get("name", ""))

        @self.app.route("/login", methods=["GET", "POST"])
        def login_route():
            error = None
            if request.method == "POST":
                username = request.form.get("username")
                password = request.form.get("password")
                if (
                    username in self.USERS
                    and self.USERS[username]["password"] == password
                ):
                    session["username"] = username
                    session["name"] = self.USERS[username]["name"]
                    logging.getLogger("WebServer").info(
                        f"Login bem-sucedido para o usuário: {username} via ComponentFactory"
                    )
                    return redirect(url_for("index"))
                else:
                    error = "Usuário ou senha incorretos"
                    logging.getLogger("WebServer").warning(
                        f"Tentativa de login falhou para o usuário: {username} via ComponentFactory"
                    )
            return render_template("login.html", error=error)

        @self.app.route("/logout")
        def logout_route():
            session.pop("username", None)
            session.pop("name", None)
            logging.getLogger("WebServer").info(
                "Usuário deslogado via ComponentFactory"
            )
            return redirect(url_for("login_route"))

        # Registra as rotas da API
        try:
            from core.api import register_routes

            register_routes(self.app)
            import logging

            logging.getLogger("WebServer").info(
                "Rotas da API registradas com sucesso")
        except Exception as e:
            import logging

            logging.getLogger("WebServer").error(
                f"Erro ao registrar rotas da API: {e}")

    def run(self, host=None, port=None, **kwargs):
        """Inicia o servidor Flask de forma síncrona (compatível com Flask)"""
        try:
            host = host or self.host
            port = port or self.port
            self._running = True
            from core.utils.event_manager import EventManager
            EventManager.notify("web.server.started", {
                                "port": port, "host": host})
            self.app.run(
                host=host, port=port, debug=True, use_reloader=True
            )
            return True
        except Exception as e:
            logging.getLogger("WebServer").error(
                f"Erro ao iniciar o servidor web: {e}")
            self._running = False
            return False
