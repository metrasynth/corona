===============================
``catalog`` and ``render`` apps
===============================

Viewing a details page about a new SunVox audio file
----------------------------------------------------

1.  Add ``sunvox.audio/`` to the beginning of your URL:
    ``http://sunvox.audio/https://some.site/file.sunvox``

    a.  In production, it'll redirect you to the ``https://...`` equivalent.

2.  A *catalog.Location* is created, after failing to find any by that *url*.

3.  As it's new, the *location.fetches* will be empty.

    Create a new *catalog.Fetch*, setting *location*.

    *fetch.state* will start as *new*.

4.  Call *fetch.start()*.

    A new rq job on the *fetch* queue will be created: *perform_fetch(fetch)*

    *fetch.state* will become *fetching* and return immediately.

5.  Render a page with information about the location, and that it's fetching.

    As long as the state is not *done* or *rejected*, the page will refresh every 5 seconds.

6.  When the file is downloaded, *fetch.state* becomes *fetch.processing*.

    If any download times out after 1 minute, *fetch.reject('download timeout')*.

7.  The hash of the file is computed, and checked against *Content*.

    If it exists, remove the downloaded content.

    a.  If it is valid, set *fetch.content* and call *fetch.finish()*.

    b.  If it exists, but is not valid, set *fetch.content* and call *fetch.reject('unreadable file')*.

8.  The file is processed by trying to read it using Radiant Voices.

    If any processing times out after 2 minutes, *fetch.reject('processing timeout')*.

    If any errors are raised, *fetch.reject('unreadable file')*.

9.  Move downloaded file into content store.

    Create a new *Content* instance.

    *fetch.finish()*

10. Based on whether *content.file_type* is *project* or *module*, page will redirect to
    ``//sunvox.audio/project/<base36-hash>/`` or ``//sunvox.audio/module/<base36-hash>/``.

11. The page will display the following information:

    -   Whether it's a project or module.

    -   File size.

    -   Locations where it's been seen online.
