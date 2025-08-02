class DecisionNode:
    def __init__(self, prompt, responses=None, is_terminal=False):
        self.prompt = prompt
        self.responses = responses or {}
        self.is_terminal = is_terminal

    def get_next(self, user_input):
        user_input = user_input.strip().lower()
        for key, next_node in self.responses.items():
            if key in user_input:
                return next_node
        return None

def build_tree():
    intervention = DecisionNode("Apply airway intervention now. Done.", is_terminal=True)
    monitor = DecisionNode("Continue to monitor airway. No action required.", is_terminal=True)

    verbal = DecisionNode(
        "Is the patient able to speak or respond verbally?",
        responses={"yes": monitor, "no": intervention}
    )

    root = DecisionNode(
        "Is the patient conscious?",
        responses={"yes": verbal, "no": intervention}
    )

    return root
