# Define a mapping of tags to list IDs to create tasks based on tags
TAG_TO_LIST_ID_MAP = {
    'prabhu': '901606178743',
    'deepak': '901606178750',
    'nandhu': '901606248381',
    'abhijith': '901606186292',
    'vaibhav': '901606248361',
    'bhuvanesh': '901606586758',
    'beelittle': '901606177816',
    'prathiksham': '901606248338',
    'zing': '901606248326',
    'adoreaboo': '901606248353',
    'all': '901606248206',
    # Add more mappings as needed
}

# Define a direct mapping of list IDs to their corresponding names
LIST_ID_TO_NAME_MAP = {
    '901606178743': 'prabhu',
    '901606178750': 'deepak',
    '901606248381': 'nandhu',
    '901606186292': 'abhijith',
    '901606248361': 'vaibhav',
    '901606586758': 'bhuvanesh',
}

# Define a mapping of list IDs to conditional tags for creating linked tasks in relevant list id only based on tags
LIST_ID_TO_TAGS_MAP = {
    #socialmedia
    '901605050377': ['prabhu', 'deepak', 'abhijith', 'nandhu', 'vaibhav', 'bhuvanesh'], #beelittle
    '901606186307': ['prabhu', 'deepak', 'abhijith', 'nandhu', 'vaibhav', 'bhuvanesh'], #zing
    '901606186317': ['prabhu', 'deepak', 'abhijith', 'nandhu', 'vaibhav', 'bhuvanesh'], #prathiksham
    '901606186318': ['prabhu', 'deepak', 'abhijith', 'nandhu', 'vaibhav', 'bhuvanesh'], #adoreaboo
    #ads
    '901606186180': ['prabhu', 'deepak', 'abhijith', 'nandhu', 'vaibhav', 'bhuvanesh'], #beelittle 
    '901606186297': ['prabhu', 'deepak', 'abhijith', 'nandhu', 'vaibhav', 'bhuvanesh'], #zing
    '901606186300': ['prabhu', 'deepak', 'abhijith', 'nandhu', 'vaibhav', 'bhuvanesh'], #prathiksham
    '901606186304': ['prabhu', 'deepak', 'abhijith', 'nandhu', 'vaibhav', 'bhuvanesh'], #adoreaboo
    #video edit
    '901606178743': ['beelittle', 'prathiksham', 'zing', 'adoreaboo'], #prabhu
    '901606178750': ['beelittle', 'prathiksham', 'zing', 'adoreaboo'], #deepak
    '901606248381': ['beelittle', 'prathiksham', 'zing', 'adoreaboo'], #nandhu
    #graphic design
    '901606186292': ['beelittle', 'prathiksham', 'zing', 'adoreaboo'], #abhijtih
    '901606248361': ['beelittle', 'prathiksham', 'zing', 'adoreaboo'], #vaibhav
    '901606586758': ['beelittle', 'prathiksham', 'zing', 'adoreaboo'], #bhuvanesh
    #review
    '901606177816': ['all'], #beelittle
    '901606248338': ['all'], #prathiksham
    '901606248326': ['all'], #zing
    '901606248353': ['all'], #adoreaboo
}

# Define a mapping of review folder list IDs
REVIEW_FOLDER_LIST_IDS = {
    '901606177816',  # Beelittle
    '901606248326',  # Zing
    '901606248338',  # Prathiksham
    '901606248353',  # Adoreaboo
}