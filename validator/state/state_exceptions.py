class VerifierWarning(Exception):
    pass

class VerifierError(Exception):
    pass

class VarNotInState(Exception):
    """
    when asking something about a variable which is not in the abstract state at all
    """
    pass