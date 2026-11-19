"""Format tool-returned financial facts without model-generated arithmetic."""


def comparison_rows(source):
    rows = []
    prior_label = "Six months ended " + source["periods"]["prior"][1]
    current_label = "Six months ended " + source["periods"]["current"][1]
    for label, metric in source["metrics"].items():
        unit = metric["unit"]
        def formatted(value):
            if unit == "USD":
                return "$%.2fB" % (value / 1e9)
            if unit == "shares":
                return "%.3fB shares" % (value / 1e9)
            return "$%.2f / share" % value
        rows.append({"Measure": label, prior_label: formatted(metric["prior"]),
                     current_label: formatted(metric["current"]),
                     "Change": "%+.1f%%" % metric["growth_percent"]})
    margins = source["operating_margin_percent"]
    rows.append({"Measure": "Operating margin", prior_label: "%.1f%%" % margins["prior"],
                 current_label: "%.1f%%" % margins["current"],
                 "Change": "%+.1f percentage points" % source["operating_margin_change_percentage_points"]})
    return rows
