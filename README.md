# Dynamic Cards

Hate when you memorize the wording of an Anki card rather than the card's
content? Introducing the **Dynamic Cards** plugin, a small plugin
that allows Anki to ping LLMs to slightly change the content of your cards
each time you review them.

This extension currently relies solely upon **Mistral AI** for generating and
serving new content; please note that your cards will be used as training
data if you use Mistral's free tier for your API key.

> [!WARNING]
> This has only been tested on a Windows 11 machine with PyQt6. It is possible
> that UI windows for this extension look subpar on other systems. If this
> plugin is indeed broken for other systems, please raise an issue on GitHub
> (see **Bugs and other issues** below).

## Download and installation

Head over to the [AnkiWeb page](https://ankiweb.net/shared/info/1902186394)
for installation instructions. You should be able to install the plugin
through the *Add-ons > Get Add-ons* menu in Anki itself.

## Usage

### First-time setup

There are some critical steps that need to be done before this extension may
be used.

1. **Create a Mistral API key:** Create a free account at
   [Mistral AI](https://console.mistral.ai/) to get started. Once created,
   navigate to the [API Keys](https://console.mistral.ai/api-keys/) page
   and follow instructions to create a **free** API key.
2. **Paste the API key into the extension.** Navigate to the *Tools > Dynamic
   Cards* window in Anki. Then, paste your API key into the *Mistral API key*
   field.
3. That's it! **The plugin should begin working immediately without further
   action; changes will initially be subtle. Enjoy your dynamic cards!**

> [!IMPORTANT]
> If you see a tooltip (pop-up) saying 'Unauthorized', there is a problem with
> your API key. Please try again or raise an issue on GitHub (see **Bugs and
  other issues**) if that doesn't work.

> [!WARNING]
> This extension might not work with certain types of cards, but should work
> with Basic, Cloze, and other note types that have the question text in their
> first field. This has been tested on AnKing and Miledown decks, for instance.
> Please raise an issue if you find a bug; see **Bugs and other issues** below.

### Normal operation

The workflow of the extension is quite simple. Each time you review a card, a
new "rewording" is generated in the background for next time (until the maximum
number of rewordings are reached). The extension therefore operates as follows:

* The first time you see a card, you will see the original wording.
* The second time you see a card, you will see a different rewording.
* Upon subsequent reviews of a card, one of any of the previous rewordings
  (or a new rewording) may be selected for display.

Do note that this extension uses an LLM and is subject to mistakes; cards might
not always look right. See **The Settings menu** subsection for what to do in
order to remove a poor rewording of a card from memory.

### The Settings menu

The Settings menu is the main control center of this plugin. It is accessible
via *Tools > Dynamic Cards.* The below bulletpoints describe all current
settings within the Settings menu.

* **Clear current card from cache:** If the LLM outputs a card whose wording
  doesn't quite make sense, press the corresponding hotkey to reset the
  wording of that specific card.
* **Clear all cards from cache:** Same as above, but do so for all cards.
* **Exclude/include current note type:** If you come across a card during
  your review whose note type is not amenable to dynamic generation (for
  example, Image Occlusion cards do not often have text to reword), hit this
  hotkey during your review to tell Dynamic Cards to not generate
  unnecessary rewordings for this note type.
* **Pause dynamic card generation:** Temporaeily stop the generation of
  dynamic cards by pressing this hotkey during review. Press the hotkey
  again to resume dynamic card generation.
* **Mistral API key:** The API key to allow access to Mistral's API.
* **Mistral model:** The Mistral model to use to generate card rewordings.
* **Max renders:** The maximum number of alternative "versions" of a card to
  hold. The default is `3` to balance storage use with a healthy variety of
  cards. Increasing this will increase the number of rewordings of cards
  available to you.
* **Context:** Instructions fed to the LLM to generate rewordings for cards.
  If the model is misbehaving, try rewording the context to suit your needs.
* **Clear cache on review end:** By default, any card rewordings that
  you create are cleared when you stop reviewing. Uncheck this option
  to allow rewordings to persist until you close Anki.
* **Excluded note types:** A list of all note types that have been excluded
  so far. Double-click any note type to remove it from the list (and thus
  resume dynamic generation again for it).

## Bugs and other issues

Found a bug? Please raise an issue so I can see it! Contributions are also
welcome.
