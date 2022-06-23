import os
from unicodedata import numeric
import openpyxl
import pandas as pd
import requests
from dic_sku_shopee import dic_sku

diretorio = './arquivos_shopee'

lista_arquivos = []

for arquivo in os.listdir(diretorio):
    lista_arquivos.append(arquivo)
    
#print(lista_arquivos)

for i in lista_arquivos:

    if '~' not in i:
        #book = openpyxl.load_workbook('./arquivos_shopee/'+i)

        #pedidos = book['orders']

        caminho = '.\\arquivos_shopee\\'+i

        #print('caminho: ', caminho)

        pedidos = pd.read_excel(caminho)

        df = pd.DataFrame(pedidos)

        #from  rows  in pedidos.iter

        lista_dados = []
        dic_vendas = {}

        qtd_linhas =len(df.index)
        #print("len: ", qtd_linhas)

        for i, row in df.iterrows():
            #print(f"Index: {i}")
            #print(f"{row}\n")

            contador = 0

            dic_dados_venda = {}
            dic_itens_venda = {}

            dic_dados_venda['plataforma'] = 1

            dic_itens = {}
            dic_item = {}
            codigo_pedido = ''
            variacao_produto = ''

            dic_rastreamento = {}
            pedido_ja_importado = False

            nome_produto_completo = ''

            for b in row:

                contador+=1

                

                if contador == 1:
                    codigo_pedido = b
                    id_pedido = ''

                    verifica_pedido_importado = requests.get('http://localhost:3000/venda_pedido/' + str(codigo_pedido)).json()

                    try:
                        if 'id' in verifica_pedido_importado:

                            id_pedido = int(verifica_pedido_importado['id'])

                            pedido_ja_importado = True
                        else:
                            dic_dados_venda['codigo_pedido'] = b
                    except:
                        pass
                    
                elif contador == 2 and pedido_ja_importado == False:

                    if b == 'A Enviar':
                        dic_dados_venda['status_venda'] = 2
                    elif b == 'Frete':
                        dic_dados_venda['status_venda'] = 3
                    elif b == 'Concluído':
                        dic_dados_venda['status_venda'] = 5
                    
                elif contador == 4 and pedido_ja_importado == False:
                    if id_pedido != '':
                        dic_rastreamento['venda'] = id_pedido
                    dic_rastreamento['codigo_rastreamento'] = b
                elif contador == 10 and pedido_ja_importado == False:
                    dic_dados_venda['data'] = b

                
                #elif contador == 11:
                    #variacao_produto = int(b)
                    #dic_item['variacao_produto'] = variacao_produto
                
                elif contador == 12:
                    if b in dic_sku:
                        print('dic_sku[b]: ',dic_sku[b])
                        variacao_produto = dic_sku[b]
                    else:
                        nome_produto_completo = b
                #elif contador == 13:
                    #if b is numeric:
                        #dic_item.update['variacao_produto'] = b

                elif contador == 14 and variacao_produto == '':
                    nome_produto_completo = nome_produto_completo + b

                    if nome_produto_completo in dic_sku:
                        print('dic_sku[b]: ',dic_sku[nome_produto_completo])
                        variacao_produto = dic_sku[nome_produto_completo]
                elif contador == 16:
                    valor_item = b
                elif contador == 17:
                    quantidade_item = b
                elif contador == 21 and pedido_ja_importado == False:
                    if b != 0.00:
                        dic_dados_venda['valor_reembolso'] = b
                elif contador == 39:
                    comissao = b

            request_verifica_item_venda = requests.get('http://localhost:3000/itens_venda/'+ str(id_pedido)).json()

            print('request_verifica_item_venda: ', request_verifica_item_venda)

            lista_variacaoId_itens_venda = []

            if id_pedido != '':
                if 'id' in request_verifica_item_venda[0]:
                    for i in request_verifica_item_venda:

                        id = i['variacao_produto']['id']

                        if id not in lista_variacaoId_itens_venda:
                            lista_variacaoId_itens_venda.append(id)

                    print('lista_variacaoId_itens_venda: ', lista_variacaoId_itens_venda)


            if (pedido_ja_importado == False) or (pedido_ja_importado == True and variacao_produto not in lista_variacaoId_itens_venda):

                request_estoqueId = requests.get('http://localhost:3000/estoque_disponivel/' + str(variacao_produto) + '/' + str(quantidade_item)).json()
                print('request_estoqueId: ', request_estoqueId)

                if pedido_ja_importado == False:
                    request_inserir_venda = requests.post('http://localhost:3000/venda/', data=dic_dados_venda).json()
            
                if 'id' in request_estoqueId[0]:
                    for i in request_estoqueId:
                        dic_item['venda'] = request_inserir_venda['id']
                        dic_item['variacao_produto'] = variacao_produto
                        dic_item['valor'] = valor_item
                        dic_item['comissao'] = comissao
                        dic_item['estoque'] = i['id']
                        
                        dic_itens[i['id']] = dic_item

                        request_inserir_itens_venda = requests.post('http://localhost:3000/item_venda/', data=dic_item).json()
                        print('request_inserir_itens_venda: ', request_inserir_itens_venda)
                
            dic_dados_venda['itens'] = dic_itens
            dic_dados_venda['rastreamento'] = dic_rastreamento
            dic_vendas[codigo_pedido] = dic_dados_venda

            if pedido_ja_importado == False:
                dic_rastreamento['venda'] = request_inserir_venda['id']
                request_inserir_rastreamento_venda = requests.post('http://localhost:3000/rastreamento_venda/', data=dic_rastreamento).json()

            
            #break
                   
    break

