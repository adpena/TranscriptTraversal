# First, I am going to explore the structure of the transcript. I copied it from the New York Times website (https://www.nytimes.com/2019/06/28/us/politics/transcript-debate.html) using getkontent.com (getkontent.com/TRANSCRIPT_URL) and pasted it into a text file named "transcript_debate 2.txt" that is located in the same directory as this exploratory script.
with open('transcript_debate 2.txt', 'r', encoding='UTF-8') as transcript_debate_2:
    # Using the .split() method to create a list of words in each line of the file and then appending them to the full ordered list of words in the transcript. Later on, we will perform an operation to deduplicate the words in the list.
    transcript_list = []
    for line in transcript_debate_2:
        words_list = line.split()
        for word in words_list:
            transcript_list.append(word)
    print('Full transcript:', transcript_list)

    # Creating a new list to store the deduplicated list of words in the transcript in.
    deduplicated_transcript_list = []
    for word in transcript_list:
        if word.upper() not in deduplicated_transcript_list:
            deduplicated_transcript_list.append(word.upper())
        else:
            pass
    print('Deduplicated:', deduplicated_transcript_list)

    # Creating a new list to identify the words with colons in them - can we use them to identify when a candidate will begin speaking?
    words_with_colons = []
    for word in deduplicated_transcript_list:
        if ":" in word:
            words_with_colons.append(word)
    print('Words with colons(names):', words_with_colons)

    # Counting the number of times an individual's name appears in the transcript (and the time 3:00 AM lol this is important to recognize for understanding the data and for parsing future transcripts, anticipating potential for errors). NOTE: this includes times they were interrupted and got a few words out before continuing their thoughts in a few moments.
    name_count = {}
    for name in words_with_colons:
        name_count[name] = 0
    transcript_debate_2.seek(0)
    for line in transcript_debate_2:
        words_list = line.split()
        for word in words_list:
            for name in words_with_colons:
                if word == name:
                    name_count[name] += 1
    print('Name count:', name_count)

    # Making sure that an individual's NAME: does not occur twice in any lines (like '3:00' does)
    transcript_debate_2.seek(0)
    broken_lines = []
    for line in transcript_debate_2:
        broken_lines_local = []
        words_list = line.split()
        for word in words_list:
            for name in words_with_colons:
                if word == name:
                    broken_lines_local.append(word)
        if len(broken_lines_local) > 1:
            broken_lines.append(line)
    print('Broken line(s):', broken_lines)

    # Since that has been confirmed, we should be able to use an individual's NAME: to mark the beginning of a statement and the appearance of a different individual's NAME: to indicate that a statement has ended. Confirming that an individual's NAME: does not occur more than once in a row.
    transcript_debate_2.seek(0)
    name_tracker = {
        'PREVIOUS': '',
        'CURRENT': ''
    }
    consecutive_statements = []
    line_counter = 0
    for line in transcript_debate_2:
        line_counter += 1
        words_list = line.split()
        for word in words_list:
            for name in words_with_colons:
                if word == name:
                    name_tracker['CURRENT'] = word
                    if name_tracker['CURRENT'] == name_tracker['PREVIOUS']:
                        consecutive_statements.append((line_counter, line))
                    name_tracker['PREVIOUS'] = name_tracker['CURRENT']
    print('Consecutive statement(s):', consecutive_statements)
    # The results of this print statement indicate that there are multiple times where an individual was cut off while making a statement or asking a question as is reflected in the transcript (this is important to keep in mind for purposes of parsing the transcript).

    import srt

    # Now, we are going to begin exploring the subtitles file ripped from the YouTube video (NBC News - https://www.youtube.com/watch?v=cX7hni-zGD8) for the debate. I am primarily interested in identifying the time that each statement is begun, adding this data along with an index to the transcript and otherwise formatting it so that it can be used as a .srt subtitles file.
    with open('Democratic Presidential Debate - June 27 (Full) _ NBC News - English - CC1.srt', 'r') as subtitle_file:
        subtitles = list(srt.parse(subtitle_file.read()))
        # This is how you access the content in each subtitle.
        # print(subs[0].content)

    # How to match the subtitles to the transcript, now that we understand the transcript's and subtitles' structure?

    # Iterate through the transcript. For each statement, iterate through the subtitles until you've found a match. Then identify the time and save it.
    # Remove 3:00 from the list of candidate and moderator names so the error no longer trickles down.
    individuals_list = words_with_colons[:-1]

    structured_transcript = {}
    transcript_debate_2.seek(0)
    new_subtitle = []
    subtitle_counter = 0
    index = 1
    read_switch = False
    # Create a dictionary of structured transcript data. Format should be: index, time (), content.
    for word in transcript_list:
        if word in individuals_list and read_switch is False:
            new_subtitle = []
            new_subtitle.append(word)
            read_switch = True
            subtitle_counter += 1
            continue
        if word not in individuals_list and read_switch is True:
            new_subtitle.append(word)
            subtitle_counter += 1
        if word not in individuals_list and read_switch is True and subtitle_counter == len(transcript_list):
            structured_transcript[index] = {}
            structured_transcript[index]['index'] = index
            structured_transcript[index]['speaker'] = new_subtitle[0][:(len(new_subtitle[0]) - 1)]
            structured_transcript[index]['time_begin'] = ''
            structured_transcript[index]['subtitle_index_begin'] = ''
            structured_transcript[index]['time_end'] = ''
            structured_transcript[index]['subtitle_index_end'] = ''
            structured_transcript[index]['content'] = " ".join(new_subtitle[1:])
        if word in individuals_list and read_switch is True:
            structured_transcript[index] = {}
            structured_transcript[index]['index'] = index
            structured_transcript[index]['speaker'] = new_subtitle[0][:(len(new_subtitle[0]) - 1)]
            structured_transcript[index]['time_begin'] = ''
            structured_transcript[index]['subtitle_index_begin'] = ''
            structured_transcript[index]['time_end'] = ''
            structured_transcript[index]['subtitle_index_end'] = ''
            structured_transcript[index]['content'] = " ".join(new_subtitle[1:])
            index += 1
            new_subtitle = []
            new_subtitle.append(word)
            subtitle_counter += 1
            continue

    import json
    print('Structured transcript:', json.dumps(structured_transcript, indent=2))

    with open('structured_transcript_debate 2.json', 'r') as structured_transcript_json:
        structured_transcript_json = json.load(structured_transcript_json)
        for index in structured_transcript_json.keys():
            if structured_transcript_json[index]['subtitle_index_begin'] == '':
                print()
                print("Structured index:", index)
                print("Content:", structured_transcript_json[index]['content'])
                break

    # Now, we're going to create a new file that searches the subtitles for segments' start/end times based on their indexes and then converts the start index into a YouTube url.
    debate_video_url = 'https://youtu.be/cX7hni-zGD8'
    time_extension = '?t='
    structured_transcript_json_w_url = structured_transcript_json
    with open('structured_transcript_debate 2_w url.json', 'w') as structured_transcript_json_w_url_file:
        for index in structured_transcript_json_w_url.keys():
            subtitle_index_begin = structured_transcript_json_w_url[index]['subtitle_index_begin']
            subtitle_index_end = structured_transcript_json_w_url[index]['subtitle_index_end']
            time_begin = ''
            time_end = ''
            time_begin_formatted = ''
            for subtitle in subtitles:
                if str(subtitle.index) == subtitle_index_begin:
                    time_begin = subtitle.start
                    time_begin_formatted = str(time_begin).split(":")
                    time_begin_formatted = str(time_begin_formatted[0]) + "h" + str(time_begin_formatted[1]) + "m" + str(round(float(time_begin_formatted[2]))) + "s"
                if str(subtitle.index) == subtitle_index_end:
                    time_end = subtitle.end
            structured_transcript_json_w_url[index]['url'] = debate_video_url + time_extension + time_begin_formatted
            structured_transcript_json_w_url[index]['time_begin'] = str(time_begin)
            structured_transcript_json_w_url[index]['time_end'] = str(time_end)

        json.dump(structured_transcript_json_w_url, structured_transcript_json_w_url_file, indent=2)

    with open('linked_transcript_debate 2.html', 'w') as linked_transcript_debate_2_file:
        linked_transcript_debate_2 = ''
        for index in structured_transcript_json_w_url:
            linked_transcript_debate_2 += '<p>' + structured_transcript_json_w_url[index]['speaker'] + ': ' + structured_transcript_json_w_url[index]['content'] + ' <a href="' + structured_transcript_json_w_url[index]['url'] + '" target="_blank"> Begins: ' + structured_transcript_json_w_url[index]['time_begin'] + '</a></p>'

        linked_transcript_debate_2_file.write(linked_transcript_debate_2)

    linked_transcript_debate_2_file.close()
    subtitle_file.close()
    transcript_debate_2.close()
    structured_transcript_json_w_url_file.close()

    # How many times was there applause? Cross-talk?
