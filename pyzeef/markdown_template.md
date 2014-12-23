<%!
    # from django's slugify method
    # https://github.com/django/django/blob/master/django/utils/text.py#L439-L448
    import unicodedata
    import re
    def slugify(value):
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub('[^\w\s-]', '', value).strip().lower()
        return re.sub('[-\s]+', '-', value)

%>
${ page.title }
${ '=' * len(page.title) }

% for block in page.blocks:
% if block.type in ['link', 'feed']:
- [${ block.title }](#${block.title | slugify})
% endif
% endfor

% for block in page.blocks:
% if block.type in ['link', 'feed']:
${block.title}
${'-' * len(block.title)}
% if block.description:
**${block.description}**
% endif
% for link in block.links:
- [${link.title or 'Link {}'.format(loop.index)}](${link.url}) - ${link.description or link.url}
% endfor

% endif
% endfor
