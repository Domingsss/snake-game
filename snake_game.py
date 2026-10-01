"""Cobrinha: regras e interface Pygame."""
import json
import os
import random
from pathlib import Path

COLUNAS, LINHAS, CELULA = 28, 22, 24
LARGURA, ALTURA, TOPO = 720, 708, 112
DIFICULDADES = {"Fácil": 6, "Normal": 9, "Difícil": 13}
ARQUIVO = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "Cobrinha" / "recordes.json"


class Partida:
    def __init__(self, dificuldade="Normal", livre=False):
        self.dificuldade, self.livre = dificuldade, livre
        self.cobra = [(7, 10), (6, 10), (5, 10)]
        self.direcao = self.proxima = (1, 0)
        self.virou = self.terminou = self.venceu = False
        self.pontos = 0
        self.comida = self.sortear_comida()

    @property
    def nivel(self):
        return self.pontos // 50 + 1

    @property
    def velocidade(self):
        return min(22, DIFICULDADES[self.dificuldade] + self.nivel - 1)

    def sortear_comida(self):
        ocupadas = set(self.cobra)
        livres = [(x, y) for x in range(COLUNAS) for y in range(LINHAS) if (x, y) not in ocupadas]
        return random.choice(livres) if livres else None

    def virar(self, direcao):
        if self.virou or direcao == self.direcao:
            return
        if direcao != (-self.direcao[0], -self.direcao[1]):
            self.proxima, self.virou = direcao, True

    def avancar(self):
        if self.terminou:
            return
        self.direcao, self.virou = self.proxima, False
        x, y = (self.cobra[0][i] + self.direcao[i] for i in (0, 1))
        if self.livre:
            x, y = x % COLUNAS, y % LINHAS
        elif not (0 <= x < COLUNAS and 0 <= y < LINHAS):
            self.terminou = True
            return
        cabeca = (x, y)
        comeu = cabeca == self.comida
        if cabeca in (self.cobra if comeu else self.cobra[:-1]):
            self.terminou = True
            return
        self.cobra.insert(0, cabeca)
        if comeu:
            self.pontos += 10
            self.comida = self.sortear_comida()
            if self.comida is None:
                self.terminou = self.venceu = True
        else:
            self.cobra.pop()


def carregar_recordes(caminho=ARQUIVO):
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        if isinstance(dados, dict):
            return {k: v for k, v in dados.items() if type(v) is int and v >= 0}
    except (OSError, ValueError):
        pass
    return {}


def salvar_recordes(dados, caminho=ARQUIVO):
    try:
        caminho.parent.mkdir(parents=True, exist_ok=True)
        temporario = caminho.with_suffix(".tmp")
        temporario.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
        temporario.replace(caminho)
        return True
    except OSError:
        return False


