"""RetailIQ Inventory Recommendation Engine.

Generates inventory recommendations using:
- Demand forecasts
- Inventory risk
- ABC classification
- Stockout risk
- Reorder points
"""


# --------------------------------------
# Inventory Recommendation Engine
# --------------------------------------

def calculate_reorder_point(
    avg_daily_demand,
    safety_stock,
    lead_time_days=1
):
    """Calculate reorder point."""

    reorder_point = (
        avg_daily_demand * lead_time_days
        + safety_stock
    )

    return reorder_point


# --------------------------------------
# Inventory Decision Rules
# --------------------------------------

def generate_inventory_recommendation(
    abc_class,
    inventory_risk_score,
    stockout_risk_score,
    avg_daily_demand,
    reorder_point
):
    """Generate a business recommendation for a product."""

    if (
        abc_class == "A"
        and stockout_risk_score >= 0.70
    ):
        return "Urgent Reorder"

    elif (
        abc_class in ["A", "B"]
        and stockout_risk_score >= 0.50
    ):
        return "High Priority Reorder"

    elif (
        inventory_risk_score >= 1.20
        and avg_daily_demand > 10
    ):
        return "Increase Safety Stock"

    elif reorder_point > 0:
        return "Monitor Inventory"

    else:
        return "Low Priority"


# --------------------------------------
# Inventory Priority Score
# --------------------------------------

def calculate_decision_priority(
    inventory_risk_score,
    stockout_risk_score,
    demand_score
):
    """Calculate overall inventory decision priority."""

    priority_score = (
        inventory_risk_score * 0.40
        + stockout_risk_score * 0.30
        + demand_score * 0.30
    )

    return priority_score