import json
import logging

logger = logging.getLogger(__name__)

class TrailReasoner:
    """Uses LLM to select best trail and provide reasoning."""

    def __init__(self, llm=None):
        self.llm = llm

    def build_explanation(self, inputs, filtered_by, selected_trail_name=None):
        explanation = {
            "user_inputs": inputs,
            "filters_applied": filtered_by,
            "llm_reasoning": None,
            "selected_trail_name": selected_trail_name
        }
        if self.llm:
            try:
                prompt = (
                    f"You are an assistant generating reasoning for trail selection.\n"
                    f"User Inputs: {inputs}\nFilters: {filtered_by}\nSelected Trail: {selected_trail_name}\n"
                    "Provide structured JSON explanation."
                )
                response = self.llm.ask(prompt)
                explanation["llm_reasoning"] = response
            except Exception as e:
                logger.error("TrailReasoner LLM error: %s", e)
        return explanation

    def select_trail_with_reason(self, trails, explanation_data):
        if not trails:
            return None, None
        for t in trails:
            t["_distance_diff"] = t.get("_distance_diff", 0.0)
            t["_scenery_count"] = len(t.get("Tags","").split(","))
        best_trail = trails[0]  # Fallback
        reason_text = None
        if self.llm:
            try:
                prompt = "Select the best trail based on distance (soft), scenery (soft), difficulty (hard)."
                response = self.llm.ask(prompt)
                parsed = json.loads(response)
                best_name = parsed.get("best_trail", best_trail.get("Trail"))
                best_trail = next((t for t in trails if t.get("Trail") == best_name), best_trail)
                reason_text = parsed.get("reasoning")
            except Exception:
                pass
        reason = self.build_explanation(
            inputs=explanation_data.get("inputs", {}),
            filtered_by=explanation_data.get("filters", {}),
            selected_trail_name=best_trail.get("Trail")
        )
        if reason_text:
            reason["llm_reasoning"] = reason_text
        return best_trail, reason
