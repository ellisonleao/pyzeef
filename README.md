pyzeef
======

[![Code Health](https://landscape.io/github/ellisonleao/pyzeef/master/landscape.svg?style=flat)](https://landscape.io/github/ellisonleao/pyzeef/master)
[![Build Status](https://travis-ci.org/ellisonleao/pyzeef.svg?branch=master)](https://travis-ci.org/ellisonleao/pyzeef)
[![PyPI](https://img.shields.io/pypi/dm/pyzeef.svg)](https://pypi.python.org/pypi/pyzeef/)

Welcome to the Python Zeef API lib.

# Table of contents

- [Installing](#installing)
- [Basic Usage](#basic-usage)
- [The Zeef Class](#the-zeef-class)
- [The Page Class](#the-page-class)
- [The Block Class](#the-block-class)
- [The Link Class](#the-link-class)


## Installing

Using pip:

```
pip install pyzeef
```

or cloning installing the current build
```
	git clone https://github.com/ellisonleao/pyzeef.git
	cd pyzeef
	python setup.py develop
```
I strong recommend using a virtualenv before installing any of the methods above.

## [Basic Usage](#basic-usage)

Before get things started, you will need a ZEEF Token in order to use the lib.
To generate a new token, please [go here](https://zeef.com/dashboard/user/profile/tokens)

After generating your token:

from pyzeef import Zeef

```python
	z = Zeef('YOUR-TOKEN')
	print z.pages
	# Output
	[
		<Page ID>,
		...
	]
```

### [The ZEEF Class](#zeef-class)

## `Zeef(token, persist_pages=True, get_scratchpad=True)`

When instantiating a new Zeef class all of your pages and the scratchpad will also be persisted by default. If you don't want to fetch the pages and/or the scratchpad you can pass `persist_pages` and `get_scratchpad` kwargs when creating the new class

#### Methods

#### `authorize(token=None, persist_pages=True)`

That method will be called on the object creation if `persist_pages=True`. It will authorize and persist your token through all the API requests and also fetch/persist your ZEEF pages. You can also pass a new
token when instantiating the class. That token will be persisted to be used on the future requests.

#### `get_page(page_id=int, alias=string, username=string)`

You can fetch a page by passing the `page_id` or passing both `alias` and `username`
This wil return a [Page](#page) class.


### `get_block(block_id)`

This will return a [Block](#block) class object, if any block is found with the `block_id` provided.

### `get_link(link_id)`

This will return a [Link](#link) class objects, if any link is found with the `link_id` provided.

### `create_page(name, language='en', type=['SUBJECT', 'COMPANY', 'PERSONAL'])`

Quick method to create a new page, given the name, language and the type. This will return a Page instance with the new page information.

### Main properties

- `page` - This will return the fetched pages list, as [Page](#page) objects.

### [The Page Class](#page)

When fetching the pages, there is a helper class which can help you make Zeef Page CRUD operations.

#### Methods

#### `update(type=['SUBJECT', 'COMPANY'], description='your description')`

Updates the current page. Both fields are optional.

### `to_markdown()`

This will output your ZEEF page in a markdown format.

### Main Properties

- `blocks` - A page can contain multiple blocks. When retrieving a page, the blocks property will return a list of [Block](#block) objects to help on block API operations.
- `title` - Page's title.

### [The Block Class](#block-class)

### Methods

### `update(data)`

Updates the current block with given data dict. `data` keys can be:

- `title` - String
- `promoted` - Boolean
- `publicly_visible` - Boolean

For `link` type blocks, we can add:

- `description` - String

For `feed` type `blocks`, we can add:

- `feed_url` - URL String
- `max_links` - Integer
- `refresh_minutes` - Integer


### `delete()`

Deletes the block from the Page

### Main Properties

- `links` - A list of [Link](#link) objects to help links API operations
- `title` - Block's title
- `type` - Block's type

### [The Link Class](#link-class)

### Methods

### `update(link='http://mylink.com', description='text', title='title')`

Updates the current link with the provided kwargs.

### `delete()`

Deletes the link

### Main Properties

- `title` - Link's title
- `url` - Link's URL
