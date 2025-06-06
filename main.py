import tkinter as tk
import random
import threading
import time

class Jogo:
    def __init__(self, master):
        self.master = master
        self.master.title("Pega-Toupeiras")

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
        label = tk.Label(self.master, text="Bem-vindo ao Pega-Toupeiras!", font=("Arial", 18))
        label.pack(pady=20)
        botao = tk.Button(self.master, text="Iniciar Jogo", command=self.iniciar_jogo, font=("Arial", 14))
        botao.pack(pady=10)

    def iniciar_jogo(self):
        self.limpar_tela()
        self.tocas = [False] * self.qtd_tocas
        self.toupeiras_restantes = self.total_toupeiras

        self.label_pontuacao = tk.Label(self.master, text=f"Pontuação: {self.pontuacao}", font=("Arial", 14))
        self.label_pontuacao.pack(pady=10)

        self.label_restantes = tk.Label(self.master, text=f"Toupeiras restantes: {self.toupeiras_restantes}", font=("Arial", 12))
        self.label_restantes.pack()

        container = tk.Frame(self.master)
        container.pack(expand=True)

        self.campo = tk.Frame(container)
        self.campo.pack()

        self.botoes_tocas = []
        colunas = min(self.qtd_tocas, 6)
        for i in range(self.qtd_tocas):
            canvas = tk.Canvas(self.campo, width=80, height=80, bg="#8B4513", highlightthickness=0)
            canvas.grid(row=i // colunas, column=i % colunas, padx=5, pady=5)
            canvas.bind("<Button-1>", lambda e, i=i: self.clicar_toupeira(i))
            self.botoes_tocas.append(canvas)

        threading.Thread(target=self.controlar_toupeiras, daemon=True).start()

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
            canvas.create_oval(20, 20, 60, 60, fill="#A9A9A9", outline="")
        else:
            canvas.config(bg="#8B4513")

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
        label = tk.Label(self.master, text=f"Nível {self.nivel - 1} completo!", font=("Arial", 16))
        label.pack(pady=20)
        botao = tk.Button(self.master, text="Próximo Nível", command=self.iniciar_jogo, font=("Arial", 14))
        botao.pack(pady=10)

    def tela_fim_jogo(self):
        self.limpar_tela()
        label = tk.Label(self.master, text="Fim de Jogo!", font=("Arial", 18))
        label.pack(pady=20)
        pontos = tk.Label(self.master, text=f"Pontuação final: {self.pontuacao}", font=("Arial", 14))
        pontos.pack(pady=10)

    def limpar_tela(self):
        for widget in self.master.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    jogo = Jogo(root)
    root.mainloop()
