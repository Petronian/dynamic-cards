# Dynamic Cards

Hate when you memorize the wording of an Anki card rather than the card's
content? Introducing the **Dynamic Cards** plugin, a small plugin
that allows Anki to ping LLMs to slightly change the content of your cards
each time you review them.

This extension currently relies solely upon **Mistral AI** for generating and
serving new content; please note that your cards will be used as training
data if you use Mistral's free tier for your API key.

## Download and installation

Head over to the [AnkiWeb page](https://ankiweb.net/shared/info/1902186394)
for installation instructions. You should be able to install the plugin
through the *Add-ons > Get Add-ons* menu in Anki itself.

## Usage

There are some critical steps that need to be done before this extension may
be used.

1. **Create a Mistral API key:** Create a free account at
   [Mistral AI](https://console.mistral.ai/) to get started. Once created,
   navigate to the [API Keys](https://console.mistral.ai/api-keys/) page
   and follow instructions to create a **free** API key. You should not need
   to pay for this, but be aware that free accounts submit training data to
   Mistral AI for use in training their models.
2. **Paste the API key into the extension.** Navigate to the *Tools > Add-ons*
   window in Anki. Then, select the **Dynamic Cards** extension and select
   **Config**. Paste your API key into the space corresponding to the `api_key`
   entry, keeping the quotes; your answer should overwrite the placeholder value
   of `"MISTRAL_API_KEY"`.
3. **Restart Anki.**
4. That's it! You can change the other parameters around if you'd like, but it
   is far from necessary. Enjoy your dynamic cards!

> [!IMPORTANT]
> If you see a tooltip (pop-up) saying 'Unauthorized', there is a problem with your API key. Please try again or raise an issue on Github (see **Bugs and other issues**) if that doesn't work.

> [!WARNING]
> This extension might not work with certain types of cards, but should work with Basic, Cloze, and other card types that have the question text in their first field. This has been tested on AnKing and Miledown decks, for instance. Please raise an issue if you find a bug; see **Bugs and other issues** as well as **Config file reference** below.

### Hotkeys

During use, it is possible that Mistral AI's LLM might output some bad results.
This can be especially drastic with cards featuring little text. You can use
the following buttons to fix this:

* `;`: Clear all AI rewordings of the current card.
* `'`: Clear all AI rewordings of all cards.
* `P`: Pause the generation of new dynamic cards (for example, if you're hitting API rate limits).
       Press `P` again to resume generation of dynamic cards.
* `E`: Opening the editor will act as if `;` were pressed out of necessity.

Closing the study session (i.e., returning to the 'Decks' screen) will also act as if `;` were pressed.

### Config file reference

A brief explanation of config file options.

| Key | Value |
| --- | ----- |
| `api_key` | Mistral AI API key. Instructions on obtaining one are above. |
| `context` | Instructions fed to the LLM to generate rewordings for cards. If the model is misbehaving, try rewording the context to suit your needs. |
| `max_renders` | The maximum number of alternative "versions" of a card to hold. The default is `3` to balance storage use with a healthy variety of cards. Increasing this will increase the number of rewordings of cards available to you. |
| `model` | The Mistral AI model to use. Default is `mistral-large-latest`, which should behave well. | 
| `exclude_note_types` | Note types to exclude from the Dynamic Cards plugin. For example, Image Occlusion cards have no text to change. |

## Bugs and other issues

Found a bug? Please raise an issue so I can see it! Contributions are also welcome.
