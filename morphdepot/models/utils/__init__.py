
def cut_to_render( text, count=30 ):
    if len( text ) < count:
        return text
    return text[ : count-3] + '..'
