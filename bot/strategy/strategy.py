from bot import config

def decide_action(prob_up):
    if prob_up >= config.LONG_THRESHOLD:
        return "LONG"
    if prob_up <= config.FLAT_THRESHOLD:
        return "CLOSE"
    return "HOLD"
