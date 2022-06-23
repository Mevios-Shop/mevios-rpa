from turtle import st
from unicodedata import numeric
from xmlrpc.client import Boolean
from navegador import Navegador
import xpto
import requests
from bs4 import BeautifulSoup
import math
from datetime import date, datetime
from selenium.common.exceptions import NoSuchElementException

url_amazon = 'https://sellercentral.amazon.com.br/'
url_pedidos_enviados = 'https://sellercentral.amazon.com.br/orders-v3/mfn/shipped?date-range=last-365&sort=order_date_desc&page=1'
url_pedidos_envio_pendente = 'https://sellercentral.amazon.com.br/orders-v3/mfn/unshipped?date-range=last-365&sort=order_date_desc&page=1'

#region Coleta numero dos pedidos nao importados

def coleta_codigos_pedidos_nao_importados(quantidade_pedidos_nao_importados: int):

    lista_pedidos_para_importar = []

    contadorx = 0

    print('len: ', len(lista_pedidos_para_importar), ', quantidade_pedidos_nao_importados: ', quantidade_pedidos_nao_importados)

    coletando_codigo_pedidos_enviados = False

    while len(lista_pedidos_para_importar) < quantidade_pedidos_nao_importados:

        tipo_pedido = ""

        print('quantidade_pedidos_envio_pendente: ', quantidade_pedidos_envio_pendente)
        print('len(lista_pedidos_para_importar): ', len(lista_pedidos_para_importar))
        print('contadorx: ', contadorx)

        if quantidade_pedidos_envio_pendente > 0 and contadorx < quantidade_pedidos_envio_pendente:
            tipo_pedido = 'envio_pendente'
            navegador.navegar(url_pedidos_envio_pendente)
            navegador.esperar(5)
        elif len(lista_pedidos_para_importar) < quantidade_pedidos_nao_importados and contadorx >= quantidade_pedidos_envio_pendente:
            tipo_pedido = 'enviado'

            if coletando_codigo_pedidos_enviados == False:
                navegador.navegar(url_pedidos_enviados)
                navegador.esperar(5)
                coletando_codigo_pedidos_enviados = True
            

        print('tipo_pedido: ', tipo_pedido)

        pedidos = navegador.soup_dados('orders-table', 'id', 'tbody', 'tr')

        quantidade_pedidos_por_pagina = 0

        #Conta a quantidade de pedidos na tela
        for i in pedidos:
            
            if '/orders-v3/order/' in str(i):
                #print('\ni: ', i, '\n')
                quantidade_pedidos_por_pagina+=1

        print("Quantidade_pedidos_por_pagina: ", quantidade_pedidos_por_pagina)

        

        contador = 0
        quantidade_paginas=0

        if tipo_pedido == 'envio_pendente':
            print('entrei em: envio_pendente')
            quantidade_paginas = math.ceil(quantidade_pedidos_envio_pendente/quantidade_pedidos_por_pagina)
        elif tipo_pedido == 'enviado':
            print('quantidade_pedidos_enviados: ', quantidade_pedidos_enviados)
            quantidade_paginas = math.ceil(quantidade_pedidos_enviados/quantidade_pedidos_por_pagina)


        print("quantidade_paginas: ", quantidade_paginas)

        


        pedidos = navegador.soup_dados('orders-table', 'id', 'table', 'a', {"id": "orders-table"})

        

        #coleta os numeros de pedidos
        for i in pedidos:
            '''
            if contadorx > quantidade_pedidos_envio_pendente:
                print('\n', i, '\n')'''

            if '<a href="/orders-v3/order/' in str(i) and '/confirm-shipment' not in str(i) and '/cancel-order' not in str(i) and '/edit-shipment' not in str(i):

                contadorx+=1
                
                codigo_pedido = str(i).split('>')[1]

                codigo_pedido = codigo_pedido.replace('</a', '')

                verifica_pedido_importado = requests.get('http://localhost:3000/venda_pedido/' + str(codigo_pedido)).json()

                #print('verifica_pedido_importado: ', verifica_pedido_importado)

                try:
                    if verifica_pedido_importado['mensagem'] == "Pedido não encontrado!":

                        #print('codigo_pedido: ', codigo_pedido, ' statusCode: ', verifica_pedido_importado)

                        lista_pedidos_para_importar.append(codigo_pedido)
                except:
                    pass


                

        #print('lista_pedidos_para_importar: ', lista_pedidos_para_importar)

        if(quantidade_paginas > 1 and len(lista_pedidos_para_importar) < quantidade_pedidos_nao_importados):
            #print("#", contador)
            navegador.procurar_elemento("a-last", 'class_name').click()
            navegador.esperar(5)

        if len(lista_pedidos_para_importar) == quantidade_pedidos_nao_importados:
            break

    lista_pedidos_para_importar.reverse()

    navegador.esperar(5)

    return lista_pedidos_para_importar

