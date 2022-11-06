# @rebootstr

import time
from yattag import Doc


def save_html(html_name, messages):
    doc, tag, text = Doc().tagtext()
    doc.asis('<!DOCTYPE html>')
    with tag('html'):
        with tag('body', style="background-color: #edeef0;"):
            for message in messages:
                with tag('div', style="margin: 5px;"):
                    with tag('span', style="margin-right: 5px;font-weight: bold;"):
                        text(message['name'])
                    with tag('span', style="color: gray;"):
                        text(time.ctime(message['date']))
                    with tag('p', style="margin: 6px;margin-left: 0px;margin-bottom: 11px;"):
                        text(message["text"])
                    if message["audio_message"] is not None:
                        with tag('a',
                                 href=message["audio_message"],
                                 style="margin: 6px;margin-left: 0px;margin-bottom: 11px;"):
                            text("Голосовое сообщение")
                    if len(message["photos"]) != 0:
                        with tag('div', style="height: 150px;"):
                            for photo in message["photos"]:
                                doc.stag('img', style="height: 100%;", src=photo)

    with open(html_name, "w") as f:
        f.write(doc.getvalue())


if __name__ == '__main__':
    photos = [
        "",
    ]
    messages = [
        {
            "name": "NAME",
            "date": time.time(),
            "text": "all",
            "photos": photos,
            "audio_message": None  # or link
        }
    ]
    save_html("test/1.html", messages)
