# Task: reconstruction parameters

From the source pack, produce a JSON object only (no markdown fence) with this shape:

{
  "ovens": [
    {
      "id": "arc-lite" | "tread" | "dome-xl",
      "published": { external_mm: [W,D,H], internal_mm: [W,D,H], mouth_mm: [W,H], mass_kg, stone_mm, power_kW, mass_flow_g_h, model },
      "conflicts": [ { "item", "values", "use" } ],
      "inferred_envelope": {
        "side_wall_mm": "number and the subtraction",
        "front_plus_rear_mm": "number",
        "vertical_stack_mm": "external H minus internal H, and what it cannot mean for Dome XL",
        "mouth_over_apex": "ratio",
        "mouth_over_width": "ratio",
        "hypothesis_wall_stack": [
          { "layer", "thickness_mm_low", "thickness_mm_high", "why" }
        ]
      },
      "geometry_for_cad": {
        "body_height_mm": "the solid body, excluding a loose flue",
        "flue": null or { "rises_to_total_height_mm", "clear_of_carton_mm", "rain_gap_mm" },
        "vault": "how to sweep the inner void so apex is internal H and the mouth is shorter",
        "burner_side": "left, as the Arc Lite manual describes, and say that left/right for Dome wood is the manual's right for the wood bed",
        "stone_plan_mm": [W, D],
        "confidence": "high|medium|low per field that is not a direct copy"
      }
    }
  ],
  "shared_mechanism": "one paragraph on the lateral roll",
  "do_not_treat_as_measured": ["list"]
}

Compute every ratio yourself. For Dome XL, propose a body height that fits in a 613 mm carton and a flue that brings the installed height to 997 mm. State that body height as Inferred. The 219 mm callout stays a named unknown with two hypotheses and which one you reject.
