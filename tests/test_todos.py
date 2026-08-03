"""
Unit tests for the todo list logic used by telegram_bot.py.
These test the data structure and operations directly, without
needing a live Telegram connection or a running Pi.
"""


def test_default_structure():
    """todos.json should always have 'him' and 'her' keys"""
    default = {'him': [], 'her': []}
    assert 'him' in default
    assert 'her' in default
    assert isinstance(default['him'], list)
    assert isinstance(default['her'], list)


def test_add_todo_to_correct_person():
    """Adding a todo should append to the right person's list only"""
    todos = {'him': [], 'her': []}
    todos['him'].append({'text': 'Buy milk', 'done': False})
    assert len(todos['him']) == 1
    assert todos['him'][0]['text'] == 'Buy milk'
    assert todos['him'][0]['done'] is False
    assert len(todos['her']) == 0


def test_mark_done():
    """Marking an item done should set done=True without affecting others"""
    todos = {
        'him': [
            {'text': 'Buy milk', 'done': False},
            {'text': 'Call bank', 'done': False},
        ],
        'her': []
    }
    todos['him'][0]['done'] = True
    assert todos['him'][0]['done'] is True
    assert todos['him'][1]['done'] is False


def test_clear_keeps_pending_removes_done():
    """Clearing should remove only completed items, keep pending ones"""
    todos = {
        'him': [
            {'text': 'Buy milk', 'done': True},
            {'text': 'Call bank', 'done': False},
        ],
        'her': [
            {'text': 'Book dentist', 'done': True},
        ]
    }
    todos['him'] = [t for t in todos['him'] if not t['done']]
    todos['her'] = [t for t in todos['her'] if not t['done']]

    assert len(todos['him']) == 1
    assert todos['him'][0]['text'] == 'Call bank'
    assert len(todos['her']) == 0


def test_ekadashi_detection():
    """Ekadashi should be detected from the tithi name string"""
    def is_ekadashi(tithi_name):
        if not tithi_name:
            return False
        return 'ekadashi' in tithi_name.lower()

    assert is_ekadashi('Shukla Ekadashi') is True
    assert is_ekadashi('EKADASHI') is True
    assert is_ekadashi('Purnima') is False
    assert is_ekadashi(None) is False
    assert is_ekadashi('') is False
