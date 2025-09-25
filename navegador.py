from pydoc import pager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import time
import json
import math
from datetime import date, datetime

class Navegador:
    def __init__(self):
        options = webdriver.ChromeOptions()
        #codigo necessário para não dar erro
        prefs = {
        "translate_whitelists": {"en":"pt_BR"},
        "translate":{"enabled":"true"}
        }
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.pagina = webdriver.Chrome(options=options)
        self.guia_principal = self.pagina.current_window_handle

    def abrir_nova_janela(self):
        self.pagina.execute_script("window.open('');")
        self.pagina.switch_to.window(self.pagina.window_handles[1])

    def clicar(self, seletor, tipo_seletor):
        elemento = self.procurar_elemento(seletor, tipo_seletor)
        elemento.click()

    def esperar(self, tempo):
        time.sleep(tempo)

    def espera_implicita(self, tempo):
        self.pagina.implicitly_wait(tempo)

    def esperar_por_elemento(self, seletor, tipo_seletor):
        WebDriverWait(self.navegar, 120).until(lambda d: self.procurar_elemento(seletor, tipo_seletor))

    def esperar_por_elemento_texto(self, seletor, tipo_seletor, valor):
        elemento = WebDriverWait(self.navegar, 120).until(lambda d: self.procurar_elemento(seletor, tipo_seletor))
        texto = elemento.text

        texto.strip()

        assert valor in texto

    def fechar_guia_atual(self):
        self.pagina.close()
        self.pagina.switch_to.window(self.guia_principal)

    def inserir_valor(self, valor, seletor, tipo_seletor):
        elemento = self.procurar_elemento(seletor, tipo_seletor)
        elemento.send_keys(valor)

    def maximizar(self):
        self.pagina.maximize_window()

    def minimizar(self):
        self.pagina.minimize_window()

    def navegar(self, url):
        self.pagina.get(url)

    def pegar_texto(self, seletor, tipo_seletor):
        elemento = self.procurar_elemento(seletor, tipo_seletor)
        return elemento.text

    def pegar_url_atual(self):
        return self.pagina.current_url

    def procurar_elemento(self, seletor, tipo_seletor):
        if tipo_seletor == 'xpath':
            return self.pagina.find_element(By.XPATH, seletor)
        elif tipo_seletor == 'id':
            return self.pagina.find_element(By.ID, seletor)
        elif tipo_seletor == 'name':
            return self.pagina.find_element(By.NAME, seletor)
        elif tipo_seletor == 'class_name':
            return self.pagina.find_element(By.CLASS_NAME, seletor)
        elif tipo_seletor == 'link_text':
            return self.pagina.find_element(By.LINK_TEXT, seletor)

    def salvar_cookies(self):
        with open('cookies.txt','w') as cookief:
            # save the cookies as json format 
            cookief.write(json.dumps(self.pagina.get_cookies()))

    def usar_cookies(self):
        with open('cookies.txt','r') as cookief:
            # read using json cookies  note that it is reading a file load instead of loads 
            cookieslist = json.load(cookief)
            for cookie in cookieslist:
                self.pagina.add_cookie(cookie)

    def send_key(self, seletor, tipo_seletor):
        elemento = self.procurar_elemento(seletor, tipo_seletor)
        elemento.send_keys(Keys.ENTER)

    def soup_dados(self, seletor, tipo_seletor, seletor_find_name, seletor_find_all_name, find_attrs="",find_all_attrs=""):
        tabela_dados = self.procurar_elemento(seletor, tipo_seletor)

        conteudo_html = tabela_dados.get_attribute("outerHTML")

        soup = BeautifulSoup(conteudo_html, 'html.parser')

        if find_attrs == '':
            dados = soup.find(name=seletor_find_name)
        else:
            dados = soup.find(name=seletor_find_name, attrs=find_attrs)

        if find_all_attrs == '':
            dados = dados.find_all(name=seletor_find_all_name)
        else:
            dados = dados.find_all(name=seletor_find_all_name, attrs=find_all_attrs)

        return dados
    

    

    

    