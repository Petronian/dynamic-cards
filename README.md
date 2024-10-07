# Dynamic Cards

Hate when you memorize the wording of an Anki card rather than the card's
content? Introducing the **Dynamic Cards** plugin, a small plugin
that allows Anki to ping LLMs to slightly change the content of your cards
each time you review them.

## Download and installation

To be done. Until I release this, I'll be showing people how to do this in
person.

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
3. That's it! You can change the other parameters around if you'd like, but it
   is far from necessary. Enjoy your dynamic cards!

### Hotkeys

During use, it is possible that Mistral AI's LLM might output some bad results.
This can be especially drastic with cards featuring little text. You can use
the following buttons to fix this:

* `;`: Clear all AI rewordings of the current card.
* `'`: Clear all AI rewordings of all cards.
* `E`: Opening the editor will act as if `;` was pressed out of necessity.

### Config file reference

A brief explanation of config file options.

| Key | Value |
| --- | ----- |
| `api_key` | Mistral AI API key. Instructions on obtaining one are above. |
| `context` | Instructions fed to the LLM to generate rewordings for cards. If the model is misbehaving, try rewording the context to suit your needs. |
| `max_renders` | The maximum number of alternative "versions" of a card to hold. The default is `3` to balance storage use with a healthy variety of cards. Increasing this will increase the number of rewordings of cards available to you. |
| `model` | The Mistral AI model to use. Default is `mistral-large-latest`, which should behave well. | 
| `exclude_note_types` | Note types to exclude from the Dynamic Cards plugin. For example, Image Occlusion cards have no text to change. |

## Known issues

These are just issues that I know about. For a more comprehensive list, check the **GitHub** page. (Insert link)

* **Review closing behavior:** If cards are being generated when the main
  reviewer window is closed, items might still be added to the cache and
  might persist. This shouldn't cause any major effects, so I've left it
  alone.

## Support

To be done.