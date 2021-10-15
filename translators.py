from googletrans import Translator

translator = Translator()


def get_translate_ru_to_en(string):
    result = translator.translate(string, dest='en')
    return result.text


def get_translate_en_to_ru(string):
    result = translator.translate(string, dest='ru')
    return result.text
