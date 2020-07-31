from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from spliteString import split_string
# from funDownload import download
from time import time
from conversation import conversation

import json
import requests
import os
from os.path import join, dirname
from dotenv import load_dotenv
from ibmWatson import Audio_To_Text

#leitura dos arquivos .env
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


materia = assunto = name_audio = ''

# ranges da conversa
MATERIA, ASSUNTO, AUDIO = range(3)

# funções de interações da duda
# duas funções para iniciar uma conversa com a duda, através de comandos ou palavras
# def start(update, context):
#     user = update.message.from_user
#     update.message.reply_text(conversation['inicio'])
#     update.message.reply_text(conversation['inicio_2'])
#     update.message.reply_text(conversation['materia'])
#     return MATERIA

def start_2(update, context):
    iniciar = ['/start','start', 'inicio', 'oi', 'olá', 'ola', 'começar', 'hi', 'hello']
    ajudar = ['/help','help','ajuda']

    for word in iniciar:
        if word == update.message.text:
            update.message.reply_text(conversation['inicio'])
            update.message.reply_text(conversation['inicio_2'])
            update.message.reply_text(conversation['materia'])
            return MATERIA

    for ajuda in ajudar:
        if ajuda == update.message.text:
            update.message.reply_text(conversation['ajuda'])
            # DEVE COLOCAR COMANDO PARA CANCELAR!
            return ''

    update.message.reply_text('Me desculpa eu não sei o que fazer com esse comando, vamos tentar de novo, digite start ou /start para começarmos. 😉')



#função que resgata a materia e passa os próximos comandos
def get_materia(update, context):
    if not update.message.text == 'cancelar':
        global materia
        materia = update.message.text
        update.message.reply_text(f'Legal ja sei que sua Disciplina é de {materia.lower()}')
        update.message.reply_text(conversation['conteudo'])
        return ASSUNTO
    else:
        update.message.reply_text(conversation['cancelar'])
        update.message.reply_text(conversation['cancelar_2'])
        return ConversationHandler.END

#função que resgata o assunto e passa os próximos comandos
def get_assunto(update, context):
    if not update.message.text == 'cancelar':
        global assunto
        assunto = update.message.text
        update.message.reply_text(f'Muito legal o conteúdo da sua aula é sobre {assunto.lower()}')
        update.message.reply_text(conversation['audio'])
        # update.message.reply_text(conversation['dicas'])
        # update.message.reply_text(conversation['dica_1'])
        # update.message.reply_text(conversation['dica_2'])
        # update.message.reply_text(conversation['dica_2.1'])
        # update.message.reply_text(conversation['dica_2.2'])
        # update.message.reply_text(conversation['dicas_2'])
        # update.message.reply_text(conversation['dica_3'])
        # update.message.reply_text(conversation['dica_4'])
        update.message.reply_text(conversation['audio_2'])
        return AUDIO
    else:
        update.message.reply_text(conversation['cancelar'])
        update.message.reply_text(conversation['cancelar_2'])
        return ConversationHandler.END

#função que pega o audio e trabalha com esse audio
def get_audio(update, context):
    update.message.reply_text('Só um minutinho estou processando tudo...')
    audio = update.message.audio.get_file()
    currente_date = time()

    dados = {'file_id':audio.file_unique_id,'file_path':audio.file_path,'materia':materia,'assunto':assunto,'horario':currente_date}
    update.message.reply_text(f'Acesse: {os.environ.get("URL_SERVER")}audio?id={currente_date}-{audio.file_unique_id} para ouvir!')
    r = requests.post(os.environ.get("URL_SERVER")+'tratarAudio',data=json.dumps(dados))

    if r.status_code == 200:
        print ('ok')
    else:
        print ('erro')



#função de tratamento de voice
def get_voice(update, context):
    update.message.reply_text('Só um minutinho estou processando tudo...')
    audio = update.message.voice.get_file()
    currente_date = time()

    dados = {'file_id':audio.file_unique_id,'file_path':audio.file_path,'materia':materia,'assunto':assunto,'horario':currente_date}
    update.message.reply_text(f'Acesse: {os.environ.get("URL_SERVER")}audio?id={currente_date}-{audio.file_unique_id} para ouvir!')
    r = requests.post(os.environ.get("URL_SERVER")+'tratarAudio',data=json.dumps(dados))

    if r.status_code == 200:
        print ('ok')
    else:
        print ('erro')

#funções para tratamento de erros no processo
#Mandou uma palavra en vez de um audio.
def not_audio(update, context):
    if not update.message.text == 'cancelar':
        update.message.reply_text('Me desculpe eu estava esperando um arquivo de audio')
        update.message.reply_text('Vamos tentar de novo!')
        update.message.reply_text('O arquivo precisa ser em formato MP3.')
        update.message.reply_text('Me envie o audio da aula:')
        return AUDIO
    else:
        update.message.reply_text(conversation['cancelar'])
        update.message.reply_text(conversation['cancelar_2'])
        return ConversationHandler.END

#função de cancelamento da conversa com a duda
def cancel(update, context):
    update.message.reply_text(conversation['cancelar'])
    update.message.reply_text(conversation['cancelar_2'])
    return ConversationHandler.END

# área de execução da duda
def main():
    token = os.environ.get("TOKEN_BOT")
    duda = Updater(token, use_context=True)
    dp = duda.dispatcher

    # Inicia o sistema e aguarda algum comando
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start_2),
            CommandHandler('help', start_2),
            # CommandHandler('inicio', start_2),
            # CommandHandler('ajuda', start),
            MessageHandler(Filters.text & ~Filters.command, start_2)
        ],
        states={
            MATERIA: [MessageHandler(Filters.text & ~Filters.command, get_materia)],
            ASSUNTO: [MessageHandler(Filters.text & ~Filters.command, get_assunto)],
            AUDIO: [
                MessageHandler(Filters.audio, get_audio),
                MessageHandler(Filters.voice, get_voice),
                MessageHandler(Filters.text & ~Filters.command, not_audio)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dp.add_handler(conv_handler)
    duda.start_polling()
    duda.idle()

if __name__ == "__main__":
    main()
