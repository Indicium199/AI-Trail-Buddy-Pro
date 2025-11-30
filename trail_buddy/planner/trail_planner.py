# trail_buddy/planner/trail_planner.py
import csv
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class PlannerAgent:
    """Filters trails from CSV based on user preferences."""

    def __init__(self, csv_file="trail_buddy/data/trails.csv"):
        self.trails = []
        try:
            with open(csv_file, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row["Distance_km"] = float(row.get("Distance_km", 0))
                    row["Fell_Height_m"] = float(row.get("Fell_Height_m", 0))
                    row.setdefault("Route", "N/A")
                    row.setdefault("Tags", "")
                    row.setdefault("Region", "")
                    self.trails.append(row)
            logger.info("Loaded %d trails from %s", len(self.trails), csv_file)
        except Exception as e:
            logger.error("Failed to load trails: %s", e)

    def filter_trails(self, difficulty=None, max_distance=None, route_type=None, soft_distance=False):
        filtered = self.trails

        if difficulty:
            filtered = [t for t in filtered if t.get("Difficulty", "").lower() == difficulty.lower()]

        if route_type:
            filtered = [t for t in filtered if t.get("Route", "").lower() == route_type.lower()]

        if max_distance is not None:
            if not soft_distance:
                filtered = [t for t in filtered if t.get("Distance_km", 0) <= max_distance]
            else:
                for t in filtered:
                    t["_distance_diff"] = t.get("Distance_km", 0) - max_distance

        return filtered[:10]
