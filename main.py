import json
import argparse
import os
from bs4 import BeautifulSoup

# --- Language Configuration ---
LANGUAGES = {
    "en": {
        "error_html_not_found": "Error: HTML file not found at {path}",
        "error_reading_html": "Error reading HTML file: {error}",
        "no_turns_found": "No conversation turns found with the specified <article> structure.",
        "check_html_structure": "Please check the HTML structure and adjust the script if necessary.",
        "attempting_direct_find": "Attempting to find message containers directly...",
        "found_direct_containers": "Found {count} direct message containers. Processing them.",
        "could_not_find_text_for_role": "Could not find text content for a message with role '{role}'",
        "no_direct_containers_found": "No direct message containers found either.",
        "warning_no_text_content": "Warning: Found a {speaker} message (turn #{index}) but no text content inside the expected div.",
        "no_history_extracted": "No chat history could be extracted. The JSON file will be empty or not created.",
        "error_writing_json": "Error writing JSON file: {error}",
        "history_extracted_success": "Chat history successfully extracted to {path}",
        "cli_description": "Extracts chat history from an HTML file and saves it as a JSON format.",
        "cli_html_file_help": "Path to the HTML file from which to extract data.",
        "cli_output_help": (
            "Path to the JSON file where the extracted chat history will be saved.\n"
            "If not specified, a file with the same name as the HTML file (but .json extension)\n"
            "will be created in the same directory."
        ),
        "cli_language_help": "Language for script messages (en or ka). Default: en",
        "verification_header": "\n--- Verification ---",
        "verification_extracted_count": "Extracted {count} messages.",
        "verification_first_message": "First message:",
        "verification_last_message": "Last message:",
        "verification_json_empty": "JSON file ({path}) is empty.",
        "verification_json_not_created": "JSON file {path} was not created.",
        "error_decode_json": "Error: Could not decode the JSON file {path}. It might be malformed.",
        "error_verification": "An error occurred during verification: {error}"
    },
    "ka": {
        "error_html_not_found": "შეცდომა: HTML ფაილი ვერ მოიძებნა მითითებულ გზაზე: {path}",
        "error_reading_html": "შეცდომა HTML ფაილის წაკითხვისას: {error}",
        "no_turns_found": "ვერ მოიძებნა საუბრის სტრუქტურა მითითებული <article> ტეგებით.",
        "check_html_structure": "გთხოვთ, შეამოწმოთ HTML სტრუქტურა და საჭიროებისამებრ შეცვალოთ სკრიპტი.",
        "attempting_direct_find": "ვცდილობ შეტყობინებების კონტეინერების პირდაპირ მოძებნას...",
        "found_direct_containers": "მოიძებნა {count} პირდაპირი შეტყობინების კონტეინერი. მიმდინარეობს დამუშავება.",
        "could_not_find_text_for_role": "ვერ მოხერხდა ტექსტის შიგთავსის პოვნა როლისთვის: '{role}'",
        "no_direct_containers_found": "პირდაპირი შეტყობინების კონტეინერებიც ვერ მოიძებნა.",
        "warning_no_text_content": "გაფრთხილება: მოიძებნა {speaker} შეტყობინება ( #{index} ), მაგრამ ტექსტის შიგთავსი ვერ მოიძებნა მოსალოდნელ div-ში.",
        "no_history_extracted": "ჩატის ისტორია ვერ იქნა ამოღებული. JSON ფაილი ცარიელი იქნება ან არ შეიქმნება.",
        "error_writing_json": "შეცდომა JSON ფაილში ჩაწერისას: {error}",
        "history_extracted_success": "ჩატის ისტორია წარმატებით იქნა შენახული ფაილში: {path}",
        "cli_description": "ამოიღებს ჩატის ისტორიას HTML ფაილიდან და შეინახავს JSON ფორმატში.",
        "cli_html_file_help": "HTML ფაილის მისამართი, საიდანაც უნდა მოხდეს მონაცემების ამოღება.",
        "cli_output_help": (
            "JSON ფაილის მისამართი, სადაც შეინახება ამოღებული ჩატის ისტორია.\n"
            "თუ არ არის მითითებული, შეიქმნება ფაილი იგივე სახელით, რაც HTML ფაილს აქვს,\n"
            "ოღონდ .json გაფართოებით, იმავე დირექტორიაში."
        ),
        "cli_language_help": "სკრიპტის შეტყობინებების ენა (en ან ka). ნაგულისხმევი: en",
        "verification_header": "\n--- ვერიფიკაცია ---",
        "verification_extracted_count": "ამოღებულია {count} შეტყობინება.",
        "verification_first_message": "პირველი შეტყობინება:",
        "verification_last_message": "ბოლო შეტყობინება:",
        "verification_json_empty": "JSON ფაილი ({path}) ცარიელია.",
        "verification_json_not_created": "JSON ფაილი {path} არ შეიქმნა.",
        "error_decode_json": "შეცდომა: ვერ მოხერხდა JSON ფაილის ({path}) დეკოდირება. შესაძლოა, ფაილი დაზიანებულია.",
        "error_verification": "ვერიფიკაციისას მოხდა შეცდომა: {error}"
    }
}

