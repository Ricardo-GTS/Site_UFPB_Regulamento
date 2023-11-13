# Chatbot do Regulamento da UFPB
import io
import random
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
import warnings
import string
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, render_template, request

# Baixar recursos do NLTK
nltk.download('punkt', quiet=True)

nltk.download('stopwords', quiet=True)
nltk.download('rslp', quiet=True, )
from nltk.stem import WordNetLemmatizer
nltk.download('wordnet', quiet=True) # for downloading packages
warnings.filterwarnings('ignore')

# Mapeamento de acentos, com o objetivo de remover os acentos das palavras
mapa_acentos = {
    'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'ä': 'a',
    'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
    'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
    'ó': 'o', 'ò': 'o', 'õ': 'o', 'ô': 'o', 'ö': 'o',
    'ú': 'u', 'ù': 'u', 'ũ': 'u', 'û': 'u', 'ü': 'u'
}

# Pré-processamento
lemmer = WordNetLemmatizer()
def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]
remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)
def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))


# Geração de resposta
def response(user_response):
    robo_response=''
    sentencas.append(user_response)
    TfidfVec = TfidfVectorizer(tokenizer=LemNormalize)
    tfidf = TfidfVec.fit_transform(sentencas)
    vals = cosine_similarity(tfidf[-1], tfidf)
    
    ind = -2
    req_tfidf = 1
    contador = 1
    while(req_tfidf!=0):
        idx=vals.argsort()[0][ind]
        flat = vals.flatten()
        flat.sort()
        req_tfidf = flat[ind]
        ind = ind - 1
        if (req_tfidf!=0):
            robo_response = robo_response+"\n"+sentencas[idx]
            contador = contador + 1
        if (contador > 3):
            break

    if(ind == -3):
        sentencas.remove(user_response)
        robo_response=robo_response+"NULL"
        return robo_response
    
    sentencas.remove(user_response)
    return robo_response


# Correspondência de palavras-chave
CUMPRIMENTO_INPUTS = ("olá", "saudações", "e aí", "como vai", "oi", "bom dia", "boa tarde", "boa noite")
CUMPRIMENTO_RESPONSES = [
    "Oi",
    "Olá",
    "Tudo bem?",
    "Olá, como posso ajudar?",
    "Olá, é um prazer falar com você!",
    "Olá! Como posso ser útil?",
    "Oi, tudo bem por aí?",
    "Olá, como está o seu dia?",
    "Oi, como posso auxiliar você hoje?"
]

# Função para gerar uma resposta de cumprimento ao usuário
def cumprimento(frase):
    """Se a entrada do usuário for um cumprimento, retorna uma resposta de cumprimento"""
    frase = frase.lower()
    if frase in CUMPRIMENTO_INPUTS:
        return random.choice(CUMPRIMENTO_RESPONSES)
    return None



# Pré-processamento da entrada do usuário
def processar_entrada_usuario(entrada):
    entrada = entrada.lower().translate(remove_punct_dict)
    entrada = pattern.sub(lambda m: mapa_acentos[m.group(0)], entrada)

    stop_words = set(stopwords.words('portuguese'))
    palavras_sem_stopwords = [palavra for palavra in word_tokenize(entrada, language='portuguese') if palavra.lower() not in stop_words]
    
    texto_sem_stopwords = ' '.join(palavras_sem_stopwords)
    return texto_sem_stopwords


def resposta_do_chatbot(user_response):
    # tokenizar as sentenças

    resposta = ''
    entradaPosProcessada = ''
    resposta = ''  # Inicialize a resposta
    user_response = user_response.lower()
    
    # Verifique se o usuário deseja encerrar a conversa
    if user_response == 'tchau':
        return "ROBO: Tchau! Cuide-se..."

    # Verifique se o usuário expressou gratidão
    if user_response in ('obrigado', 'valeu'):
        return "ROBO: De nada!"

    # Verifique se o usuário fez um cumprimento
    cumprimentox = cumprimento(user_response)
    if cumprimentox:
        return f"{cumprimentox}"

    # Processamento da entrada do usuário e geração de resposta
    entradaPosProcessada = processar_entrada_usuario(user_response)
    resposta = response(entradaPosProcessada)
        
    if resposta != 'NULL':
        return resposta

    # Se o loop não gerou uma resposta, informe que o chatbot não entendeu
    return "Desculpe, não entendi a pergunta."



# Leitura do arquivo que contém o texto do Regulamento da UFPB
with open("Regulamento_extrated.txt", encoding="utf8") as file:
    texto = file.read()
    texto = texto.lower()
    texto = re.sub(r'\n\s*\n', '\n', texto)
    texto = re.sub(''.join(mapa_acentos.keys()), lambda m: mapa_acentos[m.group(0)], texto)
    pattern = re.compile("|".join(mapa_acentos.keys()))
    texto = pattern.sub(lambda m: mapa_acentos[m.group(0)], texto)

# tokenizar as sentenças
sentencas = sent_tokenize(texto, language='portuguese')


# Inicializar o Flask
app = Flask(__name__)
# Rota principal para renderizar a página inicial
@app.route("/")
def index():
    return render_template("index.html")

# Rota para processar as solicitações do usuário
@app.route("/get_response", methods=["POST"])
def get_response():
    user_response = request.form.get("user_response")
    
    # Chame a função do chatbot para obter a resposta
    resposta = resposta_do_chatbot(user_response)
    
    return resposta

if __name__ == "__main__":
    app.run(debug=True)