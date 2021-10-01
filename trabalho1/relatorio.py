# Número Médio de entidades na fila
def media_entidades_na_fila(df):
    tempo_total = df['TR'].iloc[-1]
    tempo_fila = 0

    linhas_simulacao = df.shape[0]

    for i in range(linhas_simulacao - 1):
        intervalo = df['TR'].iloc[i + 1] - df['TR'].iloc[i]

        TF = df['TF'].iloc[i]  # peso
        tempo_fila += intervalo * TF
    
    m = tempo_fila / tempo_total
    print(f'Número Médio de entidades na fila: {m}')


# Taxa Média de Ocupação dos Servidores
def ocupacao_dos_servidores(df):
    # ES = 0 (Livre) | ES = 1 (Ocupado)
    tempo_total = df['TR'].iloc[-1]
    tempo_atividade = 0

    linhas_simulacao = df.shape[0]

    for i in range(linhas_simulacao - 1):
        intervalo = df['TR'].iloc[i + 1] - df['TR'].iloc[i]

        ES = df['ES'].iloc[i]  # peso
        tempo_atividade += intervalo * ES
    
    taxa_ocupacao = tempo_atividade / tempo_total
    print(f'Taxa Média de Ocupação dos Servidores: {taxa_ocupacao}')


# Tempo médio de uma entidade na fila
def tempo_medio_fila(df):
    # dataframe com clientes que tiveram que entrar na fila
    fila = df.loc[(df['Evento'] == 'Chegada') & (df['TF'] > 0)]

    if fila.empty:
        print('Tempo Médio de uma entidade na fila: 0.0')
    
    else:
        qtd = 0  # quantidade de clientes que entraram na fila e foram atendidos
        clientes = {}
        for i in fila.itertuples():
            # i[2] -> id do cliente  |  i[3] -> Tempo do relógio na chegada

            # procura saída do cliente anterior
            aux = df.loc[(df['Evento'] == 'Saída') & (df['Cliente'] == (i[2] - 1))]

            if aux.shape[0] != 0:  # encontrou saída do cliente anterior
                qtd += 1

                # tempos de entrada e saída da fila
                entrada = i[3]
                saida = aux['TR'].iloc[0]

                # armazena no dicionário na forma {id cliente : tempo_na_fila}
                clientes[i[2]] = saida - entrada
        

        # clientes entraram na fila mas não saíram no período de simulação
        if qtd == 0:
            print('Tempo Médio de uma entidade na fila: 0.0')
        
        else:
            t = sum(clientes.values()) / len(clientes)
            print(f'Tempo Médio de uma entidade na fila: {t}')


# Tempo Médio no sistema
def tempo_medio_sistema(df):
    # dataframe com clientes que saíram do sistema
    saidas = df.loc[df['Evento'] == 'Saída']

    if saidas.shape[0] == 0:
        print('Tempo Médio no Sistema: Nenhum cliente saiu do sistema durante o período de simulação')
    
    else: # casos onde pelo menos um cliente saiu do sistema
        clientes = {}
        for i in saidas.itertuples():
            # i[2] -> id do cliente  |  i[3] -> Tempo do relógio na saída

            # pega o momento de chegada do cliente
            aux = df.loc[(df['Evento'] == 'Chegada') & (df['Cliente'] == i[2])]
            chegada = aux['TR'].iloc[0]

            # cria um dicionário na forma {id cliente : tempo_no_sistema}
            clientes[i[2]] = i[3] - chegada  # tempo saída - tempo chegada
        
        # Tempo médio
        t = sum(clientes.values()) / len(clientes)
        print(f'Tempo Médio no Sistema: {t}')
