import math
from typing import List, Dict, Any
import pandas as pd
import numpy as np

class StatisticsEngine:
    """
    OOP Statistics Engine implementing descriptive analytics, frequency distributions,
    quartile boxplot metrics (IQR, fences), and narrative insights for civic complaints.
    """
    
    @staticmethod
    def calculate_descriptive_stats(numbers: List[float]) -> Dict[str, Any]:
        """
        Calculates Mean, Median, Mode, Min, Max, Range, Variance, Standard Deviation.
        """
        if not numbers:
            return {
                "count": 0,
                "mean": 0.0,
                "median": 0.0,
                "mode": 0.0,
                "min": 0.0,
                "max": 0.0,
                "range": 0.0,
                "variance": 0.0,
                "std_dev": 0.0
            }
            
        s = pd.Series(numbers)
        mean_val = float(s.mean())
        median_val = float(s.median())
        mode_res = s.mode()
        mode_val = float(mode_res.iloc[0]) if not mode_res.empty else mean_val
        min_val = float(s.min())
        max_val = float(s.max())
        range_val = max_val - min_val
        variance_val = float(s.var(ddof=1)) if len(s) > 1 else 0.0
        std_dev_val = float(s.std(ddof=1)) if len(s) > 1 else 0.0

        return {
            "count": len(s),
            "mean": round(mean_val, 2),
            "median": round(median_val, 2),
            "mode": round(mode_val, 2),
            "min": round(min_val, 2),
            "max": round(max_val, 2),
            "range": round(range_val, 2),
            "variance": round(variance_val, 2),
            "std_dev": round(std_dev_val, 2)
        }

    @staticmethod
    def calculate_iqr_fences(numbers: List[float]) -> Dict[str, Any]:
        """
        Calculates Quartiles (Q1, Q2, Q3), IQR, Lower Fence, Upper Fence, and Outliers.
        """
        if not numbers or len(numbers) < 2:
            return {
                "q1": 0.0,
                "q2": 0.0,
                "q3": 0.0,
                "iqr": 0.0,
                "lower_fence": 0.0,
                "upper_fence": 0.0,
                "outliers_count": 0
            }

        s = pd.Series(numbers)
        q1 = float(s.quantile(0.25))
        q2 = float(s.quantile(0.50))
        q3 = float(s.quantile(0.75))
        iqr = q3 - q1
        lower_fence = max(0.0, q1 - 1.5 * iqr)
        upper_fence = q3 + 1.5 * iqr
        
        outliers = s[(s < lower_fence) | (s > upper_fence)]

        return {
            "q1": round(q1, 2),
            "q2": round(q2, 2),
            "q3": round(q3, 2),
            "iqr": round(iqr, 2),
            "lower_fence": round(lower_fence, 2),
            "upper_fence": round(upper_fence, 2),
            "outliers_count": len(outliers)
        }

    @classmethod
    def generate_full_analytics(cls, raw_complaints: List[Any]) -> Dict[str, Any]:
        """
        Generates full analytical report including frequency distributions,
        resolution time statistics, IQR fences, and narrative civic insights.
        """
        if not raw_complaints:
            return {
                "total_complaints": 0,
                "narrative_summary": "No complaint data currently available for statistical analysis."
            }

        data = []
        for c in raw_complaints:
            res_hours = None
            if c.status == "Resolved" and c.resolved_at and c.created_at:
                res_hours = (c.resolved_at - c.created_at).total_seconds() / 3600.0
            elif c.status == "Resolved" and c.updated_at and c.created_at:
                res_hours = (c.updated_at - c.created_at).total_seconds() / 3600.0
                
            data.append({
                "id": c.complaint_id,
                "category": c.category or "Unassigned",
                "priority": c.priority or "Medium",
                "status": c.status or "Open",
                "department": c.assigned_department or "General Administration",
                "location": c.location or "Unknown Location",
                "resolution_hours": res_hours
            })

        df = pd.DataFrame(data)
        total_count = len(df)

        # Frequency distributions
        cat_counts = df['category'].value_counts().to_dict()
        cat_pcts = {k: round((v / total_count) * 100, 1) for k, v in cat_counts.items()}
        
        prio_counts = df['priority'].value_counts().to_dict()
        prio_pcts = {k: round((v / total_count) * 100, 1) for k, v in prio_counts.items()}
        
        dept_counts = df['department'].value_counts().to_dict()
        status_counts = df['status'].value_counts().to_dict()
        loc_counts = df['location'].value_counts().head(5).to_dict()

        # Resolution statistics & IQR
        res_list = df['resolution_hours'].dropna().tolist()
        desc_stats = cls.calculate_descriptive_stats(res_list)
        iqr_stats = cls.calculate_iqr_fences(res_list)

        # Narrative Explanation Generation (Requirement for Benchmark 2)
        top_cat = max(cat_counts, key=cat_counts.get) if cat_counts else "None"
        critical_count = prio_counts.get("Critical", 0)
        high_count = prio_counts.get("High", 0)
        open_count = status_counts.get("Open", 0) + status_counts.get("In Progress", 0)
        
        insights = [
            f"The platform has logged {total_count} total civic complaints.",
            f"Most prevalent issue: '{top_cat}' accounts for {cat_pcts.get(top_cat, 0)}% of all reported problems.",
            f"Urgency assessment: {critical_count + high_count} complaints ({round(((critical_count + high_count)/total_count)*100, 1)}%) are rated High or Critical priority.",
            f"Backlog status: {open_count} complaints ({round((open_count/total_count)*100, 1)}%) are currently awaiting resolution."
        ]

        if res_list:
            insights.append(
                f"Resolution Performance: Mean resolution time is {desc_stats['mean']} hours (Median: {desc_stats['median']} hrs, Standard Deviation: {desc_stats['std_dev']} hrs)."
            )
            if iqr_stats['outliers_count'] > 0:
                insights.append(
                    f"Outlier Alert: {iqr_stats['outliers_count']} complaints exceeded the upper IQR threshold ({iqr_stats['upper_fence']} hrs), signaling process bottlenecks."
                )

        return {
            "total_complaints": total_count,
            "category_distribution": cat_counts,
            "category_percentages": cat_pcts,
            "priority_distribution": prio_counts,
            "priority_percentages": prio_pcts,
            "department_distribution": dept_counts,
            "status_distribution": status_counts,
            "top_locations": loc_counts,
            "resolution_time_stats": desc_stats,
            "resolution_iqr_analysis": iqr_stats,
            "narrative_insights": insights
        }

statistics_engine = StatisticsEngine()
