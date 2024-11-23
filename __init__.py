from typing import Collection, Optional
from aqt import QEvent, QObject, Qt, mw, gui_hooks
from aqt.qt import QWidget, QAction, QDialog
from aqt.editor import Editor, EditorMode
from aqt.operations import QueryOp
from aqt.utils import tooltip as tooltip_aqt
from anki.cards import Card
from anki.notes import Note
from anki.template import TemplateRenderOutput
from random import randint
import requests
import json

# Optional parameters use the .get method with a default value
config = mw.addonManager.getConfig(__name__)
model = str(config['model'])
context = str(config['context'])
api_key = str(config['api_key'])
max_renders = config.get('max_renders', 3)
exclude_note_types = config.get('exclude_note_types', [])
debug = False

# Pass by reference shim
class Cache:
    data = {}
    pause = False # This only pauses NEW dynamic card generation

cache = Cache()

# Debug function declarations
def tooltip(*args, **kwargs):
    if debug: print(*args, **kwargs)
    tooltip_aqt(*args, **kwargs)

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
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            key = event.key()
            if key == Qt.Key.Key_Semicolon:
                curr_card = mw.reviewer.card
                if curr_card is not None and curr_card.id in cache.data.keys():
                    clear_card_from_cache(curr_card)
                else:
                    tooltip('No card to clear from dynamic cache.')
                # Fix bug: hitting any cache clear keys should trigger a redraw in case card isn't drawing right
                if mw.reviewer.card is not None:
                    mw.reviewer._redraw_current_card()
                return True
            elif key == Qt.Key.Key_Apostrophe:
                if cache.data:
                    clear_cache()
                else:
                    tooltip('No dynamic cache to clear.')
                # Fix bug: hitting any cache clear keys should trigger a redraw in case card isn't drawing right
                if mw.reviewer.card is not None:
                    mw.reviewer._redraw_current_card()
                return True
            elif key == Qt.Key.Key_P:
                cache.pause = not cache.pause
                if cache.pause:
                    tooltip('Dynamic card generation paused; will resume on Anki restart or unpause. '
                            'Existing dynamic cards will still show.')
                else:
                    tooltip('Dynamic card generation unpaused.')

        return super().eventFilter(obj, event)

# Create an options window.
# The options here will be:
# API Key (label)
# Context (paragraph)
# Max renders (number)
# Excluding note types (+/- table)
# Button keybinds for clearing card and whole cache (labels)
# Also: for above, will add those options to the reviewer context menu