def snake_game():
    import pygame

    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Cobrinha • Arcade")
    fontes = {n: pygame.font.SysFont("segoeui", n, bold=n >= 28) for n in (16, 20, 28, 48)}
    relogio = pygame.time.Clock()
    fundo, branco, cinza, verde = (13, 19, 32), (231, 239, 247), (145, 163, 184), (77, 222, 154)
    recordes = carregar_recordes()
    dificuldade, livre = "Normal", False
    partida = Partida()
    estado, acumulado, rodando, erro = "menu", 0, True, False
    teclas = {pygame.K_UP: (0, -1), pygame.K_w: (0, -1),
              pygame.K_DOWN: (0, 1), pygame.K_s: (0, 1),
              pygame.K_LEFT: (-1, 0), pygame.K_a: (-1, 0),
              pygame.K_RIGHT: (1, 0), pygame.K_d: (1, 0)}

    def texto(conteudo, tamanho, cor, pos, centro=False):
        imagem = fontes[tamanho].render(conteudo, True, cor)
        tela.blit(imagem, imagem.get_rect(center=pos) if centro else pos)

    try:
        while rodando:
            delta = min(relogio.tick(60) / 1000, .1)
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    rodando = False
                elif evento.type == pygame.WINDOWFOCUSLOST and estado == "jogando":
                    estado, acumulado = "pausa", 0
                elif evento.type == pygame.KEYDOWN:
                    t = evento.key
                    if t == pygame.K_ESCAPE:
                        if estado == "menu":
                            rodando = False
                        else:
                            estado = "menu"
                    elif estado == "menu":
                        if t in (pygame.K_1, pygame.K_2, pygame.K_3):
                            dificuldade = list(DIFICULDADES)[t - pygame.K_1]
                        elif t == pygame.K_m:
                            livre = not livre
                        elif t in (pygame.K_RETURN, pygame.K_SPACE):
                            partida = Partida(dificuldade, livre)
                            estado, acumulado = "jogando", 0
                    elif t == pygame.K_r or (estado == "fim" and t == pygame.K_RETURN):
                        partida = Partida(dificuldade, livre)
                        estado, acumulado = "jogando", 0
                    elif t in (pygame.K_p, pygame.K_SPACE) and estado in ("jogando", "pausa"):
                        estado = "pausa" if estado == "jogando" else "jogando"
                        acumulado = 0
                    elif estado == "jogando" and t in teclas:
                        partida.virar(teclas[t])
            chave = f"{dificuldade}:{livre}"
            if estado == "jogando":
                acumulado += delta
                while acumulado >= 1 / partida.velocidade:
                    acumulado -= 1 / partida.velocidade
                    partida.avancar()
                    if partida.pontos > recordes.get(chave, 0):
                        recordes[chave] = partida.pontos
                        erro = not salvar_recordes(recordes)
                    if partida.terminou:
                        estado = "fim"
                        break
            tela.fill(fundo)
            texto("COBRINHA", 28, verde, (24, 18))
            texto(f"{dificuldade} / {'Bordas livres' if livre else 'Com paredes'}", 16, cinza, (24, 60))
            texto(f"PONTOS {partida.pontos:03}", 20, branco, (330, 22))
            texto(f"RECORDE {recordes.get(chave, 0):03}", 20, verde, (510, 22))
            texto(f"Nível {partida.nivel} • +10 por fruta", 16, cinza, (330, 60))
            for x in range(COLUNAS):
                for y in range(LINHAS):
                    cor = (22, 32, 46) if (x + y) % 2 else (25, 36, 50)
                    pygame.draw.rect(tela, cor, (24 + x * CELULA, TOPO + y * CELULA, CELULA, CELULA))
            if partida.comida:
                x, y = partida.comida
                pygame.draw.circle(tela, (250, 108, 116), (36 + x * CELULA, TOPO + 12 + y * CELULA), 8)
            for i, (x, y) in enumerate(partida.cobra):
                ret = pygame.Rect(25 + x * CELULA, TOPO + 1 + y * CELULA, 22, 22)
                pygame.draw.rect(tela, verde if i == 0 else (40, 163, 119), ret, border_radius=6)
                if i == 0:
                    dx, dy = partida.direcao
                    for lado in (-1, 1):
                        pygame.draw.circle(tela, fundo, (ret.centerx + dx * 5 + dy * lado * 5, ret.centery + dy * 5 + dx * lado * 5), 2)
            texto("Setas / WASD: mover    P / Espaço: pausa    R: reiniciar    Esc: menu", 16, cinza, (360, 668), True)
            if erro:
                texto("Não foi possível salvar o recorde no disco.", 16, (250, 108, 116), (360, 692), True)
            if estado != "jogando":
                sombra = pygame.Surface((LARGURA, LINHAS * CELULA), pygame.SRCALPHA)
                sombra.fill((8, 13, 24, 220))
                tela.blit(sombra, (0, TOPO))
                if estado == "menu":
                    itens = [("Uma fruta de cada vez.", 28, verde, 220),
                             ("COBRINHA", 48, branco, 282),
                             ("Coma, cresça e supere seu recorde.", 20, cinza, 340),
                             ("1 Fácil     2 Normal     3 Difícil", 20, branco, 400),
                             (f"Selecionado: {dificuldade}", 20, verde, 437),
                             (f"M: bordas {'livres' if livre else 'com paredes'}", 20, branco, 480),
                             ("ENTER para jogar", 28, verde, 550)]
                elif estado == "pausa":
                    itens = [("PAUSA", 48, branco, 320), ("P ou Espaço para continuar", 20, verde, 390)]
                else:
                    itens = [("VOCÊ VENCEU!" if partida.venceu else "FIM DE JOGO", 48, branco, 300),
                             (f"{partida.pontos} pontos • Nível {partida.nivel}", 28, verde, 368),
                             ("Enter ou R: jogar novamente", 20, branco, 430),
                             ("Esc: escolher dificuldade e modo", 20, cinza, 468)]
                for mensagem, tamanho, cor, y in itens:
                    texto(mensagem, tamanho, cor, (360, y), True)
            pygame.display.flip()
    finally:
        pygame.quit()


if __name__ == "__main__":
    snake_game()
