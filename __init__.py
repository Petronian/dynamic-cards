from typing import Callable, Collection, Optional, Sequence, Tuple, List
from aqt import QEvent, QObject, Qt, mw, gui_hooks, QMenu
from aqt.qt import QWidget, QAction, QDialog, qconnect, QKeySequence, QKeyCombination, QApplication
from aqt.editor import Editor, EditorMode
from aqt.reviewer import Reviewer
from aqt.operations import QueryOp
from aqt.utils import tooltip as tooltip_aqt
from anki.cards import Card
from anki.notes import Note
from anki.template import TemplateRenderOutput
from random import randint
import requests
import json
import re
import time
import os

# Multitasking
import queue
import threading

# Caching
import sqlite3

# Local imports
from .dialog import WelcomeDialog, SettingsDialog
from .config import Config

# TO DO:
# * PRETTIFY FUNCTION NAMES
# * ORGANIZE CODE INTO SEPARATE FILES (SQL, ETC.) 

# Create global variables.
config_dict = mw.addonManager.getConfig(__name__)
config = Config(mw.addonManager, __name__, debug = False)

# CACHING

def connect_dynamic_db():
    conn = sqlite3.connect(config.settings.CACHE)
    return conn, conn.cursor()

def setup_dynamic_db():
    conn, cursor = connect_dynamic_db()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS id_to_strings (
        id INTEGER PRIMARY KEY,
        items TEXT,
        last_render INTEGER
    )
    """)
    conn.close()

# Debug function declarations
def clear_dynamic_db():
    conn, cursor = connect_dynamic_db()
    cursor.execute("DROP TABLE IF EXISTS id_to_strings")
    conn.close()
    setup_dynamic_db()

# Function to look up cached strings by ID
def get_strings_by_id(id_val: int) -> List[str]:
    conn, cursor = connect_dynamic_db()
    cursor.execute("SELECT items FROM id_to_strings WHERE id = ?", (id_val,))
    result = cursor.fetchone()
    if config.debug: print(f'SQL strings for {id_val}:', result)
    conn.commit()
    conn.close()
    if result and result[0]:
        return json.loads(result[0])  # Deserialize JSON string to list
    else:
        return None

# Function to look up cached strings by ID
def get_last_render_by_id(id_val: int) -> List[str]:
    conn, cursor = connect_dynamic_db()
    cursor.execute("SELECT last_render FROM id_to_strings WHERE id = ?", (id_val,))
    result = cursor.fetchone()
    if config.debug: print(f'SQL last render for {id_val}:', result)
    conn.commit()
    conn.close()
    return result[0] if result else None

# Function to look up all cached info by ID
def get_all_by_id(id_val: int) -> List[str]:
    conn, cursor = connect_dynamic_db()
    cursor.execute("SELECT items, last_render FROM id_to_strings WHERE id = ?", (id_val,))
    result = cursor.fetchone()
    if config.debug: print(f'SQL all for {id_val}:', result)
    conn.commit()
    conn.close()

    if result and result[0]:
        texts, last_render = result
        return json.loads(texts), last_render  # Deserialize JSON string to list
    else:
        return None

# Function to set cached strings by ID
def set_all_by_id(id_val: int, strings: List[str], last_render: int):
    conn, cursor = connect_dynamic_db()
    cursor.execute(f"INSERT OR REPLACE INTO id_to_strings (id, items, last_render) VALUES (?, ?, ?)", (id_val, json.dumps(strings), last_render))
    conn.commit()
    conn.close()

# Function to set cached strings by ID
def set_strings_by_id(id_val: int, strings: List[str]):
    # See if id exists
    last_render = get_last_render_by_id(id_val)
    set_all_by_id(id_val, strings, last_render if last_render is not None else 0)

# Function to set last render by ID
def set_last_render_by_id(id_val: int, last_render: int):
    # See if id exists
    strings = get_strings_by_id(id_val)
    set_all_by_id(id_val, strings if strings is not None else [], last_render)

# Additional helper function for appending strings
def append_string_by_id(id_val: int, string: str):
    old = get_strings_by_id(id_val)
    new = old + [string] if old is not None else [string] # Also handles []
    set_strings_by_id(id_val, new)

# Additional helper function for popping strings from cache
# Sets blank lists to be deleted
def pop_string_by_id(id_val: int):
    curr = get_strings_by_id(id_val)
    out = curr.pop() # Will error if curr is None or [] as intended
    if len(curr): set_strings_by_id(id_val, curr)
    else: clear_strings_by_id(id_val)
    return out
    
# Additional helper function for clearing an entry
def clear_strings_by_id(id_val: int):
    conn, cursor = connect_dynamic_db()
    cursor.execute("DELETE FROM id_to_strings WHERE id = ?", (id_val,))
    conn.commit()
    conn.close()

def _tooltip(*args, **kwargs):
    if config.debug: print(*args, **kwargs)
    tooltip_aqt(*args, **kwargs)

def tooltip(*args, **kwargs):
    mw.taskman.run_on_main(lambda: _tooltip(*args, **kwargs))

# Manage a queue for tasks.
class RewordingWorkerQueue:

    # This object must be started and should start when reviewer inits (see hook)
    def __init__(self):
        self.queue = None
        self.worker_thread = None
        self.running = False
        if config.debug: tooltip('Queue initialized.')

    # Start the worker queue if not already started.
    def start(self):
        if not self.running:
            self.queue = queue.Queue()
            self.running = True
            self.worker_thread = threading.Thread(target=self.worker, daemon=True)
            self.worker_thread.start()
            if config.debug: tooltip('Queue started.')

    # Continuously pop tasks off the queue
    # Do so one-by-one to avoid throttling!
    def worker(self):
        while self.running:
            if self.queue.empty():
                time.sleep(0.5)
            else:
                func, args = self.queue.get()
                func(args)
                self.queue.task_done()

    # Task helper method
    def _task_helper(self, card: Card):
        try:
            new_render, new_text = create_new_dynamic_cached_render(card=card, return_text=True)
            if new_render is not None:
                update_cached_card(card=card, new_render=new_render, new_text=new_text)
                if config.debug: tooltip(f'Completed new render for card {card.id}.')
            elif config.debug:
                print(f'Could not complete new render for card {card.id}.')
        except Exception as e:
            tooltip(str(e))

    # Add new tasks to the queue
    def add_render_task(self, card: Card):
        self.queue.put((self._task_helper, card))
        if config.debug: tooltip(f'Queued card {card.id} for new render.')

    # Stop the queue.
    def stop(self):
        self.running = False
        self.worker_thread.join()
        del self.queue
        del self.worker_thread
        self.queue = None
        self.worker_thread = None
        if config.debug: tooltip(f'Queue stopped.')
        # Need to unblock?

    # Reset the queue and have it start running again.
    def reset(self, immediate=False):
        self.stop(immediate=immediate)
        self.start()
        if config.debug: tooltip(f'Queue reset.')

# Card entry format for use in the cache.
class CachedCardEntry:
    id: int
    renders: Collection[TemplateRenderOutput]
    last_used_render: int
    reps: int

    def __init__(self, id, renders, reps, last_used_render) -> None:
        self.id = id
        self.last_used_render = last_used_render
        self.renders = renders
        self.reps = reps

    def __str__(self):
        return (f'[Cached card {self.id}: {self.reps} recorded reps, last used render '
                f'{self.last_used_render} (zero-indexed) of {len(self.renders)} total renders]')

# Keypress event that will be used for removing faulty revisions of a card.
class KeyPressCacheClearFilter(QObject):
    def eventFilter(self, obj: object, event: QEvent):
        if event.type() == QEvent.KeyPress:
            key_combination = event.keyCombination()
            pressed_key = QKeySequence(key_combination).toString()
            if pressed_key == config.settings.shortcut_clear_current_card:
                curr_card = mw.reviewer.card
                if curr_card is not None and curr_card.id in config.data.keys():
                    clear_card_from_cache(curr_card)
                else:
                    tooltip('No card to clear from dynamic cache.')
                # Fix bug: hitting any cache clear keys should trigger a redraw in case card isn't drawing right
                if mw.reviewer.card is not None:
                    mw.reviewer._redraw_current_card()
                return True
            elif pressed_key == config.settings.shortcut_clear_all_cards:
                if config.data:
                    clear_cache()
                else:
                    tooltip('No dynamic cache to clear.')
                # Fix bug: hitting any cache clear keys should trigger a redraw in case card isn't drawing right
                if mw.reviewer.card is not None:
                    mw.reviewer._redraw_current_card()
                return True
            elif pressed_key == config.settings.shortcut_pause:
                config.pause = not config.pause
                if config.pause:
                    tooltip('Dynamic card generation paused; will resume on Anki restart or unpause. '
                            'Existing dynamic cards will still show.')
                else:
                    tooltip('Dynamic card generation unpaused.')
            elif pressed_key == config.settings.shortcut_include_exclude and mw.reviewer:
                _, add_remove_fn = inject_include_exclude_option(mw.reviewer, None)
                add_remove_fn()

        return super().eventFilter(obj, event)

def poll_cached_card(card: Card) -> CachedCardEntry:
    if card.id not in config.data.keys():
        cached_card = get_all_by_id(card.id)
        if cached_card:
            if config.debug:
                print(f'Cached card entry for card id {card.id} exists in the dynamic database, retrieving it.')
            texts, last_render = cached_card
            renders = [create_new_manual_cached_render(card, text) for text in texts] # might be slow especially with many renders!
            config.data[card.id] = CachedCardEntry(id=card.id,
                                                    renders=renders,
                                                    reps=card.reps,
                                                    last_used_render=last_render)
        else:
            if config.debug:
                print(f'Cached card entry for card id {card.id} does not exist; creating a new one.')
            config.data[card.id] = CachedCardEntry(id=card.id,
                                                   renders=[card.render_output()],
                                                   reps=card.reps,
                                                   last_used_render=0)
            set_all_by_id(id_val=card.id, strings=[card.note().fields[0]], last_render=0) # Create a new entry in the database with the current text.
    elif config.debug:
        print(f'Cached card entry exists for {card.id}.')
    cce = config.data[card.id]
    if config.debug:
        print(f'Retrieved cached card entry {cce}.')
    return cce

def update_cached_card(card: Card,
                       reps: Optional[int] = None,
                       last_used_render: Optional[int] = None,
                       new_render: Optional[TemplateRenderOutput] = None,
                       new_text: Optional[str] = None) -> CachedCardEntry:
    
    # Set card intrinsic props.
    cce = poll_cached_card(card)

    if reps is not None:
        # cce id should match card id already.
        cce.reps = reps
        if config.debug: print(f'Updated reps for card {card.id}:', str(cce))
    if new_render is not None:
        assert new_text is not None, 'New render text must be supplied (not None) for dynamic database caching.'
        cce.renders += [new_render]
        append_string_by_id(card.id, new_text)
        if config.debug: print(f'Added render for card {card.id}:', str(cce))
    if last_used_render is not None:
        assert last_used_render >= 0 and last_used_render < len(cce.renders)
        cce.last_used_render = last_used_render
        set_last_render_by_id(card.id, last_used_render)
        if config.debug: print(f'Updated last used render for card {card.id}:', str(cce))

    config.data[card.id] = cce
    return cce

def create_new_dynamic_cached_render(card: Card, return_text: bool = False):
    # print('Making a new cached render for card ' + str(card.id))
    # print('API KEY: ' + api_key)
    ord = card.ord
    note = card.note()
    note = Note(col=note.col, id=note.id)
    if config.debug: print(f'Creating new dynamic render for card {card.id} using model \'{config.settings.model}\'')
    
    new_text = reword_card(card)
    if new_text is not None:
        if config.debug: print(f'Successfully created new dynamic render for card {card.id} using model \'{config.settings.model}\'')
        note.fields[0] = new_text
        new_render = note.ephemeral_card(ord=ord, custom_note_type=note.note_type(), custom_template=card.template()).render_output()
    else:
        if config.debug: print(f'Unsuccessfully attempted new dynamic render for card {card.id} using model \'{config.settings.model}\'')
        new_render = None
        
    if return_text:
        return new_render, new_text
    return new_render

def create_new_manual_cached_render(card: Card, text: Optional[str] = None, return_text: bool = False):
    # print('Making a new cached render for card ' + str(card.id))
    # print('API KEY: ' + api_key)
    ord = card.ord
    note = card.note()
    note = Note(col=note.col, id=note.id)
    if text: note.fields[0] = text
    if config.debug: print(f'Successfully created new manual render for card {card.id}')
    new_render = note.ephemeral_card(ord=ord, custom_note_type=note.note_type(), custom_template=card.template()).render_output()
    if return_text:
        return new_render, text
    return new_render

def randint_try_norepeat(a, b, last_draw):
    v = randint(a, b)
    if v == last_draw and a != b:
        v = v - 1 if v > 0 else v + 1
    return v

# Clear cache, either entirely or for a specific card.
def clear_card_from_cache(card: Card):
    if card is not None and card.id in config.data.keys():
        del config.data[card.id]
        clear_strings_by_id(card.id)
        tooltip(f'Cleared card {card.id} from dynamic cache.')
        
def clear_note_from_cache(note: Note):
    if note is not None:
        for card in note.cards():
            clear_card_from_cache(card)
        tooltip(f'Cleared dynamic cache for cards associated with note {note.id}.')

def clear_cache():
    config.data = {}
    clear_dynamic_db()
    tooltip('Cleared dynamic cache.')

# No need to redraw the card since that will be done anyway when the editor closes
# Only clear cache when editing new cards (only ADD_CARDS, EDIT_CURRENT, and BROWSER modes exist,
# see Editor class)
def clear_cache_on_editor_load_note(e: Editor):
    if e.editorMode == EditorMode.EDIT_CURRENT:
        clear_note_from_cache(e.note)
    # if mw.reviewer.card is not None:
    #     mw.reviewer._redraw_current_card()

# Find all cloze matches of a given ord in a cloze card.
# Case insensitive.
def get_cloze_matches(curr_qtext, ord) -> list[str]:
    pattern = r'{{c' + str(ord + 1) + r'.+?}}'
    return re.findall(pattern, curr_qtext, flags=re.RegexFlag.IGNORECASE)

# Ensure all cloze deletions are in curr_qtext.
# Case insensitive.
def validate_cloze_card(curr_qtext: str, cloze_deletions: list[Optional[str]]) -> bool:
    for cloze_deletion in cloze_deletions:
        if cloze_deletion.lower() not in curr_qtext.lower():
            return False
    return True

def reword_card(curr_card: Card, num_retries: int = config.settings.num_retries, reason: Optional[str] = None) -> str:

    # Extract relevant properties from the card.
    curr_qtext = reworded_qtext = curr_card.note().fields[0]
    curr_ord = curr_card.ord
    curr_card_type = curr_card.note().note_type()['name']
    
    # If we've run out of tries, then give up.
    if num_retries < 0:
        tooltip(f'Could not properly reword card {curr_card.id} using platform {config.settings.platform_index} (reason: {reason}). Please try again.') 
        return None

    try:
        if config.settings.platform_index == 0:
            reworded_qtext = reword_text_mistral(curr_qtext)
        elif config.settings.platform_index == 1:
            reworded_qtext = reword_text_gemini(curr_qtext)
        else:
            raise RuntimeError(f'Unknown platform index {config.settings.platform_index} for rewording card {curr_card.id}.')
    except RuntimeError as e:
        time.sleep(config.settings.retry_delay_seconds) # avoid rate limit ceiling
        return reword_card(curr_card, num_retries - 1, reason=str(e))
    
    # If the card is cloze-adjacent, then validate it. If valid, return the card.
    # If not cloze-adjacent, skip this validation process and just return the card.
    # BUG: This ONLY goes by name. There must be a better way to validate it.
    if 'cloze' in curr_card_type.lower() and not validate_cloze_card(reworded_qtext, get_cloze_matches(curr_qtext, curr_ord)):
        time.sleep(config.settings.retry_delay_seconds) # avoid rate limit ceiling
        return reword_card(curr_card, num_retries - 1, reason='Cloze validation failed')
    return reworded_qtext
        
def reword_text_mistral(curr_qtext: str) -> str: 
       
    # Try to reword the card using Mistral.
    try:
        chat_response = requests.post(url="https://api.mistral.ai/v1/chat/completions",
                                      headers={'Content-Type': 'application/json',
                                              'Accept': 'application/json',
                                              'Authorization': 'Bearer ' + config.settings.api_key},
                                      data=json.dumps({'model': config.settings.model,
                                                       'messages': [
                                                           {'role': 'system', 'content': config.settings.context},
                                                           {'role': 'user', 'content': curr_qtext}
                                                       ]}))
        if not (chat_response.status_code >= 200 and chat_response.status_code < 300):
            raise requests.exceptions.RequestException(chat_response.json().get('message', f'Unspecified error ({chat_response.status_code})'))
        return chat_response.json()['choices'][0]['message']['content']
    except Exception as e:
        # Throw an error.
        # # print('Error with Mistral. Is your API key working?')
        raise RuntimeError(f'Error loading \'{config.settings.model}\' for dynamic Anki cards: ' + str(e))
                          # 'You might need to check your settings to ensure correct model name, API keys, and usage limits. '
                          # 'If this continues, disable this add-on to stop these messages.')

def reword_text_gemini(curr_qtext: str) -> str: 
       
    # Try to reword the card using Gemini.
    try:
        chat_response = requests.post(
            url=f"https://generativelanguage.googleapis.com/v1beta/models/{config.settings.model}:generateContent",
            headers={
                'Content-Type': 'application/json',
                'X-goog-api-key': config.settings.api_key
            },
            data=json.dumps({
                'contents': [{
                    'parts': [{'text': curr_qtext}]
                }],
                'system_instruction': {
                    'parts': [{'text': config.settings.context}]
                },
                'generationConfig': {
                    'thinkingConfig': {
                        'thinkingBudget': 0 # prefer fast models, this will error with CoT/reasoning models
                    }
                }})
        )
        if not (chat_response.status_code >= 200 and chat_response.status_code < 300):
            raise requests.exceptions.RequestException(chat_response.json().get('message', f'Unspecified error ({chat_response.status_code})'))
        return chat_response.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        # Throw an error.
        # # print('Error with Gemini. Is your API key working?')
        raise RuntimeError(f'Error loading \'{config.settings.model}\' for dynamic Anki cards: ' + str(e))
                          # 'You might need to check your settings to ensure correct model name, API keys, and usage limits. '
                          # 'If this continues, disable this add-on to stop these messages.')

# Based on the template used in the note, generate a rewording and rerender the front cloze.
def inject_rewording_on_question(text: str, card: Card, kind: str) -> str:

    # Although this entire hook is called each time, we only want to modify the ephemeral card when we view
    # the question side. Then, we can simply view the answer side of the modified card while it's stored
    # in the mw.reviewer.card slot, even though we call the hook again.
    if kind == 'reviewQuestion':
        
        # Using the NOTE template, create an ephermeral card referring to the given note.
        # The consequence is that we can inject whatever wording we want, the wording will stay consistent,
        # and then the scheduling will be assigned to the stored card in memory.

        # Poll the cached card.
        # This will set the number of reps of any new card to 0.
        cce = poll_cached_card(card)
        # print('Last used render: %d of %d (at that time)' % (cce.last_used_render + 1, len(cce.renders)))

        # If the rep state hasn't changed since last time, then use the last render. Don't change.
        if cce.reps <= card.reps:

            # Otherwise, make a new request in the background and set the new render to use.
            if (not config.pause and len(cce.renders) < config.settings.max_renders and 
                card.note().note_type()['name'] not in config.settings.exclude_note_types):
                if config.debug: print(f'Creating new render for card {card.id}, current cache: ', str(cce))
                q.add_render_task(card=card)
            randint_fn = randint_try_norepeat if config.settings.max_renders > 1 else lambda a, b, c: 0
            cce.last_used_render = randint_fn(0, len(cce.renders) - 1, cce.last_used_render)

            # Update the cache reps.
            # BUG: Will freeze card updates if it is undone multiple times in one "undo chain."
            # Eventually this will be fixed, or the user can clear the cache on a card manually.
            # This issue should not occur in everyday usage though.
            update_cached_card(card, reps=cce.reps+1, last_used_render=cce.last_used_render)

        # Set the current render.
        curr_render = cce.renders[cce.last_used_render]
        card.set_render_output(curr_render)
        if config.debug:
            print(f'Using render {cce.last_used_render} (zero-indexed) for card {card.id}')
            print(f'CCE: {cce}')
            print(f'True (card) reps: {card.reps}')

        # print(cce)
        return card.question()

    # Again, we don't need to do any kind of modification to the ephemeral card that's in mw.reviewer.card 
    # as long as the card is visible.
    elif kind == 'reviewAnswer':
        return card.answer()
    
    # If there is any unexpected value of kind, just display what's there.
    return text

# Inject context menu option to add or remove current card type.

def inject_include_exclude_option(r: Reviewer, m: QMenu) -> Tuple[QAction, Callable]:
    # See L1026 in reviewer.py
    curr_note_type = r.card.note().note_type()['name']
    if curr_note_type not in config.settings.exclude_note_types:
        def exclude_curr_note_type():
            # Assigning explicitly so the setting change gets written to disk since we are calling __setattr__
            config.settings.exclude_note_types = config.settings.exclude_note_types + [curr_note_type]
            tooltip(f'Excluding note type \'{curr_note_type}\' from dynamic card generation.')
        phrase = 'Exclude current note type'
        fn = exclude_curr_note_type
    else:
        def include_curr_note_type():
            config.settings.exclude_note_types = [x for x in config.settings.exclude_note_types if x != curr_note_type]
            tooltip(f'Including note type \'{curr_note_type}\' in dynamic card generation.')
        phrase = 'Include current note type'
        fn = include_curr_note_type
    a = None
    if m:
        #m.addSeparator()
        a = m.addAction(phrase)
        a.setShortcut(config.settings.shortcut_include_exclude)
        qconnect(a.triggered, fn)
    return a, fn

def inject_clear_current_card_option(r: Reviewer, m: QMenu) -> None:
    a = m.addAction('Clear current card from cache')
    a.setShortcut(config.settings.shortcut_clear_current_card)
    if mw.reviewer:
        def fn(): clear_card_from_cache(mw.reviewer.card)
        qconnect(a.triggered, fn)

def inject_clear_all_cards_option(r: Reviewer, m: QMenu) -> None:
    a = m.addAction('Clear all cards from cache')
    a.setShortcut(config.settings.shortcut_clear_all_cards)
    def fn(): clear_cache()
    qconnect(a.triggered, fn)
    
def inject_pause_generation_option(r: Reviewer, m: QMenu) -> None:
    a = m.addAction('Pause dynamic card generation' if not config.pause else 'Resume dynamic card generation')
    a.setShortcut(config.settings.shortcut_pause)
    def fn(): config.pause = not config.pause
    qconnect(a.triggered, fn)

def insert_separator(r: Reviewer, m: QMenu) -> None:
    m.addSeparator()

# Start the dynamic database.
setup_dynamic_db()

# Start the asynchronous queue and have it start/stop appropriately.
# Using the card showing as a proxy for the start of a review session.
q = RewordingWorkerQueue()
gui_hooks.card_will_show.append(lambda *args: q.start())
gui_hooks.reviewer_will_end.append(lambda *args: q.stop())

# Add hook using the new method
# Also clear the reviewer once the review session is over
# Also clear cards from the cache when they are to be edited
gui_hooks.card_will_show.append(inject_rewording_on_question)
gui_hooks.editor_did_load_note.append(clear_cache_on_editor_load_note)
gui_hooks.reviewer_will_show_context_menu.append(insert_separator)
gui_hooks.reviewer_will_show_context_menu.append(inject_pause_generation_option)
gui_hooks.reviewer_will_show_context_menu.append(inject_include_exclude_option)
gui_hooks.reviewer_will_show_context_menu.append(inject_clear_current_card_option)
gui_hooks.reviewer_will_show_context_menu.append(inject_clear_all_cards_option)
if config.settings.clear_cache_on_reviewer_end:
    gui_hooks.reviewer_will_end.append(clear_cache)

# Attach the remove revision tool.
mw.installEventFilter(KeyPressCacheClearFilter(mw))

# Make the welcome announcement if warranted.
if config.settings.show_modal:
    dlg = WelcomeDialog(config.settings.show_modal)
    def set_show_modal():
        config.settings.show_modal = dlg.form.checkBox.isChecked()
    qconnect(dlg.rejected, set_show_modal)
    dlg.setModal(True)
    dlg.show()

# Have the dialog and the settings menu in separate classes.
sdlg = SettingsDialog(config.settings)
def update_config_settings():
    config.settings.shortcut_clear_current_card = sdlg.form.keySequenceEdit.keySequence().toString()
    config.settings.shortcut_clear_all_cards = sdlg.form.keySequenceEdit_2.keySequence().toString()
    config.settings.shortcut_include_exclude = sdlg.form.keySequenceEdit_3.keySequence().toString()
    config.settings.shortcut_pause = sdlg.form.keySequenceEdit_4.keySequence().toString()
    config.settings.api_key = sdlg.form.APIKeyLineEdit.text()
    config.settings.model = sdlg.form.modelLineEdit.text()
    config.settings.context = sdlg.form.textEdit.toPlainText()
    config.settings.clear_cache_on_reviewer_end = sdlg.form.checkBox.isChecked()
    config.settings.exclude_note_types = [sdlg.form.listWidget.item(i).text() for i in range(sdlg.form.listWidget.count())]
    config.settings.platform_index = sdlg.form.platformSelect.currentIndex()

    # Handle max render input
    try:
        val = int(sdlg.form.maxRendersLineEdit.text())
        assert val > 0
        config.settings.max_renders = val
    except ValueError or AssertionError:
        tooltip(f'Invalid new value \'{sdlg.form.maxRendersLineEdit.text()}\' for max renders; reverting to old value.')

    # Handle num retries input
    try:
        val = int(sdlg.form.retryCountLineEdit.text())
        assert val > 0
        config.settings.num_retries = val
    except ValueError or AssertionError:
        tooltip(f'Invalid new value \'{sdlg.form.retryCountLineEdit.text()}\' for retry count; reverting to old value.')

    # Handle retry delay input
    try:
        val = float(sdlg.form.retryDelayLineEdit.text())
        assert val >= 0
        config.settings.retry_delay_seconds = val
    except ValueError or AssertionError:
        tooltip(f'Invalid new value \'{sdlg.form.retryDelayLineEdit.text()}\' for retry delay; reverting to old value.')
    
    # Handle reviewer ending callback
    # As per internal gui_hooks code, no exception thrown if object to remove not found
    gui_hooks.reviewer_will_end.remove(clear_cache)
    if config.settings.clear_cache_on_reviewer_end:
        gui_hooks.reviewer_will_end.append(clear_cache)

sdlg.setModal(True)
sdlg.accepted.connect(update_config_settings)
config_option = QAction("Dynamic Cards", mw)
config_option.triggered.connect(sdlg.show)
mw.form.menuTools.addAction(config_option)