#endregion

#region verifica_frete_melhor_envio

def verifica_frete_melhor_envio(codigo_rastreamento: str, id_venda: str):

    dic_envio = {}

    navegador.abrir_nova_janela()

    navegador.navegar('https://melhorenvio.com.br/painel')
    navegador.espera_implicita(30)

    navegador.esperar(5)

    print('url atual: ', navegador.pegar_url_atual())

    if navegador.pegar_url_atual() == 'https://melhorenvio.com.br/login':

        navegador.inserir_valor(xpto.email_melhor_envio, 'username', 'id')
        navegador.inserir_valor(xpto.senha_melhor_envio, 'password', 'id')

        navegador.send_key("password", 'id')

        try:
            verifica_login_excedido = navegador.pegar_texto('/html/body/div[2]/div/section/div/div/div/div[2]/form/p[1]', 'xpath')
            
            if 'Confira os dados preenchidos' in verifica_login_excedido:
                navegador.fechar_guia_atual()
                return "Quantidade de login excedida!"
        except:
            pass

    navegador.esperar_por_elemento_texto('/html/body/div[2]/div/div/div[1]/div[2]/div[2]/div[1]/div/div/div[2]/div/p', 'xpath', 'Resumo da carteira')
    
    navegador.navegar('https://www.melhorrastreio.com.br/rastreio/' + codigo_rastreamento)

    rastreio_encontrado = ""

    try:
        navegador.esperar_por_elemento_texto('/html/body/div[3]/section/div[1]/div/div/h2', 'xpath', 'Rastreio não encontrado ')
        rastreio_encontrado = False
        navegador.fechar_guia_atual()
        return "Rastreio não encontrado!"
    except:
        rastreio_encontrado = True
        

    if rastreio_encontrado:

        navegador.navegar('https://melhorenvio.com.br/painel/meus-envios#postados')

        navegador.esperar_por_elemento_texto('/html/body/div[2]/div/div/div[1]/div[2]/div[2]/div/div/div/div[2]/ul[1]/li[2]', 'xpath', 'Transportadora')

        navegador.inserir_valor(codigo_rastreamento, 'search', 'name')

        navegador.clicar('/html/body/div[2]/div/div/div[1]/div[2]/div[2]/div/div/div/div[1]/div[1]/form/button', 'xpath')

        navegador.esperar(3)

        navegador.clicar('/html/body/div[2]/div/div/div[1]/div[2]/div[2]/div/div/div/div[2]/ul[2]/li/div[1]/ul/li[1]/a', 'xpath')

        dic_envio["codigo_rastreamento"] = codigo_rastreamento
        dic_envio["plataformaId"] = 5
        valor_frete = str(navegador.pegar_texto('/html/body/div[2]/div/div/div[1]/div[2]/div[2]/div/div/div/div[2]/ul[2]/li/div[2]/ul/li/div/ul/li[5]/div/p[3]', 'xpath'))
        valor_frete = valor_frete.replace("R$ ", "")
        valor_frete = valor_frete.replace(",", ".")
        dic_envio["custo_frete"] = valor_frete
        
        print("valor frete: ", valor_frete)

        navegador.fechar_guia_atual()

        dic_envio['venda'] = id_venda

        return dic_envio

    '''
    navegador.navegar('https://melhorenvio.com.br/painel/meus-envios#postados')

    navegador.espera_implicita(30)

    navegador.inserir_valor(codigo_rastreamento, 'search', 'name')

    navegador.clicar('/html/body/div[2]/div/div/div[1]/div[2]/div[2]/div/div/div/div[1]/div[1]/form/button', 'xpath')

    navegador.esperar_por_elemento()'''

    '''
    navegador.esperar_por_elemento_texto('/html/body/div[2]/div/div/div[1]/div[2]/div[2]/div[1]/div/div/div[2]/div/p', 'xpath', "Resumo da carteira")

    navegador.esperar(5)

    navegador.clicar("hs-eu-confirmation-button", 'id')'''

