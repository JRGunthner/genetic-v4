from budget_calculator.src.model.Proposal import Proposal


class ProposalWithUserToken:
    def __init__(self):
        self.data = Proposal()
        self.token = ''

    def __getitem__(self, key):
        return getattr(self, key)
