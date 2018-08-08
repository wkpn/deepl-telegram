import requests
import json
import sys
import re


class DeepL:
    def __init__(self):
        self.request_id = 0

    def translate(self, text, source='auto', target=None, preferred_langs=[]):
        paragraphs = self.split_paragraphs(text)
        sentences = self.request_split_sentences(paragraphs, source, preferred_langs)
        result = self.request_translate(sentences, source, target, preferred_langs)
        translation = self.insert_translation(result['translations'], sentences, text)

        return translation, {
            'source': result['source'],
            'target': result['target']
        }

    @staticmethod
    def split_paragraphs(text):
        cleaned_paragraphs = []
        parts = re.split(r'(?:\s*\n)+\s*', text)

        for part in parts:
            part = part.lstrip().rstrip()

            if len(part) > 0:
                cleaned_paragraphs.append(part)

        return cleaned_paragraphs

    @staticmethod
    def insert_translation(translated_sentences, original_sentences, original_text):
        translated_sentences = translated_sentences[:]
        original_sentences = original_sentences[:]

        for i, orig_sentence in enumerate(original_sentences):
            if translated_sentences[i] is None:
                translated_sentences[i] = orig_sentence

            whitespace = re.findall(r'^\s*', original_text)[0]
            translated_sentences[i] = whitespace + translated_sentences[i]
            original_text = original_text[len(whitespace):]

            if original_text.startswith(orig_sentence):
                original_text = original_text[len(orig_sentence):]
            else:
                print('\n\nSomething went wrong.', file=sys.stderr)

        return ''''''.join(translated_sentences)

    def request_split_sentences(self, paragraphs, source, preferred_langs):
        request_paragraphs = []
        request_paragraph_ids = []
        splitted_paragraphs = []

        for i, paragraph in enumerate(paragraphs):
            if re.search(r'[.!?\':].*\S.*$', paragraph, re.M):
                request_paragraphs.append(paragraph)
                request_paragraph_ids.append(i)
                splitted_paragraphs.append([])
            else:
                splitted_paragraphs.append([paragraph])

        self.request_id += 1
        current_id = self.request_id

        url = 'https://www2.deepl.com/jsonrpc'
        headers = {'content-type': 'application/json'}

        payload = {
            'method': 'LMT_split_into_sentences',
            'params': {
                'texts': [p for p in request_paragraphs],
                'lang': {
                    'lang_user_selected': source,
                    'user_preferred_langs': json.dumps(preferred_langs),
                },
            },
            'jsonrpc': '2.0',
            'id': current_id,
        }

        response = requests.post(url, data=json.dumps(payload), headers=headers).json()

        for i, paragraph in enumerate(response['result']['splitted_texts']):
            splitted_paragraphs[request_paragraph_ids[i]] = paragraph

        return [s for paragraph in splitted_paragraphs for s in paragraph]

    def request_translate(self, sentences, source, target, preferred_langs):
        self.request_id += 1
        current_id = self.request_id

        url = 'https://www2.deepl.com/jsonrpc'
        headers = {'content-type': 'application/json'}

        payload = {
            'method': 'LMT_handle_jobs',
            'params': {
                'jobs': [
                    {
                        'raw_en_sentence': sentence,
                        'kind': 'default'
                    } for sentence in sentences
                ],
                'lang': {
                    'user_preferred_langs': preferred_langs,
                },
            },
            'jsonrpc': '2.0',
            'id': current_id,
        }

        payload['params']['lang']['source_lang_user_selected'] = source
        payload['params']['lang']['target_lang'] = target

        r = requests.post(url, data=json.dumps(payload), headers=headers).json()

        return {
            'translations': [
                r['result']['translations'][i]['beams'][0]['postprocessed_sentence']
                if len(r['result']['translations'][i]['beams']) else None
                for i in range(len(r['result']['translations']))
            ],
            'source': r['result']['source_lang'],
            'target': r['result']['target_lang']
        }
