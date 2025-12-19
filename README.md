

Dork Parser is an ultra-fast, cyberpunk-styled GUI application designed
to automate advanced search engine dorking across multiple platforms.

Built for OSINT researchers, penetration testers, security analysts,
and power users who want speed, control, and a clean interface.


FEATURES
--------

[ Search ]
- Single dork search
- Mass dork search from file
- Line-range batch processing
- Real-time result streaming

[ Supported Search Engines ]
- DuckDuckGo
- Bing
- Google (limited / optional)
- Brave
- Yandex
- Yahoo
- Yahoo Japan

[ Performance ]
- Multithreaded execution
- Adjustable thread count
- Adjustable results per engine
- Optimized HTTP sessions
- Optional caching

[ Output ]
- Live result display
- Auto-save to file
- Manual export (TXT / JSON)
- Clipboard copy
- Result deduplication

[ UI / UX ]
- Cyberpunk dark theme
- DPI-aware widget scaling
- Responsive grid layout
- Tabbed interface
- Compact mode support


REQUIREMENTS
------------

- Python 3.9+
- Internet connection

Python dependencies (auto-installed if missing):
- customtkinter
- requests
- beautifulsoup4
- duckduckgo-search
- googlesearch-python
- lxml



USAGE
-----

[ Single Search ]
1. Enter a dork query
2. Select search engines
3. Adjust results per engine
4. Adjust thread count
5. Click START SEARCH

[ Mass Search ]
1. Load a .txt file containing dorks
2. Select start/end line range
3. Choose batch size
4. Start mass search


UI SCALING
----------

If the UI is too large for your screen, widget scaling is supported.

Example:

   ctk.set_widget_scaling(0.7)

Recommended values:
- 0.8  -> Comfortable
- 0.7  -> Compact (default)
- 0.6  -> Dense / advanced users


DISCLAIMER
----------

This tool is intended for:
- Educational use
- OSINT research
- Defensive security testing

You are responsible for how you use this software.
Do not violate laws, terms of service, or ethical boundaries.


ROADMAP
-------

- Scrollable panels
- UI zoom slider in Settings
- Engine profiles
- Proxy support
- Headless CLI mode
- CSV export
- Plugin-based engine system


LICENSE
-------

MIT License

Free to use, modify, and distribute.


CREDITS
-------

Built with:
- Python
- CustomTkinter
- Requests
- BeautifulSoup

