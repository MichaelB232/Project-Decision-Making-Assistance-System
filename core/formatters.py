# Function to change the color of gainers and losers
def color_change(val):
    if val > 0:
        return "color: #00f5c4; font-weight: 600;"
    elif val < 0:
        return "color: #ff4b6e; font-weight: 600;"
    return ""


# Format for Gainers and Losers
def format_change(val):
    if val > 0:
        return f"▲ {val:.2f}%"
    elif val < 0:
        return f"▼ {abs(val):.2f}%"
    return f"{val:.2f}%"
