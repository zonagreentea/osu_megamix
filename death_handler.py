def trigger_death(score):
    if score.health <= 0:
        print("Player died! Returning to Megamix title with animation...")
        # placeholder for fade / particles / zoom
        return True
    return False