#endregion
    



#region verifica frete frenet

def verifica_frete_frenet(codigo_rastreamento: str):
    pass

#endregion

#region importar_pedidos
def importar_pedidos(lista_pedidos_nao_importados):
    #comeca importacao
    for pedido in lista_pedidos_nao_importados:

        dic_venda = {}
        dic_venda_completa = {}

        data_sem_formatacao = []
        data = ""
        contador_lista = 0
        url = "https://sellercentral.amazon.com.br/orders-v3/order/" + pedido
        print("url: ", url)

        navegador.navegar(url)
        navegador.esperar(3)

        if str(pedido) == '702-3778722-5085859':
            pass

        dic_venda["codigo_pedido"] = str(pedido)

        print("pedido: ", pedido[0])

        dic_venda["plataforma"] = 2
        dic_venda["status_venda"] = 2

        #region pegar data

        data_sem_formatacao = str(navegador.pegar_texto("/html/body/div[1]/div[2]/div/div/div[1]/div[1]/div/div[2]/div[1]/div/div/div/div/div/div[1]/table/tbody/tr[3]/td[2]/span", 'xpath'))
        data_sem_formatacao = data_sem_formatacao.split(" ")
        
        print("data_sem_formatacao: ", data_sem_formatacao)

        

        for i in data_sem_formatacao:

            #print("contador: lista: ", contador_lista)

            if contador_lista == 1:
                data+= i+"/"
            elif contador_lista == 3:
                if i == "jan.":
                    data+="01"
                elif i == "fev.":
                    data+="02"
                elif i == "mar.":
                    data+="03"
                elif i == "abr.":
                    data+="04"
                elif i == "mai.":
                    data+="05"
                elif i == "jun.":
                    data+="06"
                elif i == "jul.":
                    data+="07"
                elif i == "ago.":
                    data+="08"
                elif i == "set.":
                    data+="09"
                elif i == "out.":
                    data+="10"
                elif i == "nov.":
                    data+="11"
                elif i == "dez.":
                    data+="12"
                
                print("data+= ", data)

                data+="/"
                
            elif contador_lista == 5:
                data+=i
            elif contador_lista == 6:
                data+=" "+i

            contador_lista+=1

        print("data: ", data)

        data = datetime.strptime(data, '%d/%m/%Y %H:%M')

        print("data format: ", data)

        dic_venda["data"] = str(data)
        #endregion

        #region pegar valor do frete

        valor_frete = str(navegador.pegar_texto("/html/body/div[1]/div[2]/div/div/div[1]/div[1]/div/div[7]/div/table/tbody/tr/td[7]/div/table[1]/tbody/div[2]/div[2]/span", 'xpath'))
        valor_frete = valor_frete.replace("R$ ", "")
        valor_frete = valor_frete.replace(",", ".")
        dic_venda["valor_frete"] = float(valor_frete)

        #endregion

        #region pegar valor_reembolso
        valor_reembolso: str

        try:
            valor_reembolso = str(navegador.pegar_texto("/html/body/div[1]/div[2]/div/div/div[1]/div[2]/div[1]/table[1]/tbody/tr[3]/td[2]/span", 'xpath'))
            valor_reembolso = valor_reembolso.replace("-R$ ", "")
            valor_reembolso = valor_reembolso.replace(",", ".")

            print("valor_reembolso: ", valor_reembolso)
            dic_venda["valor_reembolso"] = float(valor_reembolso)
        except NoSuchElementException:
            print("Pedido não tem reembolso!")

        #endregion

        #region pegar itens do pedido
        itens_venda =  navegador.soup_dados('/html/body/div[1]/div[2]/div/div/div[1]/div[1]/div/div[8]/div/div/div[2]/div/table', 'xpath', 'tbody', 'tr')

        dic_itens_venda = {}

        for item in itens_venda:
            contador_coluna = 0
            for coluna in item:
                contador_coluna+=1
                if contador_coluna == 2:
                    print('\ncoluna2: ', coluna, '\n')

                    for linha in coluna:
                        contador_i = 0
                        for i in linha:
                            contador_i+=1
                            if contador_i == 3:
                                for i2 in i:
                                    contador_i3 = 0
                                    for i3 in i2:
                                        contador_i3+=1
                                        if contador_i3 == 2:
                                            sku = str(i3).replace(":", "")
                                            sku = str(sku).replace(" ", "")
                                            payload = {'sku': str(sku), 'plataformaId': int(dic_venda["plataforma"])}
                                            request_variacao = requests.get('http://localhost:3000/sku_id_variacao/', data=payload).json()
                                            
                                            if "mensagem" in request_variacao:
                                                print("request: ", request_variacao)
                                            elif "variacao_produto" in request_variacao:
                                                variacaoId = request_variacao['variacao_produto']
                                                dic_itens_venda["variacao_produto"] = variacaoId['id']
                                                print("variacaoProdutoId: ", dic_itens_venda["variacao_produto"])              

                elif contador_coluna == 4:
                    quantidade_item = 0
                    for i in coluna:
                        dic_itens_venda['quantidade'] = i

                    print("\ndic_itens_venda['quantidade']: ", quantidade_item, '\n')
                
                elif contador_coluna == 5:
                    preco_item = str(navegador.pegar_texto('/html/body/div[1]/div[2]/div/div/div[1]/div[1]/div/div[7]/div/table/tbody/tr/td[6]/span', 'xpath'))
                    preco_item = str(preco_item.replace("R$ ", ""))
                    preco_item = preco_item.replace(",", ".")

                    dic_itens_venda["valor"] = preco_item
                    
                    print('dic_itens_venda: ', dic_itens_venda)

                    #Pegar id de estoque do item
                    request_estoqueId = requests.get('http://localhost:3000/estoque_disponivel/' + str(dic_itens_venda["variacao_produto"]) + '/' + str(dic_itens_venda['quantidade'])).json()

                    print('request_estoqueId: ', request_estoqueId)

                    request_inserir_venda = requests.post('http://localhost:3000/venda/', data=dic_venda).json()

                    print("request_inserir_venda: ", request_inserir_venda)

                    lista_itens_venda = []

                    if len(request_estoqueId) > 0:
                        for i in request_estoqueId:
                            dic_itens_venda_modificado = dic_itens_venda.copy()

                            dic_itens_venda_modificado['estoque'] = i['id']

                            dic_itens_venda_modificado['venda'] = request_inserir_venda['id']
                            lista_itens_venda.append(dic_itens_venda_modificado)
                        
                        print('lista_itens_venda: ', lista_itens_venda)


                    dic_venda_completa["itens_venda"] = lista_itens_venda

                    dic_venda_completa["venda"] = dic_venda

                    print('\dic_venda: ', dic_venda_completa, '\n')

                    if 'id' in request_inserir_venda:
                        print('lista_itens_venda: ', lista_itens_venda)
                        for item_venda in lista_itens_venda:
                            request_inserir_itens_venda = requests.post('http://localhost:3000/item_venda/', data=item_venda).json()          

                            print('request_inserir_itens_venda: ', request_inserir_itens_venda)

                            if 'id' in request_inserir_itens_venda:
                                print('Item cadastrado com sucesso!')

                        #region pegar codigo de rastreio
                        codigo_rastreamento = ''
                        try:
                            codigo_rastreamento = str(navegador.pegar_texto("/html/body/div[1]/div[2]/div/div/div[1]/div[1]/div/div[8]/div/div/div[1]/div[2]/div/div[2]/div[2]/div[2]/span", 'xpath'))

                            print("codigo_rastreamento: ", codigo_rastreamento)

                            
                            
                            verifica_envio = verifica_frete_melhor_envio(codigo_rastreamento, request_inserir_venda['id'])
                            print('verifica_envio: ', verifica_envio)

                            if 'codigo_rastreamento' in verifica_envio:
                                dic_venda_completa["envio"] = verifica_envio
                            
                        except NoSuchElementException:
                            print("Pedido não tem codigo de rastreamento!")

                        #endregion

                        if codigo_rastreamento != '':
                            dic_alterar_status_venda = {}
                            dic_alterar_status_venda['status_venda']=3
                            print('url')
                            '''
                            print('url')
                            request_atualizar_status_venda = requests.patch('http://localhost:3000/venda/' + str(request_inserir_venda['id']), data=dic_alterar_status_venda['status_venda'])
                            '''
                            request_inserir_rastreamento_venda = requests.post('http://localhost:3000/rastreamento_venda/', data=dic_venda_completa['envio']).json()
                        
                            if 'id' in request_inserir_rastreamento_venda:
                                print('Rastreamento da venda cadastrado com sucesso!')

        #endregion

        

        
        #break

