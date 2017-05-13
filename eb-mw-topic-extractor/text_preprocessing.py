import metawhale_topics_functions as mt

seed                  = mt.utf8seed
trashparts            = mt.trashparts
contraction_shortcuts = mt.contraction_shortcuts

# [in main] used for utf8 encoding fixing. I/O: string (raw text) / string (text with fixed utf8 encoding)
def fix(text):
    for s in seed:
        if s[0] in text:
            text = text.replace(s[0], s[1])
    return text

# [in main] trash parts removal, basically replaces all trash parts collected from different news sites like disclaimers for every news article. I/O: string (raw text) / string (text with removed trash parts)
def trashremove(text):
    for trash in trashparts:
        text = text.replace(trash, '')
    return text

# [in main] contraction expansion. eg. "don't" -> "do not". used for normalization of text so every article would be processed on the same format. I/O: string (raw text) / string (text with expanded contractions)
def contraction(text):
    tokens = text.split()
    months = [("Jan.", 31), ("Feb.", 29), ("Mar.", 31),  ("Apr.", 30), ("Jun.", 30), ("Jul.",31), ("Aug.", 31), ("Sep.", 30), ("Sept.", 30), ("Oct.", 31), ("Nov.",30), ("Dec.", 31)]
    newtext = ""
    index = 0
    for token in tokens:
        try:
            found = False
            for month in months:
                if month[0] == token:
                    next_token = int(tokens[index+1])
                    if next_token <= month[1] or is_year(next_token):
                        newtext = newtext + contraction_shortcuts[token]+" "
                        found = True
                    else:
                        raise Exception('Not a valid date')
            if not found:
                raise Exception('Not a valid date')
        except (KeyError, ValueError, Exception):
            newtext = newtext + token + " "
        index = index + 1
    return newtext

# [in main] formats text by removing all "/" and replacing them with a space. this was a fix on articles especially from Rappler where they put image captions plus their source.
#    eg: "Chrisee Dela Paz/Rappler MANILA"
# this fixed was created because the duplicate detection rules detects 'Paz/Rappler' as one word. thus, the acronym (PM) was tagged as this topic's duplicate because of 'Paz/Rappler MANILA'. I/O: string (raw text) / string (text without "/")
def format_text(text):
    tokens = text.split()
    newtext = ""
    for token in tokens:
        token = token.replace("/", " ")
        newtext = newtext + token.strip() + " "
    return newtext