from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from spliteString import split_string
from funDownload import download
from time import time
from conversation import conversation

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
def start(update, context):
    user = update.message.from_user
    update.message.reply_text(conversation['inicio'])
    update.message.reply_text(conversation['inicio_2'])
    update.message.reply_text(conversation['materia'])
    return MATERIA

def start_2(update, context):
    words = ['start', 'help', 'inicio', 'ajuda', 'oi', 'olá', 'ola', 'começar', 'hi', 'hello']
    print(update)
    print(context)
    for word in words:
        if word == update.message.text:
            update.message.reply_text(conversation['inicio'])
            update.message.reply_text(conversation['inicio_2'])
            update.message.reply_text(conversation['materia'])
            return MATERIA
        elif word == words[-1]:
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
        update.message.reply_text(conversation['dicas'])
        update.message.reply_text(conversation['dica_1'])
        update.message.reply_text(conversation['dica_2'])
        update.message.reply_text(conversation['dica_2.1'])
        update.message.reply_text(conversation['dica_2.2'])
        update.message.reply_text(conversation['dicas_2'])
        update.message.reply_text(conversation['dica_3'])
        update.message.reply_text(conversation['dica_4'])
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
    global name_audio
    name_audio = f'{currente_date}-{audio.file_unique_id}-{update.message.from_user.id}-{materia.lower()}-{split_string(assunto)}-audio-file.mp3'
    download(url=f'{audio.file_path}', fileName=name_audio)
    update.message.reply_text(f'Seu audio {name_audio}')
    #Audio_To_Text(name_audio)
    
#função de tratamento de voice
def get_voice(update, context):
    update.message.reply_text('Só um minutinho estou processando tudo...')
    audio = update.message.voice.get_file()
    currente_date = time()
    global name_audio
    name_audio = f'{currente_date}-{audio.file_unique_id}-{update.message.from_user.id}-{materia.lower()}-{split_string(assunto)}-audio-file.mp3'
    download(url=f'{audio.file_path}', fileName=name_audio)
    update.message.reply_text(f'Seu audio {name_audio}')
    #Audio_To_Text(name_audio))

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
    # add conversa guiada
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            CommandHandler('help', start),
            CommandHandler('ajuda', start),
            CommandHandler('inicio', start),
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