#endregion

#region Abrindo pagina Amazon
navegador = Navegador()

navegador.minimizar()

navegador.navegar(url_amazon)

navegador.espera_implicita(30)
#endregion


#region Fazendo Login
navegador.inserir_valor(xpto.email, 'ap_email', 'id')
navegador.inserir_valor(xpto.senha, 'ap_password', 'id')
navegador.clicar('rememberMe', 'name')
navegador.clicar('signInSubmit', 'id')
#endregion

#region Fazendo Verificação em duas etapas

#Aguarda Texto da tela de 2FA
navegador.esperar_por_elemento_texto('/html/body/div[1]/div[1]/div[2]/div/div[2]/div/form/div/div/h1', 'xpath', "Verificação em duas etapas")

#Iniciando 2FA

_2fa = str(input("Digite o código 2fa: "))
navegador.inserir_valor(_2fa, '/html/body/div[1]/div[1]/div[2]/div/div[2]/div/form/div/div/div[1]/input', 'xpath')
navegador.maximizar()
navegador.clicar('rememberDevice', 'name')
navegador.clicar('auth-signin-button', 'id')
navegador.esperar(5)

#endregion


#region Selecionando a conta

#region Aguarda Texto da tela de selecao de conta

navegador.esperar_por_elemento_texto("/html/body/div[1]/div[2]/div/div/div[1]/div/kat-box/div/div[3]/div/div[3]/div/button", 'xpath', 'Selecionar conta')
navegador.clicar("//*[@id='picker-container']/div/div[3]/div/button", 'xpath')
navegador.espera_implicita(30)

