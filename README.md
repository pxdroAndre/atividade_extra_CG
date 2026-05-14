# Atividade: Conversão RGB para HSV (Versão Web)

Dupla:
- Pedro André da Silva Neto
- Walter Soares Costa Neto

Este projeto é uma aplicação web pura (HTML, CSS e JavaScript) desenvolvida para carregar uma imagem no formato RGB, convertê-la para o espaço de cores HSV e permitir a manipulação direta dos valores de Matiz, Saturação e Brilho.

## 🚀 Como Executar

Por ser uma aplicação web baseada puramente no lado do cliente, você **não precisa instalar nada** (nem Python, nem Node.js, nem bibliotecas externas).

1. Extraia/Baixe os arquivos deste repositório.
2. Dê um duplo clique no arquivo `index.html`.
3. O projeto abrirá no seu navegador padrão (Google Chrome, Edge, Firefox, etc.).
4. Clique em "Escolher Imagem RGB", selecione qualquer imagem do seu computador e brinque com os controles deslizantes.

## 🛠️ Tecnologias Utilizadas

- **HTML5**: Estrutura da página.
- **CSS3**: Estilização moderna e responsiva (Dark Mode).
- **Vanilla JavaScript**: Lógica do algoritmo de conversão e manipulação dos pixels frame a frame usando a API do `<canvas>`.

## 📚 A Teoria: Parâmetros 0, 2 e 4 no cálculo do Hue (Matiz)

Uma das exigências da atividade é compreender o uso matemático dos valores 0, 2 e 4. 

No algoritmo de conversão do espaço de cores RGB para HSV, a componente **Matiz (Hue)** é calculada com base em qual dos três canais (R, G ou B) possui a intensidade máxima. O resultado é mapeado para um ângulo em um círculo cromático (ou hexágono) de 0° a 360°.

Como o círculo possui 360 graus e temos 3 cores primárias, ele é dividido matematicamente em 6 blocos/segmentos de 60 graus. Os parâmetros **0, 2 e 4** atuam como **deslocamentos (offsets)** para posicionar a cor no ponto correto do círculo:

- **0 (Vermelho):** O canal vermelho fica na posição 0° do círculo cromático. A fórmula usa um deslocamento implícito de `+ 0`.
- **2 (Verde):** O verde puro está localizado a 120° no círculo cromático. Como a unidade da fórmula matemática equivale a blocos de 60°, dividimos `120 / 60` e obtemos **2**. Assim, somamos `+ 2` na fórmula quando o Verde é a cor máxima.
- **4 (Azul):** O azul puro está localizado a 240° no círculo. Seguindo a mesma lógica matemática de fatias de 60 graus, dividimos `240 / 60` e obtemos **4**. Assim, somamos `+ 4` na fórmula quando o Azul é o máximo.

Ao final do cálculo, o resultado de toda a conta é multiplicado por 60 para que a matiz final seja mapeada exatamente para um ângulo de volta à escala de 360 graus.
