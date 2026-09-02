# The fallback strategy inside your current code:
captures = [m for m in legal_moves if boardis_capture(m)]
checks = [m for m in legal_moves if boardgives_check(m)]
if (captures or checks) and random.random() < 0.75:
    return random.choice(forcing_moves)
return random.choice(legal_moves)