# Have the dialog and the settings menu in separate classes.
class DynamicCardsDialog(QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('Dyamic Cards Settings')
        self.exec()

# Add to the test options stuff.
config_option = QAction("Dynamic Cards", mw)
config_option.triggered.connect(lambda: DynamicCardsDialog(parent=mw))
mw.form.menuTools.addAction(config_option)

def poll_cached_card(card: Card) -> CachedCardEntry:
    if card.id not in cache.data.keys():
        cache.data[card.id] = CachedCardEntry(id=card.id,
                                         renders=[card.render_output()],
                                         reps=card.reps,
                                         last_used_render=0)
    return cache.data[card.id]

def update_cached_card(card: Card,
                       reps: Optional[int] = None,
                       last_used_render: Optional[int] = None,
                       new_render: Optional[TemplateRenderOutput] = None) -> CachedCardEntry:
    
    # Set card intrinsic props.
    cce = poll_cached_card(card)

    if reps is not None:
        # cce id should match card id already.
        cce.reps = reps
        if debug: print(f'Updated reps for card {card.id}:', str(cce))
    if new_render is not None:
        cce.renders += [new_render]
        if debug: print(f'Added render for card {card.id}:', str(cce))
    if last_used_render is not None:
        assert last_used_render >= 0 and last_used_render < len(cce.renders)
        cce.last_used_render = last_used_render
        if debug: print(f'Updated last used render for card {card.id}:', str(cce))

    cache.data[card.id] = cce
    return cce

def create_new_cached_render(card: Card):
    # print('Making a new cached render for card ' + str(card.id))
    # print('API KEY: ' + api_key)
    ord = card.ord
    note = card.note()
    note = Note(col=note.col, id=note.id)
    if debug: print(f'Creating new render for card {card.id} using model \'{model}\'')
    note.fields[0] = reword_card_mistral(note.fields[0])
    if debug: print(f'Successfully created new render for card {card.id} using model \'{model}\'')
    return note.ephemeral_card(ord=ord, custom_note_type=note.note_type(), custom_template=card.template()).render_output()

def randint_try_norepeat(a, b, last_draw):
    v = randint(a, b)
    if v == last_draw and a != b:
        v = v - 1 if v > 0 else v + 1
    return v

# Clear cache, either entirely or for a specific card.
def clear_card_from_cache(card: Card):
    if card is not None and card.id in cache.data.keys():
        tooltip(f'Cleared card {card.id} from dynamic cache.')
        del cache.data[card.id]

def clear_note_from_cache(note: Note):
    if note is not None:
        for card in note.cards():
            clear_card_from_cache(card)
        tooltip(f'Cleared dynamic cache for cards associated with note {note.id}.')

def clear_cache():
    cache.data = {}
    tooltip('Cleared dynamic cache.')

# No need to redraw the card since that will be done anyway when the editor closes
# Only clear cache when editing new cards (only ADD_CARDS, EDIT_CURRENT, and BROWSER modes exist,
# see Editor class)
def clear_cache_on_editor_load_note(e: Editor):
    if e.editorMode == EditorMode.EDIT_CURRENT:
        clear_note_from_cache(e.note)
    # if mw.reviewer.card is not None:
    #     mw.reviewer._redraw_current_card()

def reword_card_mistral(curr_qtext):
    try:
        chat_response = requests.post(url="https://api.mistral.ai/v1/chat/completions",
                                      headers={'Content-Type': 'application/json',
                                              'Accept': 'application/json',
                                              'Authorization': 'Bearer ' + api_key},
                                      data=json.dumps({'model': model,
                                                       'messages': [
                                                           {'role': 'system', 'content': context},
                                                           {'role': 'user', 'content': curr_qtext}
                                                       ]}))
        
        if not (chat_response.status_code >= 200 and chat_response.status_code < 300):
            raise requests.exceptions.RequestException(chat_response.json().get('message', 'Unspecified error'))
        return chat_response.json()['choices'][0]['message']['content']
    except Exception as e:
        # Throw an error.
        # # print('Error with Mistral. Is your API key working?')
        raise RuntimeError(f'Error loading \'{model}\' for dynamic Anki cards: ' + str(e))
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
            if (not cache.pause and len(cce.renders) < max_renders and 
                card.note().note_type()['name'] not in exclude_note_types):

                if debug: print(f'Creating new render for card {card.id}, current cache: ', str(cce))
                op = QueryOp(parent=mw,
                             op=lambda col: create_new_cached_render(card=card),
                             success=lambda render_output: update_cached_card(card, new_render=render_output))
                op = op.failure(failure=lambda e: tooltip(str(e)))
                op.run_in_background()
            randint_fn = randint_try_norepeat if max_renders > 1 else lambda a, b, c: 0
            cce.last_used_render = randint_fn(0, len(cce.renders) - 1, cce.last_used_render)

            # Update the cache reps.
            # BUG: Will freeze card updates if it is undone multiple times in one "undo chain."
            # Eventually this will be fixed, or the user can clear the cache on a card manually.
            # This issue should not occur in everyday usage though.
            update_cached_card(card, reps=cce.reps+1)

        # Set the current render.
        curr_render = cce.renders[cce.last_used_render]
        card.set_render_output(curr_render)
        if debug: print(f'Using render {cce.last_used_render} for card {card.id}')

        # print(cce)
        return card.question()

    # Again, we don't need to do any kind of modification to the ephemeral card that's in mw.reviewer.card 
    # as long as the card is visible.
    elif kind == 'reviewAnswer':
        return card.answer()
    
    # If there is any unexpected value of kind, just display what's there.
    return text

# Add hook using the new method
# Also clear the reviewer once the review session is over
# Also clear cards from the cache when they are to be edited
gui_hooks.card_will_show.append(inject_rewording_on_question)
gui_hooks.reviewer_will_end.append(clear_cache)
gui_hooks.editor_did_load_note.append(clear_cache_on_editor_load_note)

# Attach the remove revision tool.
mw.installEventFilter(KeyPressCacheClearFilter(mw))