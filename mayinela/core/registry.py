COMMANDS = {}

def command(name, help_text="", category="General", owner=False):
    def deco(func):
        func._mayinela = {
            "name": name,
            "help": help_text,
            "category": category,
            "owner": owner,
        }
        COMMANDS[name] = func
        return func
    return deco
