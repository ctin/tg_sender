# tg_sender

`tg_sender` is a Python library that transforms protobuf-based message packages into Telegram messages using the [aiogram](https://github.com/aiogram/aiogram) framework. It is designed to help you send various types of content (text, images, files, media groups, etc.) to Telegram channels, groups, or users, with support for advanced features like Markdown formatting, inline keyboards, message pinning, and more.

## Features

- **Protobuf Integration**: Accepts message data in protobuf format for structured, type-safe messaging.
- **Telegram Messaging**: Sends text, images, files, and media groups to Telegram via the Bot API.
- **Markdown Support**: Handles Markdown formatting and escaping for safe, rich-text messages.
- **Inline Keyboards**: Supports sending messages with inline buttons and custom markup.
- **Message Management**: Pin, unpin, forward, and delete messages programmatically.
- **Logging**: Obfuscates sensitive data in logs for security.

## Installation

Install via [Poetry](https://python-poetry.org/) (recommended):

```bash
poetry add tg_sender
```

Or clone the repository and install dependencies:

```bash
git clone https://github.com/fun-limited/tg_sender.git
cd tg_sender
poetry install
```

### 5. Advanced Features

- **Inline Keyboards**: Use `send_markup` to send messages with inline buttons.
- **Pin/Unpin/Delete**: Use `Pin`, `Unpin`, and `Delete` methods for message management.
- **Forwarding**: Use `Forward` to forward messages between chats.

## API Reference

### SenderBot Methods

- `SendText(bmd)` — Send a text message.
- `send_markup(bmd)` — Send a message with inline keyboard.
- `SendPhoto(bmd, path)` — Send a photo with optional caption.
- `SendMultipleImages(bmd, paths)` — Send multiple images as a media group.
- `SendFile(bmd, path)` — Send a file/document.
- `Forward(chat_id, from_chat_id, message_id, thread_id)` — Forward a message.
- `Pin(chat_id, message_id, disable_notification)` — Pin a message.
- `Unpin(chat_id, message_id)` — Unpin a message.
- `Delete(chat_id, message_id)` — Delete a message.

### Message Data

The `BaseMessageData` class contains fields like:
- `channel`: Target chat/channel username or ID
- `text`: Message text
- `parse_mode`: Markdown/HTML formatting
- `thread_id`: (Optional) Topic/thread ID
- `reply_to`: (Optional) Message ID to reply to
- `disable_web_page_preview`: (Optional) Disable link previews
- `buttons`: (Optional) List of inline keyboard buttons

## Contributing

Contributions are welcome! Please open issues or submit pull requests for bug fixes, features, or documentation improvements.

## License

This project is licensed under the MIT License.

## Acknowledgements

- [aiogram](https://github.com/aiogram/aiogram) — Telegram Bot API framework for Python
- [protobuf](https://developers.google.com/protocol-buffers) — Google's data interchange format

---

For questions or support, please open an issue or contact the maintainer.