# Traduzir a pagina
navegador.clicar("/html/body/div[1]/div[3]/div/div[2]/ul/li[3]/span/div/select/option[1]", 'xpath')


#endregion

#region Abre pagina de pedidos e começa importação


navegador.navegar(url_pedidos_enviados)
navegador.esperar(5)

#espera carregar os pedidos
navegador.esperar_por_elemento_texto("/html/body/div[1]/div[2]/div/div/div[3]/div[3]/div[2]/div[1]/div[1]/div/span[1]", 'xpath', 'pedidos')

#region conta quantidade de pedidos

quantidade_pedidos_importados = int(len(requests.get('http://localhost:3000/vendas_plataforma/2').json()))

quantidade_pedidos_enviados = str(navegador.pegar_texto("/html/body/div[1]/div[2]/div/div/div[3]/div[3]/div[2]/div[1]/div[1]/div/span[1]", 'xpath'))
quantidade_pedidos_enviados = int(quantidade_pedidos_enviados.replace(" pedidos", ""))
navegador.navegar('https://sellercentral.amazon.com.br/orders-v3/mfn/unshipped')
navegador.esperar_por_elemento_texto("/html/body/div[1]/div[2]/div/div/div[3]/div[4]/div[2]/div[1]/div[1]/div/span[1]", 'xpath', 'pedidos')
quantidade_pedidos_envio_pendente = str(navegador.pegar_texto("/html/body/div[1]/div[2]/div/div/div[3]/div[4]/div[2]/div[1]/div[1]/div/span[1]", 'xpath'))
quantidade_pedidos_envio_pendente = int(quantidade_pedidos_envio_pendente.replace(" pedidos", ""))

quantidade_total_pedidos = quantidade_pedidos_enviados + quantidade_pedidos_envio_pendente

quantidade_pedidos_nao_importados = quantidade_total_pedidos - quantidade_pedidos_importados


print(  "total de pedidos: ", quantidade_total_pedidos, 
        ", enviados: ", quantidade_pedidos_enviados, 
        ", importados: ", quantidade_pedidos_importados,
        ", envio pendente: ", quantidade_pedidos_envio_pendente,
        ", não importados: ", quantidade_pedidos_nao_importados)



#endregion
        

if(quantidade_pedidos_nao_importados > 0):

    #pedidos nao importados
    pedidos_nao_importados = coleta_codigos_pedidos_nao_importados(quantidade_pedidos_nao_importados)

    print('pedidos_nao_importados: ', pedidos_nao_importados)
    print('\nlen pedidos_nao_importados: ', len(pedidos_nao_importados))

    importar_pedidos(pedidos_nao_importados)

    
#region Coleta numero pedidos nao importados



navegador.esperar(30)