CURRENT_LANG = "en" # Default language
TEXTS = LANGUAGES[CURRENT_LANG]

def set_language(lang_code):
    global CURRENT_LANG, TEXTS
    if lang_code in LANGUAGES:
        CURRENT_LANG = lang_code
        TEXTS = LANGUAGES[lang_code]
    else:
        print(f"Warning: Language code '{lang_code}' not supported. Using default 'en'.") # Keep this in English as a fallback
        CURRENT_LANG = "en"
        TEXTS = LANGUAGES["en"]
# --- End Language Configuration ---

def extract_chat_history_to_json(html_file_path, json_file_path):
    chat_history = []

    if not os.path.exists(html_file_path):
        print(TEXTS["error_html_not_found"].format(path=html_file_path))
        return

    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        print(TEXTS["error_reading_html"].format(error=e))
        return

    soup = BeautifulSoup(html_content, 'html.parser')
    turns = soup.find_all('article', attrs={'data-testid': lambda x: x and x.startswith('conversation-turn-')})

    if not turns:
        print(TEXTS["no_turns_found"])
        print(TEXTS["check_html_structure"])
        print(TEXTS["attempting_direct_find"])
        message_containers = soup.find_all('div', attrs={'data-message-author-role': True})
        if message_containers:
            print(TEXTS["found_direct_containers"].format(count=len(message_containers)))
            for container in message_containers:
                role = container.get('data-message-author-role')
                text_div = container.find('div', class_='whitespace-pre-wrap') # User messages
                if not text_div:
                     text_div = container.find('div', class_='markdown') # Assistant messages

                if text_div:
                    # Simplified text extraction for direct containers for now
                    # Complex markdown parsing like in article turns can be added if needed
                    text_content = ""
                    if role == "user":
                        text_content = text_div.get_text(separator='\n', strip=True)
                    elif role == "assistant":
                        parts = []
                        for element in text_div.find_all(['p', 'pre', 'ul', 'ol', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'table', 'hr'], recursive=False):
                            if element.name == 'pre':
                                code_tag = element.find('code')
                                lang_container = element.find_previous_sibling('div')
                                lang = "text"
                                if lang_container and 'flex' in lang_container.get('class', []) and 'items-center' in lang_container.get('class', []):
                                    lang_div_candidates = lang_container.find_all('div')
                                    if lang_div_candidates:
                                        for candidate_div in reversed(lang_div_candidates):
                                            div_text = candidate_div.get_text(strip=True)
                                            if div_text and div_text.lower() not in ["copy", "edit", "copy code"]:
                                                lang = div_text
                                                break
                                code_content = code_tag.get_text(strip=True) if code_tag else element.get_text(strip=True)
                                parts.append(f"```{lang}\n{code_content}\n```")
                            elif element.name in ['ul', 'ol']:
                                list_items = ""
                                for item_index, li in enumerate(element.find_all('li', recursive=False)):
                                    prefix = "- " if element.name == 'ul' else f"{item_index + 1}. "
                                    list_items += prefix + li.get_text(separator='\n  ', strip=True) + "\n"
                                parts.append(list_items.strip())
                            elif element.name and element.name.startswith('h') and len(element.name) > 1 and element.name[1].isdigit():
                                level = int(element.name[1])
                                parts.append("#" * level + " " + element.get_text(strip=True))
                            elif element.name == 'blockquote':
                                quote_lines = element.get_text(separator='\n', strip=True).split('\n')
                                formatted_quote = "\n".join([f"> {line}" for line in quote_lines])
                                parts.append(formatted_quote)
                            elif element.name == 'table':
                                table_md = ""
                                header_row = element.find('thead')
                                if not header_row:
                                    header_row = element.find('tr')

                                if header_row:
                                    header_tags = header_row.find_all(['th', 'td'])
                                    header = [th.get_text(strip=True) for th in header_tags]
                                    if header:
                                        table_md += "| " + " | ".join(header) + " |\n"
                                        table_md += "| " + " | ".join(["---"] * len(header)) + " |\n"
                                
                                body_rows_container = element.find('tbody')
                                if not body_rows_container:
                                    body_rows_container = element
                                
                                rows_to_process = body_rows_container.find_all('tr', recursive=False)
                                if header_row and header_row.find_parent('tbody') is None and header_row in rows_to_process :
                                     if rows_to_process and rows_to_process[0] == header_row:
                                        rows_to_process = rows_to_process[1:]

                                for row_idx, row_item in enumerate(rows_to_process):
                                    # Avoid reprocessing the header row if it was caught without a thead
                                    if not element.find('thead') and row_idx == 0 and row_item == header_row:
                                        continue
                                    cols = [td.get_text(strip=True) for td in row_item.find_all('td', recursive=False)]
                                    if cols:
                                        table_md += "| " + " | ".join(cols) + " |\n"
                                parts.append(table_md.strip())
                            elif element.name == 'hr':
                                parts.append("\n---\n")
                            elif element.name == 'p':
                                parts.append(element.get_text(strip=True))
                        
                        text_content_parts = []
                        for i, part in enumerate(parts):
                            if part.strip(): # Add non-empty parts
                                text_content_parts.append(part.strip())
                        text_content = "\n\n".join(text_content_parts) # Join with double newlines for markdown paragraphs

                    if role and text_content is not None: # Check for not None, as empty string is valid
                        speaker_val = "user" if role == "user" else "assistant"
                        chat_history.append({"speaker": speaker_val, "text": text_content})
                else:
                    print(TEXTS["could_not_find_text_for_role"].format(role=role))
        else:
            print(TEXTS["no_direct_containers_found"])
            return

    # This `for` loop is the primary extraction logic if `turns` were found
    for turn_index, turn in enumerate(turns):
        user_message_div = turn.find('div', attrs={'data-message-author-role': 'user'})
        assistant_message_div = turn.find('div', attrs={'data-message-author-role': 'assistant'})

        speaker = None
        text_content = None # Initialize to None

        if user_message_div:
            speaker = "user"
            text_div = user_message_div.find('div', class_='whitespace-pre-wrap')
            if text_div:
                text_content = text_div.get_text(separator='\n', strip=True)
        elif assistant_message_div:
            speaker = "assistant"
            text_div = assistant_message_div.find('div', class_='markdown')
            if text_div:
                parts = []
                for element in text_div.find_all(['p', 'pre', 'ul', 'ol', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'table', 'hr'], recursive=False):
                    if element.name == 'pre':
                        code_tag = element.find('code')
                        lang_container = element.find_previous_sibling('div')
                        lang = "text"
                        if lang_container and 'flex' in lang_container.get('class', []) and 'items-center' in lang_container.get('class', []):
                            lang_div_candidates = lang_container.find_all('div')
                            if lang_div_candidates:
                                for candidate_div in reversed(lang_div_candidates):
                                    div_text = candidate_div.get_text(strip=True)
                                    if div_text and div_text.lower() not in ["copy", "edit", "copy code"]: # More specific check
                                        lang = div_text
                                        break
                        code_content = code_tag.get_text(strip=True) if code_tag else element.get_text(strip=True)
                        parts.append(f"```{lang}\n{code_content}\n```")
                    elif element.name in ['ul', 'ol']:
                        list_items = ""
                        for item_index, li in enumerate(element.find_all('li', recursive=False)):
                            prefix = "- " if element.name == 'ul' else f"{item_index + 1}. "
                            list_items += prefix + li.get_text(separator='\n  ', strip=True) + "\n"
                        parts.append(list_items.strip())
                    elif element.name and element.name.startswith('h') and len(element.name) > 1 and element.name[1].isdigit():
                        level = int(element.name[1])
                        parts.append("#" * level + " " + element.get_text(strip=True))
                    elif element.name == 'blockquote':
                        quote_lines = element.get_text(separator='\n', strip=True).split('\n')
                        formatted_quote = "\n".join([f"> {line.strip()}" for line in quote_lines if line.strip()]) # Add > to each line
                        parts.append(formatted_quote)
                    elif element.name == 'table':
                        table_md = ""
                        header_row = element.find('thead')
                        if not header_row: # if no thead, try finding first tr as header
                            header_row = element.find('tr')

                        if header_row:
                            header_tags = header_row.find_all(['th', 'td'])
                            header = [th.get_text(strip=True) for th in header_tags]
                            if header:
                                table_md += "| " + " | ".join(header) + " |\n"
                                table_md += "| " + " | ".join(["---"] * len(header)) + " |\n"
                        
                        body_rows_container = element.find('tbody')
                        if not body_rows_container: # if no tbody, use all trs
                            body_rows_container = element
                        
                        rows_to_process = body_rows_container.find_all('tr', recursive=False) # Get only direct children trs
                        
                        # Avoid reprocessing the header row if it was already handled (e.g. no thead tag present)
                        if header_row and header_row.find_parent('tbody') is None and header_row in rows_to_process:
                             if rows_to_process and rows_to_process[0] == header_row:
                                rows_to_process = rows_to_process[1:]


                        for row_item in rows_to_process:
                            cols = [td.get_text(strip=True) for td in row_item.find_all('td', recursive=False)] # direct children td
                            if cols: # only if row has columns
                                table_md += "| " + " | ".join(cols) + " |\n"
                        parts.append(table_md.strip())
                    elif element.name == 'hr':
                        parts.append("\n---\n")
                    elif element.name == 'p': # Explicitly handle paragraphs
                         parts.append(element.get_text(strip=True))
                
                # Join parts, ensure non-empty parts are joined with double newlines
                text_content_parts = []
                for i, part in enumerate(parts):
                    if part.strip(): # Add non-empty parts
                        text_content_parts.append(part.strip())
                text_content = "\n\n".join(text_content_parts)

        if speaker and text_content is not None: # Allow empty string as valid content
            chat_history.append({
                "speaker": speaker,
                "text": text_content
            })
        elif speaker and text_content is None: # Only print warning if speaker was identified but no text
             print(TEXTS["warning_no_text_content"].format(speaker=speaker, index=turn_index + 1))

    if not chat_history:
        print(TEXTS["no_history_extracted"])
        return

    try:
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(chat_history, f, ensure_ascii=False, indent=2)
        print(TEXTS["history_extracted_success"].format(path=json_file_path))
    except Exception as e:
        print(TEXTS["error_writing_json"].format(error=e))

