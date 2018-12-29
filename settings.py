DOMAIN = ''  # YOUR DOMAIN WITH HTTPS
PORT = 5000  # SHOULD BE THE SAME AS IN YOUR SERVER.CONF FILE
TOKEN = ''

db_name = 'settings.db'
cc = ('US', 'FR', 'DE', 'IT', 'ES', 'NL', 'PL', 'PT', 'RU')  # country codes

meaning = {
    'EN': 'English',
    'FR': 'French',
    'DE': 'German',
    'IT': 'Italian',
    'ES': 'Spanish',
    'NL': 'Dutch',
    'PL': 'Polish',
    'PT': 'Portuguese',
    'RU': 'Russian'
}


def get_flag(country_code):
    offset = 127462 - ord('A')
    code = country_code.upper()
    return chr(ord(code[0]) + offset) + chr(ord(code[1]) + offset)


def clr(code):
    # to display proper emoji flag
    return code if code != 'US' else 'EN'
