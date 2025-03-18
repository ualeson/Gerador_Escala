from flask import Flask, render_template, request, send_file, redirect, url_for, flash # type: ignore
from datetime import datetime, timedelta
import calendar
import os
import random


app = Flask(__name__)
app.secret_key = "esse_sistema_e_para_gfort_mas_o_credito_e_do_ualeson"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        
        if "file" not in request.files:
            flash("Nenhum arquivo enviado!", "danger")
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            flash("Nenhum arquivo selecionado!", "danger")
            return redirect(request.url)

        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

           
            mes_ano = request.form.get("mes_ano") 
            ano, mes = map(int, mes_ano.split("-")) 
            dias_excluir = request.form.getlist("dias_excluir[]")
            dias_excluir = [int(d) for d in dias_excluir]  
            dias_selecionados = request.form.getlist("dias_selecionados[]")
            dias_selecionados = [int(d) for d in dias_selecionados] 

            
            horarios_semana = {}
            for i in range(7): 
                horarios_semana[i] = [
                    request.form.get(f"horario_{i}_1"),
                    request.form.get(f"horario_{i}_2"),
                    request.form.get(f"horario_{i}_3"),
                    request.form.get(f"horario_{i}_4"),
                ]

            
            arquivo_escala = gerar_escala(filepath, mes, ano, dias_excluir, dias_selecionados, horarios_semana)

            return send_file(arquivo_escala, as_attachment=True)

    return render_template("index.html")

def gerar_escala(filepath, mes, ano, dias_excluir, dias_selecionados, horarios_semana):
    """Gera a escala semanal excluindo os dias marcados e permitindo dias selecionados"""
    with open(filepath, "r") as f:
        
        matriculas = [linha.strip().zfill(10) for linha in f.readlines()]

    _, ultimo_dia = calendar.monthrange(ano, mes)
    arquivo_saida = os.path.join(UPLOAD_FOLDER, f"escala_gerada_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt")

    with open(arquivo_saida, "w") as f:
        for matricula in matriculas:
            for dia in range(1, ultimo_dia + 1):
                data = datetime(ano, mes, dia)
                if dia in dias_excluir or data.weekday() not in dias_selecionados:
                    continue  

                horarios_gerados = [gerar_horario_aleatorio(h) for h in horarios_semana[data.weekday()] if h]  

                for horario in horarios_gerados:
                    f.write(f"{matricula}, {data.strftime('%d/%m/%Y')}, {horario}\n")

    return arquivo_saida

def gerar_horario_aleatorio(horario):
    """Gera um horário aleatório com variação de minutos"""
    try:
        hora, minuto = map(int, horario.split(":"))
        variacao = random.randint(-5, 5)
        novo_minuto = minuto + variacao

        if novo_minuto < 0:
            novo_minuto += 60
            hora -= 1
        elif novo_minuto >= 60:
            novo_minuto -= 60
            hora += 1
        return f"{hora:02d}:{novo_minuto:02d}"
    except ValueError:
        return "00:00"

if __name__ == "__main__":
    app.run(debug=True)
