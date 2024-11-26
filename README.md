# Poluição do Ar - RMSP

Esta aplicação web foi desenvolvida como parte da disciplina **Laboratório Avançado de Ciência de Dados (MAC0476)** do Instituto de Matemática e Estatística da Universidade de São Paulo. Seu objetivo é apresentar a distribuição espacial e temporal de diversos indicadores poluentes e meteorológicos na **Região Metropolitana de São Paulo** (RMSP), utilizando dados do sistema [**QUALAR**](https://qualar.cetesb.sp.gov.br/qualar/home.do) da **CETESB**.

A aplicação é composta por:

- **Backend**: Desenvolvido em `Flask` (Python), responsável por processar os dados.
- **Frontend**: Construído em `Angular`, oferece uma interface intuitiva para visualização dos dados.
- **Banco de Dados**: `MySQL`, armazenando os dados coletados e processados.

Toda a aplicação é executada utilizando `Docker` para simplificar o processo de execução e garantir consistência entre os ambientes de desenvolvimento e produção.

## Índice
1. [Requisitos](#requisitos)
2. [Instruções de Instalação e Execução](#instruções-de-instalação-e-execução)
3. [Arquitetura da Aplicação](#arquitetura-da-aplicação)
4. [Tipos de Gráficos Disponíveis](#tipos-de-gráficos-disponíveis)
5. [Autores do Projeto](#autores-do-projeto)
6. [Contribuições e Agradecimentos](#contribuições-e-agradecimentos)

## Requisitos
Para executar esta aplicação, você precisa ter:

- **Docker** instalado no sistema.

> Caso não tenha o Docker instalado, siga as instruções oficiais de instalação [aqui](https://docs.docker.com/get-started/get-docker/).

## Instruções de Instalação e Execução

### Construir e subir os contêineres

1. Clone este repositório:
    ```bash
    git clone https://gitlab.com/mjurgensen/poluicao-ar-rmsp
    cd poluicao-ar-rmsp
    ```

2. Construa as imagens e suba os contêineres usando `Docker Compose`:
    ```bash
    sudo docker compose up --build
    ```

3. Após a inicialização bem-sucedida, acesse a aplicação em *http://127.0.0.1:80*.

### Alterações no código e reconstrução
Caso sejam realizadas alterações no código, siga os passos abaixo para garantir que as mudanças sejam refletidas nos contêineres:

1. Pare os contêineres em execução:
    ```bash
    sudo docker compose down
    ```

2. Reconstrua as imagens e suba os contêineres novamente:
    ```bash
    sudo docker compose up --build
    ```

## Arquitetura da Aplicação
### Backend (Flask)
- Processa e organiza os dados extraídos do QUALAR.
- Expõe APIs RESTful para consumo pelo frontend.

### Frontend (Angular)
- Interface que permite ao usuário visualizar gráficos e informações detalhadas.
- Gráficos de distribuição espacial e temporal baseados nos dados fornecidos.

### Banco de Dados (MySQL)
- Estrutura otimizada para armazenar e consultar os dados processados.
- Modelo de dados desenvolvido em colaboração com especialistas.

## Tipos de Gráficos Disponíveis
Ao acessar a página da aplicação, são oferecidos ao usuário dois diferentes tipos de gráficos a serem visualizados, permitindo uma análise detalhada dos dados ambientais. Nesse sentido, deve-se escolher uma das duas opções abaixo, considerando suas múltiplas variações:

### Gráfico de Linha
Os gráficos de linha mostram a variação temporal de um poluente específico em diferentes escalas temporais. As opções incluem:

1. **Anual**  
Apresenta a média anual do poluente para cada ano entre 2000 e 2024.

2. **Mensal**  
Exibe as médias mensais do poluente para um mês específico ao longo de vários anos.  
**Exemplo:** As médias de março de 2000 a 2024.

3. **Mensal Total**  
Mostra a média geral de cada mês considerando todo o conjunto de dados.  
**Exemplo:** Médias gerais para janeiro, fevereiro, março, etc., ao longo de todos os anos disponíveis.

4. **Diária**  
Apresenta as médias diárias do poluente para cada dia de um mês específico em um determinado ano.  
**Exemplo:** As médias dos dias 1, 2, ..., 30 de novembro de 2023.

5. **Horária**  
Mostra a média geral de cada horário (0h, 1h, 2h, etc.) para todos os dias de um mês específico.  
**Exemplo:** Médias horárias para o mês de março.

> **Nota**: Os gráficos de linha permitem a exibição das concentrações de **mais de um indicador ao mesmo tempo**. No entanto, é importante destacar que nem todo indicador é mensurado em uma mesma **unidade de medida**, de tal forma que é indicado apenas exibir ao mesmo tempo indicadores que estão na mesma unidade de medida.

### Mapa de Calor
Os mapas de calor representam visualmente as concentrações dos poluentes em uma determinada região e período. Essas concentrações são obtidas por meio da **interpolação espacial** dos valores coletados pelas 37 estações na Região Metropolitana de São Paulo. 

Quando há mais de um mapa para um conjunto de dados, o usuário pode navegar entre eles utilizando uma barra interativa (**"navegador de mapas"**).

As opções de escalas temporais incluem:

1. **Anual**  
Gera um mapa de calor para cada ano (médias anuais) dentro de um intervalo definido pelo usuário.  
**Parâmetros:** Ano de início e ano final.

2. **Mensal**  
Gera mapas de calor mensais (médias mensais) para os 12 meses de um ano especificado.  
**Parâmetros:** Ano.

3. **Diária**  
Produz mapas de calor diários (médias diárias) para todos os dias de um mês em um ano fornecido.  
**Parâmetros:** Mês e ano.

4. **Horária**  
Gera mapas de calor por hora (médias horárias) para todas as 24 horas de um dia específico.  
**Parâmetros:** Dia, mês e ano.

5. **Instantâneo**  
Cria um único mapa de calor para uma hora específica em um dia específico (média horária).  
**Parâmetros:** Hora, dia, mês e ano.

> **Nota**: Os mapas de calor permitem a exibição de **apenas um indicador por vez**.

#### Sobre a interpolação
Para que seja feita a interpolação dos pontos da Região Metropolitana de São Paulo para exibição do mapa de calor, **dois métodos** foram implementados:

1. **k-Nearest Neighbors (kNN)**  
Calcula a média ponderada das k estações mais próximas ao ponto de interpolação. O peso de uma estação é inversamente proporcional à sua distância para o ponto.

> **Parâmetros do kNN**:  
> - ***k*** = número de vizinhos a considerar

2. **Krigagem**  
Considera não só a proximidade (médias ponderadas), mas também a correlação espacial entre os pontos (modela a variabilidade espacial).

> **Parâmetros da Krigagem**:  
> - ***method*** = define o tipo de krigagem (*ordinary* ou *universal*)   
> - ***variogram_model*** = especifica o modelo de variograma usado para representar a variabilidade espacial (*linear*, *power*, *gaussian* ou *spherical*)  
> - ***nlags*** = número de intervalos usados para calcular o variograma experimental
> - ***weight*** = aplica pesos aos pares no variograma, geralmente com base na contagem de pontos (*true* ou *false*).

Nem todos os pontos no mapa são interpolados. Pontos **distantes das estações de coleta de dados** não são interpolados para garantir que apenas informações com maior grau de confiabilidade sejam exibidas. Por isso, é comum haver áreas no mapa sem informações.

Um ponto é considerado **distante** (e, portanto, não interpolado) se estiver fora do **raio de confiança** de todas as estações de coleta. O **raio de confiança** é o limite ao redor de uma estação dentro do qual os dados fornecidos por ela são considerados confiáveis. Esses raios variam conforme a estação e o indicador, podendo ir de 1 quilômetro a dezenas de quilômetros.

Em resumo, todos os pontos interpolados estão dentro do raio de pelo menos uma estação. Para esses pontos, a interpolação considera não apenas as estações cujos raios incluem o ponto, mas também todas as que o método selecionado determinar como relevantes, ponderadas pela distância.

## Autores do Projeto
- Matheus Sanches Jurgensen [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue)](https://www.linkedin.com/in/matheusjurgensen/)
- André Nogueira Ribeiro [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue)](https://www.linkedin.com/in/andré-nogueira-ribeiro-0172ba24b/)
- Tobias Rossi Müller [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue)](https://www.linkedin.com/in/tobias-rossi-muller/)
- Kaique Nunes de Oliveira [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue)](https://www.linkedin.com/in/kaique-oliveira-302b72212/)
- Gabriel Jacob Perin [![Gmail](https://img.shields.io/badge/Gmail-email-red?logo=gmail)](mailto:gabrieljp@usp.br) 

## Contribuições e Agradecimentos
Agradecemos às seguintes pessoas por sua valiosa contribuição durante o desenvolvimento deste projeto:

- **Professor Fabio Kon** (*kon@ime.usp.br*): Pela excelente condução da disciplina **MAC0476**, permitindo que este projeto fosse desenvolvido como parte do aprendizado acadêmico.
- **Professora Flávia Noronha Dutra Ribeiro** (*flaviaribeiro@usp.br*): Por sugerir este projeto de grande impacto e por todo o suporte oferecido ao longo do desenvolvimento.
- **Professora Kelly Rosa Braghetto** (*kellyrb@ime.usp.br*): Por seu apoio essencial na modelagem do banco de dados.


