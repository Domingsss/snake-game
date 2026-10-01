# Cobrinha

## Executar

Requer Python 3.10 ou superior.

```powershell
python -m pip install -r requirements.txt
python title.py
```

Também funciona com `python snake_game.py`.

## Controles e recursos

| Controle | Função |
| --- | --- |
| Enter | Iniciar ou jogar novamente |
| Setas / WASD | Mover a cobra |
| P / Espaço | Pausar e continuar |
| R | Reiniciar |
| Esc | Voltar ao menu; no menu, sair |
| 1 / 2 / 3 no menu | Fácil / Normal / Difícil |
| M no menu | Alternar paredes e bordas livres |

- Frutas dão 10 pontos e aumentam a cobra. A cada 50 pontos, o nível sobe e a velocidade aumenta, até 22 passos por segundo.
- Com paredes, bater na borda encerra a partida. Com bordas livres, a cobra reaparece no lado oposto.
- Colidir com o próprio corpo encerra a partida. Não é permitido inverter a direção diretamente ou fazer duas curvas no mesmo passo.
- Comida aparece apenas em células livres. Preencher o tabuleiro inteiro resulta em vitória.
- Ao perder o foco da janela, o jogo pausa automaticamente.
- Recordes separados por modo e dificuldade são salvos em `%LOCALAPPDATA%\Cobrinha\recordes.json` (ou `~/Cobrinha/recordes.json` quando a variável não existe). Falhas de gravação aparecem na tela e não interrompem a partida.
- Menu e jogo usam uma única janela Pygame.

## Testar as regras

```powershell
python -m unittest discover -s tests -v
```
