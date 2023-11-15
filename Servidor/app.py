from flask import Flask
from flask_assets import Environment, Bundle
from controller.funcionario_controller import controller_bp as funcionario_bp
from controller.veiculo_controller import controller_bp as veiculo_bp
from controller.acesso_controller import controller_bp as aceesso_bp

app = Flask(__name__)
assets = Environment(app)

css_bundle = Bundle("scss/estilo.scss", filters="libsass", output="css/site.css")
assets.register("css_bundle", css_bundle)

app.register_blueprint(aceesso_bp, url_prefix="/")
app.register_blueprint(funcionario_bp, url_prefix="/funcionario")
app.register_blueprint(veiculo_bp, url_prefix="/veiculo")

if __name__ == "__main__":
    app.debug = True
    app.run()
