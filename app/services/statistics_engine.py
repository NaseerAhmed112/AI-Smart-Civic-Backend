import math
from collections import Counter
from typing import List, Dict, Any

class StatisticsEngine:
    """Pure Python statistics engine — no pandas/numpy (Vercel-compatible)."""

    @staticmethod
    def calculate_descriptive_stats(numbers: List[float]) -> Dict[str, Any]:
        if not numbers:
            return {"count": 0, "mean": 0.0, "median": 0.0, "mode": 0.0,
                    "min": 0.0, "max": 0.0, "range": 0.0, "variance": 0.0, "std_dev": 0.0}
        n = len(numbers)
        mean_val = sum(numbers) / n
        sorted_nums = sorted(numbers)
        mid = n // 2
        median_val = sorted_nums[mid] if n % 2 else (sorted_nums[mid - 1] + sorted_nums[mid]) / 2
        mode_val = Counter(numbers).most_common(1)[0][0]
        min_val, max_val = sorted_nums[0], sorted_nums[-1]
        variance_val = sum((x - mean_val) ** 2 for x in numbers) / (n - 1) if n > 1 else 0.0
        return {
            "count": n, "mean": round(mean_val, 2), "median": round(median_val, 2),
            "mode": round(mode_val, 2), "min": round(min_val, 2), "max": round(max_val, 2),
            "range": round(max_val - min_val, 2), "variance": round(variance_val, 2),
            "std_dev": round(math.sqrt(variance_val), 2),
        }

    @staticmethod
    def calculate_iqr_fences(numbers: List[float]) -> Dict[str, Any]:
        if not numbers or len(numbers) < 2:
            return {"q1": 0.0, "q2": 0.0, "q3": 0.0, "iqr": 0.0,
                    "lower_fence": 0.0, "upper_fence": 0.0, "outliers_count": 0}
        sorted_nums = sorted(numbers)
        def percentile(data, p):
            idx = (p / 100) * (len(data) - 1)
            lo, hi = int(idx), min(int(idx) + 1, len(data) - 1)
            return data[lo] + (data[hi] - data[lo]) * (idx - lo)
        q1, q2, q3 = percentile(sorted_nums, 25), percentile(sorted_nums, 50), percentile(sorted_nums, 75)
        iqr = q3 - q1
        lower_fence, upper_fence = max(0.0, q1 - 1.5 * iqr), q3 + 1.5 * iqr
        outliers = [x for x in sorted_nums if x < lower_fence or x > upper_fence]
        return {"q1": round(q1, 2), "q2": round(q2, 2), "q3": round(q3, 2), "iqr": round(iqr, 2),
                "lower_fence": round(lower_fence, 2), "upper_fence": round(upper_fence, 2), "outliers_count": len(outliers)}

    @classmethod
    def generate_full_analytics(cls, raw_complaints: List[Any]) -> Dict[str, Any]:
        if not raw_complaints:
            return {"total_complaints": 0, "narrative_summary": "No complaint data currently available."}
        categories, priorities, statuses, departments, locations, res_hours_list = [], [], [], [], [], []
        for c in raw_complaints:
            categories.append(c.category or "Unassigned")
            priorities.append(c.priority or "Medium")
            statuses.append(c.status or "Open")
            departments.append(c.assigned_department or "General Administration")
            locations.append(c.location or "Unknown Location")
            if c.status == "Resolved" and c.created_at:
                end = c.resolved_at or c.updated_at
                if end:
                    res_hours_list.append((end - c.created_at).total_seconds() / 3600.0)
        total_count = len(raw_complaints)
        cat_counts = dict(Counter(categories).most_common())
        cat_pcts = {k: round((v / total_count) * 100, 1) for k, v in cat_counts.items()}
        prio_counts = dict(Counter(priorities).most_common())
        prio_pcts = {k: round((v / total_count) * 100, 1) for k, v in prio_counts.items()}
        status_counts = dict(Counter(statuses).most_common())
        desc_stats = cls.calculate_descriptive_stats(res_hours_list)
        iqr_stats = cls.calculate_iqr_fences(res_hours_list)
        top_cat = max(cat_counts, key=cat_counts.get) if cat_counts else "None"
        critical_count = prio_counts.get("Critical", 0)
        high_count = prio_counts.get("High", 0)
        open_count = status_counts.get("Open", 0) + status_counts.get("In Progress", 0)
        insights = [
            f"The platform has logged {total_count} total civic complaints.",
            f"Most prevalent issue: '{top_cat}' accounts for {cat_pcts.get(top_cat, 0)}% of all reported problems.",
            f"Urgency: {critical_count + high_count} complaints ({round(((critical_count + high_count)/total_count)*100,1)}%) are High or Critical.",
            f"Backlog: {open_count} complaints ({round((open_count/total_count)*100,1)}%) are awaiting resolution.",
        ]
        if res_hours_list:
            insights.append(f"Mean resolution: {desc_stats['mean']} hrs (Median: {desc_stats['median']} hrs, StdDev: {desc_stats['std_dev']} hrs).")
            if iqr_stats["outliers_count"] > 0:
                insights.append(f"Outlier Alert: {iqr_stats['outliers_count']} complaints exceeded {iqr_stats['upper_fence']} hrs — possible bottleneck.")
        return {
            "total_complaints": total_count,
            "category_distribution": cat_counts, "category_percentages": cat_pcts,
            "priority_distribution": prio_counts, "priority_percentages": prio_pcts,
            "department_distribution": dict(Counter(departments).most_common()),
            "status_distribution": status_counts,
            "top_locations": dict(Counter(locations).most_common(5)),
            "resolution_time_stats": desc_stats, "resolution_iqr_analysis": iqr_stats,
            "narrative_insights": insights,
        }

statistics_engine = StatisticsEngine()
