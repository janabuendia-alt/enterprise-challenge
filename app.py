from flask import Flask, render_template, request, send_file
from fmea_engine import generate_fmea
from excel_formatter import create_fmea_excel
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        form_data = request.form.to_dict()

        # Generar análisis FMEA con IA
        fmea_data = generate_fmea(form_data)

        # Crear Excel con la nueva capçalera (passem form_data sencer)
        file_path = create_fmea_excel(fmea_data, form_data)

        return send_file(file_path, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    # El servidor públic ens assignarà un port automàticament
    port = int(os.environ.get("PORT", 5001))
    # '0.0.0.0' permet que la web sigui visible a tot internet
    app.run(host='0.0.0.0', port=port)
