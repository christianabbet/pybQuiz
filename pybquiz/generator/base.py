
    
class QGenerator:

    
    def __init__(self) -> None:
        pass
    
    def get_codes(self):
        raise NotImplementedError
    
    def get_round(self, options: str):
        raise NotImplementedError

    @staticmethod
    def parse_options(l):
        return ", ".join(["{} ([red]{}[/red])".format(o[0], o[1]) for o in l])    

