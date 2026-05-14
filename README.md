# RGB -> HSV (OpenGL + Python)

Este programa permite selecionar uma imagem RGB, converter para HSV e visualizar o resultado em uma janela OpenGL. Existem dois modos de visualizacao HSV:

- HSV para exibicao (convertido de volta para RGB): aparencia natural na tela.
- HSV bruto (H,S,V mostrados como R,G,B): cores falsas para inspeção técnica dos canais.

## Como executar

1) Crie/ative um ambiente Python (opcional, mas recomendado)
2) Instale dependências:

```
pip install -r requirements.txt
```

3) Rode o programa:

```
python main.py
```

## Controles

- `o`: abrir imagem
- `1`: visualizar RGB (original)
- `2`: visualizar HSV convertido para RGB (cores naturais)
- `3`: visualizar HSV bruto (canais H, S e V como cores falsas)
- `s`: salvar a imagem HSV
- `q` ou `Esc`: sair

## Explicação dos parâmetros 0, 2 e 4 no Hue

Na conversao RGB -> HSV, o valor de Hue (H) é calculado em setores de 60 graus, dependendo de qual canal (R, G ou B) é o máximo. O termo adicionado (0, 2 ou 4) desloca o Hue para o setor correto do círculo de cores:

- **0**: quando o maximo é **R**. O Hue baseia-se em $(G - B) / \Delta$ e fica no setor [0, 60) graus.
- **2**: quando o maximo é **G**. O Hue usa $(B - R) / \Delta$ e é deslocado para o setor [120, 180) graus.
- **4**: quando o maximo é **B**. O Hue usa $(R - G) / \Delta$ e é deslocado para o setor [240, 300) graus.

Onde $\Delta = max(R,G,B) - min(R,G,B)$. Esses deslocamentos garantem que o Hue percorra corretamente o círculo de cores (0 a 360 graus) ao mudar o canal dominante.

## Referência

https://embarcados.com.br/processamento-de-imagens-com-opencv-no-raspberry-pi-zero/
