from typing import Collection, Optional
from aqt import QEvent, QObject, Qt, mw, gui_hooks
from aqt.editor import Editor
from aqt.operations import QueryOp
from aqt.utils import tooltip
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

# Pass by reference shim
class Cache:
    data = {}

cache = Cache()

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

# Keypress event that will be used for removing faulty revisions of a card.
class KeyPressCacheClearFilter(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            key = event.key()
            if key == Qt.Key.Key_Semicolon:
                curr_card = mw.reviewer.card
                if curr_card is not None and curr_card.id in cache.data.keys():
                    clear_card_from_cache(curr_card)
                    mw.reviewer._redraw_current_card()
                else:
                    tooltip('No card to clear from dynamic cache.')
                return True
            elif key == Qt.Key.Key_Apostrophe:
                if cache.data:
                    clear_cache()
                    if mw.reviewer.card is not None:
                        mw.reviewer._redraw_current_card()
                else:
                    tooltip('No dynamic cache to clear.')
                return True
        return super().eventFilter(obj, event)

def poll_cached_card(card: Card) -> CachedCardEntry:
    if card.id not in cache.data.keys():
        cache.data[card.id] = CachedCardEntry(id=card.id,
                                         renders=[card.render_output()],
                                         reps=card.reps,
                                         last_used_render=0)
    return cache.data[card.id]

def update_cached_card(card: Card,
                       last_used_render: Optional[int] = None,
                       new_render: Optional[TemplateRenderOutput] = None) -> CachedCardEntry:
    cce = poll_cached_card(card)
    
    # Set card intrinsic props.
    # cce id should match card id already.
    cce.reps = card.reps

    # Set card extrinsic props.
    if new_render is not None:
        cce.renders += [new_render]
    if last_used_render is not None:
        assert last_used_render >= 0 and last_used_render < len(cce.renders)
        cce.last_used_render = last_used_render

    # print('Updating card ID ' + str(card.id) + ' to have ' + str(len(cce.renders)) + ' renders, last used: ' + str(cce.last_used_render))
    cache.data[card.id] = cce
    return cce

def create_new_cached_render(card: Card):
    # print('Making a new cached render for card ' + str(card.id))
    # print('API KEY: ' + api_key)
    ord = card.ord
    note = card.note()
    note = Note(col=note.col, id=note.id)
    note.fields[0] = reword_card_mistral(note.fields[0])
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
def clear_cache_on_editor_load_note(e: Editor):
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
        cce = poll_cached_card(card)
        # print('Last used render: %d of %d (at that time)' % (cce.last_used_render + 1, len(cce.renders)))

        # If the rep state hasn't changed since last time, then use the last render. Don't change.
        # BUG: Will freeze card updates if it is undone multiple times in one "undo chain."
        # Eventually this will be fixed, or the user can clear the cache on a card manually.
        # This issue should not occur in everyday usage though.
        if cce.reps >= card.reps:
            # Use the last render.
            # print('Currently using render: %d of %d (at this time; unchanged)' % (cce.last_used_render + 1, len(cce.renders)))
            curr_render = cce.renders[cce.last_used_render]
        else:
            # Otherwise, make a new request in the background and set the new render to use.
            if len(cce.renders) < max_renders and card.note().note_type()['name'] not in exclude_note_types:
                op = QueryOp(parent=mw,
                             op=lambda col: create_new_cached_render(card=card),
                             success=lambda render_output: update_cached_card(card, new_render=render_output))
                op.failure(failure=lambda e: tooltip(str(e)))
                op.run_in_background()
            randint_fn = randint_try_norepeat if max_renders > 1 else lambda a, b, c: 0
            cce.last_used_render = randint_fn(0, len(cce.renders) - 1, cce.last_used_render)
            # print('Currently using render: %d of %d (at this time)' % (cce.last_used_render + 1, len(cce.renders)))

        # Set the current render.
        curr_render = cce.renders[cce.last_used_render]
        card.set_render_output(curr_render)
        
        # Update the cache; at this time, just updating the number of reps.
        update_cached_card(card)

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