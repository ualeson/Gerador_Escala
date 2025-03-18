from flask import Flask, render_template, request, send_file, flash
import os
import calendar
import random
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "esse_sistema_e_para_gfort_mas_o_credito_e_do_ualeson"

def gerar_horario_aleatorio(horario):
    """Gera um horário aleatório baseado no original permitindo valores negativos corretamente"""
    try:
        hora, minuto = map(int, horario.split(":"))
        variacao = random.randint(-5, 5)
        novo_minuto = minuto + variacao
        nova_hora = hora

        if novo_minuto < 0:
            novo_minuto += 60
            nova_hora -= 1
        elif novo_minuto >= 60:
            novo_minuto -= 60
            nova_hora += 1

        
        if nova_hora < 0:
            nova_hora = 23
            novo_minuto = max(0, novo_minuto)  
        elif novo_minuto >= 60:
            novo_minuto = 59  

        return f"{nova_hora:02d}:{novo_minuto:02d}"
    except ValueError:
        return "00:00"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            flash("Nenhum arquivo enviado.", "danger")
            return render_template("index.html")

        file = request.files["file"]
        if file.filename == "":
            flash("Nenhum arquivo selecionado.", "danger")
            return render_template("index.html")

        matriculas = [linha.strip().zfill(10) for linha in file.read().decode("utf-8").splitlines()]
        
        data_selecionada = request.form["data"]  
        ano, mes = map(int, data_selecionada.split("-"))
        escala = request.form["escala"]
        par_impar = request.form["par_impar"]
        
        horarios = [
            request.form["horario0"],
            request.form["horario1"],
            request.form["horario2"],
            request.form["horario3"]
        ]

        arquivo_saida = "escala_trabalho.txt"

        try:
            _, ultimo_dia = calendar.monthrange(ano, mes)

            with open(arquivo_saida, "w") as file:
                for matricula in matriculas:
                    for dia in range(1, ultimo_dia + 1):
                        if (par_impar == "par" and dia % 2 == 0) or (par_impar == "ímpar" and dia % 2 != 0):
                            data = datetime(ano, mes, dia)
                            horarios_gerados = [gerar_horario_aleatorio(h) for h in horarios]

                            for i, horario in enumerate(horarios_gerados):
                                hora, _ = map(int, horario.split(":"))
                                
                                
                                if escala == "noturna" and i > 0 and hora < 12:
                                    data_saida = data + timedelta(days=1)
                                else:
                                    data_saida = data
                                
                                file.write(f"{matricula}, {data_saida.strftime('%d/%m/%Y')}, {horario}\n")

            return send_file(arquivo_saida, as_attachment=True)

        except Exception as e:
            flash(f"Erro ao gerar a escala: {e}", "danger")
            return render_template("index.html")

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
