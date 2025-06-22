import tkinter as tk
from tkinter import ttk
import random
import threading
import time
import os

class Jogo:
    def __init__(self, master):
        self.master = master
        self.master.title("Pega-Toupeiras")
        self.master.configure(bg="#2C3E50")

        self.nivel = 1
        self.pontuacao = 0
        self.total_toupeiras = 10
        self.toupeiras_restantes = self.total_toupeiras
        self.qtd_tocas = 6
        self.tempo_entre_toupeiras = 2.5

        self.tocas = []
        self.botoes_tocas = []

        self.semaforo = threading.Semaphore(1)

        self.tela_boas_vindas()

    def tela_boas_vindas(self):
        self.limpar_tela()
        label = tk.Label(self.master, text="Bem-vindo ao Pega-Toupeiras!", font=("Helvetica", 24, "bold"), fg="#1ABC9C", bg="#2C3E50")
        label.pack(pady=20)

        def piscar_texto():
            cor = label.cget("fg")
            nova_cor = "#ECF0F1" if cor == "#1ABC9C" else "#1ABC9C"
            label.config(fg=nova_cor)
            self.master.after(500, piscar_texto)

        piscar_texto()

        botao = tk.Button(self.master, text="Iniciar Jogo", command=self.iniciar_jogo,
                          font=("Helvetica", 14, "bold"), bg="#1ABC9C", fg="white",
                          activebackground="#16A085")
        botao.pack(pady=10)

        botao.bind("<Enter>", lambda e: botao.config(bg="#16A085"))
        botao.bind("<Leave>", lambda e: botao.config(bg="#1ABC9C"))

    def iniciar_jogo(self):
        self.limpar_tela()
        self.tocas = [False] * self.qtd_tocas
        self.toupeiras_restantes = self.total_toupeiras

        self.label_pontuacao = tk.Label(self.master, text=f"Pontuação: {self.pontuacao}",
                                        font=("Helvetica", 14), fg="white", bg="#2C3E50")
        self.label_pontuacao.pack(pady=10)

        self.label_restantes = tk.Label(self.master, text=f"Toupeiras restantes: {self.toupeiras_restantes}",
                                        font=("Helvetica", 12), fg="#ECF0F1", bg="#2C3E50")
        self.label_restantes.pack()

        self.barra_tempo = ttk.Progressbar(self.master, length=200, mode='determinate')
        self.barra_tempo.pack(pady=5)

        container = tk.Frame(self.master, bg="#2C3E50")
        container.pack(expand=True)

        self.campo = tk.Frame(container, bg="#2C3E50")
        self.campo.pack()

        self.botoes_tocas = []
        colunas = min(self.qtd_tocas, 6)
        for i in range(self.qtd_tocas):
            canvas = tk.Canvas(self.campo, width=80, height=80, bg="#2C3E50", highlightthickness=0)
            canvas.grid(row=i // colunas, column=i % colunas, padx=5, pady=5)
            self.desenhar_toca(canvas)
            canvas.bind("<Button-1>", lambda e, i=i: self.clicar_toupeira(i))
            self.botoes_tocas.append(canvas)

        threading.Thread(target=self.controlar_toupeiras, daemon=True).start()
        threading.Thread(target=self.atualizar_barra_tempo, daemon=True).start()

    def desenhar_toca(self, canvas):
        canvas.delete("all")
        canvas.create_oval(10, 30, 70, 60, fill="#3E2723", outline="#1B0F0A")

    def desenhar_toupeira(self, canvas):
        # Cabeça
        canvas.create_oval(25, 10, 55, 40, fill="#8D5524", outline="")
        # Nariz
        canvas.create_oval(37, 20, 43, 26, fill="#D2691E", outline="")
        # Olhos
        canvas.create_oval(32, 15, 36, 19, fill="black")
        canvas.create_oval(44, 15, 48, 19, fill="black")

    def atualizar_barra_tempo(self):
        tempo_total = self.total_toupeiras * self.tempo_entre_toupeiras
        passos = 100
        for i in range(passos):
            time.sleep(tempo_total / passos)
            self.barra_tempo["value"] = (i + 1)

    def controlar_toupeiras(self):
        threads = []
        for _ in range(self.total_toupeiras):
            t = threading.Thread(target=self.aparecer_toupeira)
            t.start()
            threads.append(t)
            time.sleep(self.tempo_entre_toupeiras)

        for t in threads:
            t.join()

        self.master.after(0, self.fim_de_nivel)

    def aparecer_toupeira(self):
        with self.semaforo:
            idx = random.randint(0, self.qtd_tocas - 1)
            self.tocas[idx] = True
            self.master.after(0, self.atualizar_toca, idx, True)
            time.sleep(1)
            self.tocas[idx] = False
            self.master.after(0, self.atualizar_toca, idx, False)
            self.toupeiras_restantes -= 1
            self.master.after(0, self.label_restantes.config, {"text": f"Toupeiras restantes: {self.toupeiras_restantes}"})

    def atualizar_toca(self, idx, status):
        canvas = self.botoes_tocas[idx]
        canvas.delete("all")
        if status:
            self.desenhar_toca(canvas)
            self.desenhar_toupeira(canvas)
        else:
            self.desenhar_toca(canvas)

    def clicar_toupeira(self, idx):
        if self.tocas[idx]:
            self.pontuacao += 1
            self.label_pontuacao.config(text=f"Pontuação: {self.pontuacao}")
            self.tocas[idx] = False
            self.atualizar_toca(idx, False)

    def fim_de_nivel(self):
        if self.nivel >= 8:
            self.tela_fim_jogo()
            return

        self.nivel += 1
        self.qtd_tocas += 3
        self.total_toupeiras = max(3, self.total_toupeiras - 2)
        self.tempo_entre_toupeiras = max(0.5, self.tempo_entre_toupeiras - 0.25)

        self.limpar_tela()
        label = tk.Label(self.master, text=f"Nível {self.nivel - 1} completo!", font=("Helvetica", 16, "bold"), fg="white", bg="#2C3E50")
        label.pack(pady=20)
        botao = tk.Button(self.master, text="Próximo Nível", command=self.iniciar_jogo,
                          font=("Helvetica", 14, "bold"), bg="#1ABC9C", fg="white",
                          activebackground="#16A085")
        botao.pack(pady=10)
        botao.bind("<Enter>", lambda e: botao.config(bg="#16A085"))
        botao.bind("<Leave>", lambda e: botao.config(bg="#1ABC9C"))

    def tela_fim_jogo(self):
        self.limpar_tela()
        label = tk.Label(self.master, text="Fim de Jogo!", font=("Helvetica", 18, "bold"), fg="white", bg="#2C3E50")
        label.pack(pady=20)
        pontos = tk.Label(self.master, text=f"Pontuação final: {self.pontuacao}", font=("Helvetica", 14), fg="#ECF0F1", bg="#2C3E50")
        pontos.pack(pady=10)

    def limpar_tela(self):
        for widget in self.master.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    jogo = Jogo(root)
    root.mainloop()
