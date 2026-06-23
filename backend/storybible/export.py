import io
import re
from ebooklib import epub


def content_to_html(content):
    if not content:
        return '<p></p>'
    if content.strip().startswith('<'):
        return content
    content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
    content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', content)
    paragraphs = content.split('\n\n')
    return ''.join(f'<p>{p.strip()}</p>' for p in paragraphs if p.strip())


def generate_epub(project, user, scenes):
    book = epub.EpubBook()
    book.set_identifier(f'wda-{project.pk}-{project.created_at.isoformat()}')
    book.set_title(project.title)
    book.set_language('en')
    book.add_author(user.username)

    style = (
        'body { font-family: Georgia, "Times New Roman", serif; '
        'line-height: 1.6; margin: 1em 2em; }\n'
        'h1 { font-size: 1.6em; margin-top: 1.5em; }\n'
        'h2 { font-size: 1.3em; margin-top: 1.2em; }\n'
        'p { margin: 0.5em 0; text-indent: 1.5em; }\n'
        'blockquote { font-style: italic; margin: 1em 2em; }\n'
    )
    css = epub.EpubItem(
        uid='style',
        file_name='style/default.css',
        media_type='text/css',
        content=style,
    )
    book.add_item(css)

    chapters = []
    for i, scene in enumerate(scenes):
        title = scene.title or f'Chapter {scene.order + 1}'
        html_body = content_to_html(scene.content or '')
        chapter = epub.EpubHtml(
            title=title,
            file_name=f'chap_{i}.xhtml',
            lang='en',
        )
        chapter.content = (
            f'<html><head><title>{title}</title></head>'
            f'<body><h1>{title}</h1>{html_body}</body></html>'
        )
        chapter.add_item(css)
        book.add_item(chapter)
        chapters.append(chapter)

    book.toc = chapters
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ['nav'] + chapters

    buf = io.BytesIO()
    epub.write_epub(buf, book)
    buf.seek(0)
    return buf