if __name__ == '__main__':
    # Initialize parser with general descriptions
    parser = argparse.ArgumentParser(
        description="Extracts chat history from HTML to JSON.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "html_file",
        help="Path to the HTML file from which to extract data."
    )
    parser.add_argument(
        "-o", "--output",
        dest="json_file",
        help=(
            "Path to the JSON file where the extracted chat history will be saved.\n"
            "If not specified, a file with the same name as the HTML file (but .json extension)\n"
            "will be created in the same directory."
        ),
        default=None
    )
    parser.add_argument(
        "-l", "--lang",
        dest="language",
        choices=["en", "ka"],
        default="en",
        help="Language for script messages (en or ka). Default: en"
    )

    args = parser.parse_args()

    # Set language based on argument BEFORE updating help texts
    set_language(args.language)

    # Update parser descriptions and help texts with the chosen language
    # This makes the -h output also translated
    parser.description = TEXTS["cli_description"]
    for action in parser._actions:
        if action.dest == "html_file":
            action.help = TEXTS["cli_html_file_help"]
        elif action.dest == "json_file": # Corresponds to --output
            action.help = TEXTS["cli_output_help"]
        elif action.dest == "language": # Corresponds to --lang
            action.help = TEXTS["cli_language_help"]


    html_input_path = args.html_file
    json_output_path = args.json_file

    if json_output_path is None:
        base = os.path.splitext(html_input_path)[0]
        json_output_path = base + ".json"

    extract_chat_history_to_json(html_input_path, json_output_path)

    # --- Verification (Optional) ---
    if os.path.exists(json_output_path):
        try:
            with open(json_output_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data:
                    print(TEXTS["verification_header"])
                    print(TEXTS["verification_extracted_count"].format(count=len(data)))
                    if len(data) > 0:
                        print(TEXTS["verification_first_message"])
                        print(json.dumps(data[0], ensure_ascii=False, indent=2))
                    if len(data) > 1:
                        print(TEXTS["verification_last_message"])
                        print(json.dumps(data[-1], ensure_ascii=False, indent=2))
                else:
                    print(TEXTS["verification_json_empty"].format(path=json_output_path))
        except FileNotFoundError:
            # This state implies extract_chat_history_to_json would have printed an error
            pass
        except json.JSONDecodeError:
            print(TEXTS["error_decode_json"].format(path=json_output_path))
        except Exception as e:
            print(TEXTS["error_verification"].format(error=e))
    # else:
        # If the file doesn't exist, extract_chat_history_to_json should have handled the error message.
        # print(TEXTS["verification_json_not_created"].format(path=json_output_path)) # Potentially redundant