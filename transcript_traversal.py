import requests
from bs4 import BeautifulSoup
from sys import stderr
from json import dump
from html2text import html2text
from markdown2 import markdown
import click


class TranscriptTraversal:
    candidate_dict = {
        'SANDERS': 'BERNIE SANDERS',
        'BENNET': 'MICHAEL BENNET',
        'BIDEN': 'JOE BIDEN',
        'HARRIS': 'KAMALA HARRIS',
        'HICKENLOOPER': 'JOHN HICKENLOOPER',
        'GILLIBRAND': 'KIRSTEN GILLIBRAND',
        'BUTTIGIEG': 'PETE BUTTIGIEG',
        'SWALWELL': 'ERIC SWALWELL',
        'YANG': 'ANDREW YANG',
        'WILLIAMSON': 'MARIANNE WILLIAMSON',
        'WARREN': 'ELIZABETH WARREN',
        'KLOBUCHAR': 'AMY KLOBUCHAR',
        "O'ROURKE": "BETO O'ROURKE",
        'BOOKER': 'CORY BOOKER',
        'CASTRO': 'JULIAN CASTRO',
        'GABBARD': 'TULSI GABBARD',
        'DELANEY': 'JOHN DELANEY',
        'INSLEE': 'JAY INSLEE',
        'RYAN': 'TIM RYAN',
        'DEBLASIO': 'BILL DEBLASIO'
    }

    def __init__(self, transcript_url=None):
        self.list_of_speakers = []
        self.raw_transcript = []
        self.word_count = {}
        self.structured_transcript = self.create_structured_transcript(transcript_url)
        pass

    def create_structured_transcript(self, transcript_url):
        try:
            r = requests.get(transcript_url, headers={'User-Agent': 'Mozilla/5.0', 'referrer': 'https://l.facebook.com/'})
            raw_html = r.text
            markdown_text = html2text(raw_html)
            html_converted = markdown(markdown_text)
            raw_transcript_html = BeautifulSoup(html_converted, features='html.parser').find_all('p')
            raw_transcript = []
            processed_transcript = []
            list_of_speakers = []
            new_statement = []
            trim_switch_beginning = True
            statement_index = 1
            statement_counter = 0
            structured_transcript = {}
            for line in raw_transcript_html:
                line = line.get_text().strip().split()
                if line != [] and line != [""]:
                    for word in line:
                        raw_transcript.append(word)
                        if ":" in word and word[-1] == ':' and line.index(word) == 0:
                            if word[0:-1] not in list_of_speakers:
                                list_of_speakers.append(word[0:-1])
            for item in raw_transcript:
                if item[0:-1] not in list_of_speakers and trim_switch_beginning is True:
                    continue
                if item[0:-1] in list_of_speakers and trim_switch_beginning is True:
                    trim_switch_beginning = False
                    processed_transcript.append(item)
                    new_statement = []
                    new_statement.append(item)
                    statement_counter += 1
                    continue
                if (item[0:-1]) not in list_of_speakers and trim_switch_beginning is False:
                    new_statement.append(item)
                    processed_transcript.append(item)
                    structured_transcript[statement_index] = {}
                    structured_transcript[statement_index]['index'] = statement_index
                    structured_transcript[statement_index]['speaker'] = new_statement[0][:(len(new_statement[0]) - 1)]
                    structured_transcript[statement_index]['time_begin'] = ''
                    structured_transcript[statement_index]['subtitle_index_begin'] = ''
                    structured_transcript[statement_index]['time_end'] = ''
                    structured_transcript[statement_index]['subtitle_index_end'] = ''
                    structured_transcript[statement_index]['content'] = " ".join(new_statement[1:]).replace("\n", " ")
                    continue
                if item[0:-1] in list_of_speakers and trim_switch_beginning is False:
                    processed_transcript.append(item)
                    structured_transcript[statement_index] = {}
                    structured_transcript[statement_index]['index'] = statement_index
                    structured_transcript[statement_index]['speaker'] = new_statement[0][:(len(new_statement[0]) - 1)]
                    structured_transcript[statement_index]['time_begin'] = ''
                    structured_transcript[statement_index]['subtitle_index_begin'] = ''
                    structured_transcript[statement_index]['time_end'] = ''
                    structured_transcript[statement_index]['subtitle_index_end'] = ''
                    structured_transcript[statement_index]['content'] = " ".join(new_statement[1:]).replace("\n", " ")
                    statement_index += 1
                    new_statement = []
                    new_statement.append(item)
                    statement_counter += 1
                    continue

            # Removing everything in the HTTP response after the debate transcript.
            structured_transcript[statement_index]['content'] = structured_transcript[statement_index]['content'][:(structured_transcript[statement_index]['content'].index(' The above transcript'))]

            # Saving our list of speakers, raw transcript and structured transcript into instance variables.
            self.list_of_speakers = list_of_speakers
            self.raw_transcript = processed_transcript
            try:
                self.structured_transcript = structured_transcript
                return structured_transcript
            except AttributeError:
                print('ALERT: Structured transcript created.')
                return structured_transcript

        except KeyError:
            stderr.write(f"INVALID URL: Enter valid URL of NYT debate transcript. {transcript_url} is invalid.")

        except TypeError:
            stderr.write(f"URL REQUIRED: Enter valid URL of NYT debate transcript.")

    def download_structured_transcript(self):
        filename = input("What would you like to name this structured transcript? (do not include the file extension, i.e. .json):\t")
        with open(f'results/{filename}.json', 'w') as download_file:
            dump(self.structured_transcript, download_file, indent=4)
        print(f'ALERT: Structured transcript ({filename}.json) successfully downloaded!')

    def get_word_count(self):
        word_count = {}
        replace_dict = {
            ".": "",
            ",": "",
            "?": "",
            "!": "",
        }
        for index in self.structured_transcript.keys():
            speaker = self.structured_transcript[index]['speaker']
            if speaker not in word_count.keys():
                word_count[speaker] = {}
                word_count[speaker]['word_count'] = 0
                word_count[speaker]['words'] = []
                word_count[speaker]['unduplicated_word_count'] = 0
                word_count[speaker]['unduplicated_words'] = []
            for word in self.structured_transcript[index]['content'].split():
                word = word.upper()
                for key, replacement in replace_dict.items():
                    word = word.replace(key, replacement)
                try:
                    if word[0] != "(" and word[-1] != ")" and word != "" and word != " ":
                        word_count[speaker]['word_count'] += 1
                        word_count[speaker]['words'].append(word)
                        if word not in word_count[speaker]['unduplicated_words']:
                            word_count[speaker]['unduplicated_word_count'] += 1
                            word_count[speaker]['unduplicated_words'].append(word)
                except IndexError:
                    print("Standalone punctuation was replaced with '' and should not be included in the word count. See line below")
                    print("LINE:", self.structured_transcript[index]['content'].split())
                    continue

        self.word_count = word_count
        return self.word_count

    def download_word_count(self):
        if self.word_count != {}:
            filename = input("What would you like to name this word count? (do not include the file extension, i.e. .json):\t")
            with open(f'results/{filename}.json', 'w') as download_file:
                dump(self.word_count, download_file, indent=4)
            print(f'ALERT: Word count ({filename+".json"}) successfully downloaded!')
        else:
            self.get_word_count()
            self.download_word_count()
            

if __name__ == '__main__':
    @click.command()
    @click.option('--url', default=None, prompt='Debate transcript URL', help='URL of NYT debate transcript.')
    @click.option('--structured', is_flag=True, default=False, help='Download structured transcript (.json).')
    @click.option('--word_count', is_flag=True, default=False, help='Download word count (.json).')
    def transcript_traversal_cli(url, structured, word_count):
        traverser = TranscriptTraversal(url)
        if structured:
            traverser.download_structured_transcript()
        if word_count:
            traverser.download_word_count()
        elif not structured and not word_count:
            print(traverser.structured_transcript)
        else:
            return traverser.structured_transcript

    transcript_traversal_cli()
